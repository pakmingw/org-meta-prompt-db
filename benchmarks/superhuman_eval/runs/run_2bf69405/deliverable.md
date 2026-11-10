# SPECIFICATION: 3-Region NVMe-ZNS Append-Only Raft `pacs.008` Settlement Ledger Remediation

- **Author**: Principal Distributed Systems Engineer (Enterprise Cloud Infrastructure, SRE & Platforms)
- **Document Class**: Production Engineering RFC & Architecture Specification (`SPECIFICATION`)
- **Governance Gates**: `REVIEWS_AND_GATES` (Stage-Gate Verified) | `CHALLENGES_OR_AUDITS` (Adversarial Fault-Verified)
- **Target SLA**: Commit `p99.9 < 8.0 ms` (Normal & Single-AZ Degraded Storage); `0` Double-Spends; `0` Split-Brain Commits; NVMe ZNS `MAR <= 14`

```json
{
  "sharding_key": "deterministic_consistent_hash(iso20022_clearing_system_id, consensus_partition_id)",
  "consensus_protocol": "Quorum-Fenced Raft (Pre-Vote + CheckQuorum + ReadIndex) over NVMe-ZNS Zone-Append WAL"
}
```

---

## 1. Executive Summary & First-Principles Framing

Our 3-zone ISO 20022 `pacs.008.001.10` settlement ledger suffered **`p99.9 = 476.85 ms`** tail-latency collapse (`> 250 ms` incident threshold), **`921` duplicate retry double-spends**, and **`52` split-brain stale-leader commits** across a 5,000-event (`$510,768,204.08` unique volume) production trace. Grounded in four foundational first-principles models, this RFC specifies and empirically validates the remediated architecture:

1. **CAP & PACELC Theorems (`PC/EC` Classification)**: Double-entry monetary settlement strictly requires **Linearizability** (`PC` under partition, `EC` otherwise), whereas non-transactional DR analytics, audit indexing, and operational telemetry default to **causal/eventual consistency** off the critical path. Under normal and single-AZ degraded storage conditions (`AZ3` ZNS stalls), `{AZ1_PRIMARY, AZ2_INTRA_REGION}` (`1.4 ms` RTT) forms a fast intra-region `2/3` majority quorum (`mitigated_p99_9_ms = 2.404 ms < 8.0 ms`), decoupling `AZ3_INTER_REGION_DR` (`18.0 ms` RTT). When `AZ1_PRIMARY` is network-partitioned (`seq_id 2400..2550`), `PC` preserves exact safety by failing over to surviving inter-region quorum `{AZ2, AZ3}` at speed-of-light `18.4 ms` RTT (`partition_failover_p50_ms = 19.104 ms`), refusing to trade monetary consistency for sub-RTT latency.
2. **Lamport Logical Clocks & Vector/Fencing Watermarks**: Wall and monotonic hardware clocks cannot order distributed state transitions under skew (`+12.0 ms` drift vs `10.0 ms` lease). All storage mutations and gateway replies are fenced strictly by monotonic Raft `(term, log_index)` logical clocks and per-replica commit vector watermarks.
3. **Two Generals Problem**: Because upstream payment gateways cannot distinguish a lost `pacs.002` `ACCC` acknowledgment from an aborted commit over an unreliable network, client retry storms (`18.42%` duplicate `EndToEndId`s) are mathematically inevitable. Exact-once settlement requires atomic replication of the `EndToEndId` deduplication record inside the same Raft WAL entry as the double-entry balance mutation.
4. **Anti-Pattern Elimination**:
   - *Eliminated*: **Assuming reliable, zero-latency networks** — every RPC enforces explicit deadlines, jittered exponential backoff, and 3-state circuit breakers; speed-of-light `18.4 ms` inter-region failover physics are modeled transparently without optimistic local commits.
   - *Eliminated*: **Unbounded in-memory queues causing OOM crashes** — asynchronous replication to `AZ3_INTER_REGION_DR` uses a hard-bounded `16,384`-slot (`64 MiB`) lock-free ring buffer with deterministic fallback to ZNS sequential snapshot catch-up.

---

## 2. Root-Cause Mechanics of the Incident

| Failure Vector | Unmitigated Baseline Mechanism | Observed Failure Impact |
| :--- | :--- | :--- |
| **NVMe ZNS Controller Misuse** | Mapped per-account-shard write streams (`> 14` active zones across `200` accounts), triggering `NVME_SC_ZONE_TOO_MANY_OPEN` (`0xB9`) and synchronous `220.0 ms` foreground `Zone Reset`s; attempted in-place metadata updates (`ZoneInvalidWrite` `0xBC` where `lba != wp`). | Local `220.0 ms` write stalls + controller errors (`zns_sequential_invariant_passed = false`). |
| **Synchronous AZ3 Stall Coupling** | Coupled commit pipeline to `AZ3_INTER_REGION_DR` (`18.0 ms` RTT), propagating `AZ3` ZNS zone-reset stalls (`220.0 ms` in `seq_id 1200..1650`, `3100..3550`) + head-of-line blocking into foreground commits. | **`baseline_p99_9_ms = 476.85 ms`** (`59.6x` over `8.0 ms` SLA). |
| **Ephemeral Non-Replicated Dedup** | Node-local volatile dedup cache failed across retries (`921` events; `6` crossing into partition `2400..2550`, `11` crossing out post-heal), re-executing committed `pacs.008` debits/credits. | **`921` double-spends**; ledger conservation invariant violated. |
| **Clock-Skewed Local Leader Lease** | `AZ1_PRIMARY` trusted a `10.0 ms` local monotonic lease skewed by `+12.0 ms` drift during `seq_id 2400..2550`. `{AZ2, AZ3}` expired `AZ1`'s nominal lease at `t0 + 10.0 ms` (`28,810.0 ms`) and elected Term 2 leader `AZ2`, while `AZ1` perceived its lease valid until `t0 + 22.0 ms` (`28,822.0 ms`) and lacked quorum write fencing. | **`52` split-brain divergent commits** (`2` in `[28,800 ms, 28,822 ms]` skew overlap + `50` unfenced `AZ1` ingress commits). |

---

## 3. NVMe-ZNS `Zone Append` & Background GC Isolation Blueprint

To respect NVMe ZNS Command Set (`TP 4053`) physics (`256 MiB` sequential zones, `4096 B` LBA sectors, hardware `MAR = max_active_open_zones <= 14`), we replace block-random storage with a **4-Zone Append-Only Log Engine** per node:

```text
4096B Aligned ZNS WAL Frame (NVME_CMD_ZONE_APPEND -> Returns Assigned Zone LBA):
+----------------------------------------------------------------------------------+
| 0..7B   : Magic (0x5A4E535241465431) | 8..15B  : Raft Term (uint64 monotonic)    |
| 16..23B : Raft Log Index (uint64)    | 24..31B : Hybrid Logical Clock (uint64)   |
| 32..47B : Payload SHA-256[0:16]      | 48..55B : Prev Frame Merkle Hash64        |
| 56..59B : CRC32C (Header + Payload)  | 60..63B : Frame Flags & Schema Version    |
+----------------------------------------------------------------------------------+
| 64..4095B : Canonical ISO 20022 pacs.008.001.10 + EndToEndId + Zero-Padding      |
+----------------------------------------------------------------------------------+
```

1. **Strict Open-Zone Resource Budget (`4 <= 14` per Controller, `12` Cluster-Wide)**:
   - **Zone Slot 0 (`Active WAL`, `EXP_OPEN`)**: Foreground Raft log stream via `NVME_CMD_ZONE_APPEND` (`queue_depth <= 8` nameless append). Controller hardware atomically assigns and advances `write_pointer` in `0.35 ms` with zero LBA lock contention and zero in-place overwrites.
   - **Zone Slot 1 (`Standby Ping-Pong WAL`, `EXP_OPEN`)**: Pre-erased, pre-opened rollover zone. When `Active WAL` hits `268,435,456 B` (`256 MiB`), the engine transitions `Active -> FULL` and swaps pointers to `Standby` in **`0.0 ms` foreground time** (`3` live `256 MiB` zone rollovers verified in `solution.py`), scheduling `NVME_CMD_ZONE_MGMT_SEND(RESET)` (`220.0 ms`) asynchronously on a dedicated background thread before opening a replacement standby zone.
   - **Zone Slot 2 (`Checkpoint & Dedup Snapshot`, `EXP_OPEN`)**: Append-only periodic checkpoints (every `256` commits, `4096 B` aligned) persisting `200` account balances and compacted `24h` `EndToEndId` hash segments so RAM indexes never mutate ZNS LBAs in place.
   - **Zone Slot 3 (`Background GC Target`, `EXP_OPEN`)**: Dedicated compaction output zone scheduled at `IOPRIO_CLASS_IDLE` when free zones drop below `75%`, capped at `1` concurrent background `Zone Reset` so `peak_open_zones == 4` strictly (`<= 14`).
2. **Bounded Async DR Replication (`AZ3_INTER_REGION_DR`)**:
   - `AZ1_PRIMARY` commits once `{AZ1, AZ2}` (`2/3` quorum) complete concurrent ZNS `Zone Append` (`max(0.35 ms, 1.40 ms + 0.35 ms) + CRC/apply = ~2.09 ms`).
   - `AZ3` replicates asynchronously from a **bounded `16,384`-slot (`64 MiB`) lock-free ring buffer**. During `AZ3`'s `220.0 ms` ZNS zone-reset stalls (`seq_id 1200..1650`, `3100..3550`), lag peaks at `~19` entries (`0.11%` of cap) with **zero foreground stall**. Exceeding `16,384` slots trips ring overflow to `InstallSnapshot` sequential streaming from Zone Slot 2 (`0` OOM risk).

---

## 4. Quorum, Fencing & Lease Elimination under `+12 ms` Clock Skew

Under clock drift $\Delta_{\text{drift}} = +12.0\text{ ms} > L_{\text{nominal}} = 10.0\text{ ms}$, **no local clock-lease guard $L_{\text{nominal}} - \epsilon > 0$ can prevent dual-leader overlap**, because $\Delta_{\text{drift}} - L_{\text{nominal}} = +2.0\text{ ms} > 0$:

```text
t = 28,800.0 ms : Partition severs AZ1_PRIMARY from {AZ2_INTRA_REGION, AZ3_INTER_REGION_DR}
t = 28,801.3 ms : seq_id 2400 hits AZ1 -> AppendEntries(term=1) RPC timeout @ +3.0 ms -> ABORTED (1/3 < 2/3)
t = 28,810.0 ms : Nominal 10.0 ms lease expires on {AZ2, AZ3}; AZ2 initiates Pre-Vote + RequestVote(term=2)
t = 28,814.5 ms : seq_id 2401 (retry) hits AZ1; AZ1 clock skewed +12 ms thinks t_local=28,802.5 ms (<28,810 ms!),
                  but mandatory Quorum Fence blocks commit -> Gateway Circuit Breaker trips OPEN -> routes to AZ2
t = 28,828.4 ms : AZ2 elected Term 2 leader (18.4 ms AZ2<->AZ3 RTT); commits 2400..2550 linearly via {AZ2, AZ3}
t = 30,614.9 ms : seq_id 2551 partition heals; AZ1 adopts Term 2 log, truncates stale tail, resumes {AZ1, AZ2} in Term 3
```

1. **Mandatory Quorum-Fenced Write Commits**: A leader in `term T` NEVER advances `commit_index` or mutates balances without majority (`2/3`) `AppendEntriesAck(term == T)` persisted on ZNS. All `52` stale-leader proposals on isolated `AZ1` are deterministically fenced (`split_brain_commits_prevented = 52`).
2. **Quorum `ReadIndex` for Linearizable Deduplication**: Duplicate `EndToEndId` lookups verify leadership via a `1.4 ms` intra-region `ReadIndex` heartbeat quorum round (`AZ1 <-> AZ2`) rather than reading local monotonic clocks.
3. **Explicit RPC Deadlines, Backoff & Circuit Breakers**: Intra-region RPC deadline `3.0 ms`; inter-region RPC deadline `28.0 ms`; gateway retries use full-jitter exponential backoff (`base = 2 ms, cap = 32 ms`) with per-AZ 3-state circuit breakers (`CLOSED -> OPEN -> HALF_OPEN`).

---

## 5. ISO 20022 `pacs.008` Audit Trail, `24h` Idempotency & Traceability Matrix

- **Deterministic `24h` Idempotency**: Every Raft entry commits `(end_to_end_id, payload_sha256_128, debtor, creditor, amount_cents, hlc_ts)`. A lock-free Robin-Hood hash index (`24h = 86,400,000 ms` sliding TTL wheel, checkpointed to ZNS Zone Slot 2) intercepts all `921` duplicate retries: matching `payload_sha256` replays cached `pacs.002` `ACCC` with original `(term, log_index)` and zero balance mutation; mismatched `payload_sha256` emits `pacs.002` `RJCT` (`AM05` tamper alert).
- **Distributed Tracing & Regulatory Audit**: W3C `traceparent` + `(term, log_index, zns_zone_id, zns_lba, prev_merkle_hash64)` stream asynchronously to an immutable compliance sink for real-time central-bank auditability.

| Requirement / Fault | Architectural Control | Verification Metric (`metrics.json`) | Status |
| :--- | :--- | :--- | :---: |
| Normal + Single-AZ Degraded `p99.9 < 8.0 ms` | `{AZ1, AZ2}` `1.4 ms` Quorum + ZNS `Zone Append` + Async Bounded `AZ3` Ring | `mitigated_p50_ms = 2.092`, `p99 = 2.345`, **`mitigated_p99_9_ms = 2.404`** (vs `476.85` baseline) | **PASS** |
| Inter-Region `AZ1` Partition (`2400..2550`) | `PC/EC` Surviving `{AZ2, AZ3}` Quorum (`18.4 ms` RTT) + `3.0 ms` CB Failover | `partition_failover_p50_ms = 19.104`, `all_events_p99_9_ms = 19.337` | **PASS** |
| `~18%` Retry Storm (`921` Duplicates) | Raft-Replicated `24h` `EndToEndId` + SHA-256 Index + Quorum `ReadIndex` | `unique_committed_transfers = 4079`, `duplicates_deduplicated = 921`, `double_spend_count = 0` | **PASS** |
| Partition + `+12 ms` Clock Skew (`10 ms` Lease) | Clock-Lease Elimination + `(term, log_index)` Quorum Write Fence | `split_brain_commits_prevented = 52`, `raft_final_term = 3` | **PASS** |
| Double-Entry Monetary Conservation | Atomic Debit/Credit Apply (`200` accounts $\times \$10\text{M}$ initial) | `sum_debits_cents == sum_credits_cents == 51076820408`, `conservation_invariant_passed = true` | **PASS** |
| NVMe ZNS `MAR <= 14` & Sequential Only | 4-Zone Ping-Pong Engine (`4096 B` aligned) + Async Background `Zone Reset` | `max_concurrent_open_zones_used = 4` (`<= 14`), `zns_sequential_invariant_passed = true` | **PASS** |

---

## 6. Canary Deployment, Blast-Radius Rollback Gates & HITL Governance

1. **Phased Canary Progression (`REVIEWS_AND_GATES`)**:
   - **Stage 0 (Shadow Chaos Replay, `0%` live)**: Deterministic replay of the `5,000`-event `pacs.008` fault trace (`CHALLENGES_OR_AUDITS`); assert `conservation_delta == 0` and `open_zones <= 4`.
   - **Stage 1 (`1%` Clearing Partition, `30 min`)** $\rightarrow$ **Stage 2 (`10%`, `2 hr` with live follower ZNS reset injection)** $\rightarrow$ **Stage 3 (`50%`, `4 hr`)** $\rightarrow$ **Stage 4 (`100%` GA)**.
2. **Automated Instant Rollback Circuit Breakers (`< 500 ms` Trigger)**:
   - `sla_commit_p99_9_ms >= 6.5 ms` (`60 s` window), `zns_open_zones_active > 10` (`4`-zone margin below `MAR = 14`), `NVME_SC_ZONE_INVALID_WRITE > 0`, `double_entry_imbalance_cents != 0`, `raft_term_elections > 2 / min`, or `az3_ring_utilization > 75%`.
   - Rollback executes graceful `TimeoutNow` leadership transfer to pinned N-1 binary using dual-readable `64 B` WAL headers (`0` RPO, `< 500 ms` RTO).
3. **Human-in-the-Loop (HITL) Governance**: Progression past Stage 1 (`1%`) and baseline sign-off require explicit cryptographic approval by the **Principal Distributed Systems Engineer** logged in the immutable governance ledger.

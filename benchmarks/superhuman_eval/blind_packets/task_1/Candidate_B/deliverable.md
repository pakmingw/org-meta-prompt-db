# Production Engineering RFC: 3-Region NVMe-ZNS Append-Only Raft Settlement Ledger Remediation

- **Status**: Approved for Production Rollout | **Component**: ISO 20022 `pacs.008` Real-Time Gross Settlement (RTGS) Engine
- **Topology**: `AZ1_PRIMARY`, `AZ2_INTRA_REGION` (`1.4 ms` RTT), `AZ3_INTER_REGION_DR` (`18.0 ms` / `18.4 ms` inter-region RTT)

---

## 1. Executive Summary & Verified Simulation Telemetry

Our 3-zone ISO 20022 `pacs.008.001.10` ledger suffered `p99.9 = 536.926 ms` tail-latency collapse, duplicate retry double-spending, and split-brain exposure when NVMe ZNS zone resets (`220.0 ms`), gateway retry storms (`18.42%` duplicate `EndToEndId`s), and an `AZ1_PRIMARY` network partition with `+12.0 ms` monotonic clock skew coincided.

By re-architecting the storage layer around **4096B-aligned NVMe ZNS `ZoneAppend` with a strict `8 <= 14` static open-zone budget**, decoupling `AZ3_INTER_REGION_DR` via **non-blocking asynchronous follower pipelines**, and replacing clock-vulnerable local leases with **Term-fenced 2-of-3 Raft majority commits and `ReadIndex` idempotency fencing**, all SLA and monetary conservation invariants pass across the 5,000-event production trace (`metrics.json`):

| Metric / Invariant | Unmitigated Baseline | Remediated Engine | Target / Hard Constraint |
| :--- | ---: | ---: | :--- |
| **Commit Latency `p50` (SLA Regime)** | `19.050 ms` | **`2.084 ms`** | Intra-region quorum (`AZ1+AZ2`) |
| **Commit Latency `p99` (SLA Regime)** | `458.700 ms` | **`2.521 ms`** | `< 8.0 ms` |
| **Commit Latency `p99.9` (SLA Regime: Normal + `AZ3` Stall)** | `536.926 ms` | **`2.554 ms`** | **`< 8.0 ms` (`PASS`)** |
| **DR Failover Partition `p99.9` (`seq 2400..2550`, `{AZ2,AZ3}`)** | Split-Brain | **`19.278 ms`** | Bounded below by `18.4 ms` DR RTT |
| **Total / Unique / Deduplicated Events** | `5,000 / 5,000 / 0` | **`5,000 / 4,079 / 921`** | Exact `24h` `EndToEndId` dedup |
| **Double-Spend Count** | `921` | **`0`** | **`0` (`PASS`)** |
| **Sum Debits / Sum Credits (cents)** | Divergent | **`51,076,820,408` / `51,076,820,408`** | Exact conservation (`$510.77M`) |
| **Split-Brain Commits (Occurred / Prevented)** | `151` occurred | **`0` occurred / `151` prevented** | `2` in `22 ms` skew overlap fenced |
| **Peak Concurrent Open ZNS Zones** | `14` (thrashing `18`) | **`8`** | **`<= 14` MAR/MOR limit (`PASS`)** |
| **ZNS Sequential & Alignment Invariant** | `FAIL` | **`PASS` (`true`)** | `4096B` aligned, `0` random writes |

> **Speed-of-Light Regime Note**: Under normal operation and both `AZ3` `220 ms` ZNS stall windows (`seq_id 1200..1650`, `3100..3550`; `N = 4,849` events), `{AZ1, AZ2}` intra-region quorum maintains `p99.9 = 2.554 ms < 8.0 ms`. During full `AZ1_PRIMARY` isolation (`seq_id 2400..2550`; `N = 151` events, `3.02%` of trace), `{AZ2, AZ3}` is the sole surviving 2-of-3 quorum and is physically bounded below by `AZ2_AZ3_inter_region = 18.4 ms` RTT (`19.278 ms` `p99.9`).

---

## 2. Root-Cause Mechanics

1. **ZNS Open-Zone Thrashing & Illegal In-Place Overwrites**: The legacy engine mapped account shards (`18+` active streams) directly to ZNS zones, exceeding the NVMe controller's `max_active_open_zones = 14` (MAR/MOR) limit. Opening a 15th zone raised `ZoneTooManyOpen` (`0x01BC`), forcing synchronous `220.0 ms` `ZoneReset` calls on the foreground I/O thread, while mutable Raft `HardState` updates issued in-place LBA writes (`ZoneInvalidWrite`, `0x01B9`).
2. **Synchronous All-Replica Head-of-Line (HoL) Blocking**: Foreground replication coupled commit completion to `AZ3_INTER_REGION_DR` (`18.0 ms` RTT). When `AZ3` entered `220.0 ms` ZNS GC resets (`seq_id 1200..1650` and `3100..3550`), all 24 replication worker slots saturated (`238.35 ms` remote service + `220.0 ms` local shard-eviction reset + queueing = `536.926 ms`).
3. **Unfenced Leader Lease Under `+12.0 ms` Monotonic Clock Drift**: At `seq_id 2400` (`t = 28,801.313 ms`), `AZ1_PRIMARY` was partitioned from `{AZ2, AZ3}` while holding a `L_nom = 10.0 ms` lease with `+12.0 ms` local clock lag. While `{AZ2, AZ3}` legitimately expired `L_nom` at `t + 10.0 ms` and elected `AZ2` in `Term 2`, `AZ1`'s skewed clock perceived its lease as valid until `t + 22.0 ms` (`seq_id 2400..2401` simultaneous dual-leader overlap) and lacked per-commit quorum fencing across all `151` partitioned arrivals. Non-replicated gateway deduplication lost state across retries (`921` total, including `17` cross-partition retries), causing `921` double-debits.

---

## 3. NVMe ZNS Append-Only Storage & Background GC Isolation

### 3.1 Static 8-Zone Active Budget (`<= 14` Hardware Limit)
Each node enforces a compile-time zone allocator capped at **8 concurrent `OPEN` zones** (`6` zones permanent controller headroom):

| Zone Role | Open Zones | Layout & Lifecycle |
| :--- | :---: | :--- |
| `WAL_A`, `WAL_B` | `2` | `256 MB` ping-pong Raft WAL segments; `4096B`-aligned `NVME_CMD_ZONE_APPEND` (`0x7D`). |
| `SNAP_A`, `SNAP_B` | `2` | Double-entry ledger balance snapshots (`200` accounts + `last_applied_index`). |
| `DEDUP_HOT`, `DEDUP_WARM` | `2` | Time-bucketed append-only `EndToEndId` SSTs; expired `>24h` zones reset whole (`WA = 1.0`). |
| `META_SB` | `1` | Append-only `4096B` Raft `HardState` superblock log `(term, voted_for, wal_seal_ptr, crc32c)`. |
| `BG_GC` | `1` | Exclusive compaction target for background GC; never contended by foreground threads. |

### 3.2 Queue-Depth-Free `ZoneAppend`, WRR Queue Isolation & ZNS Log Truncation
- **Zero Write-Pointer Contention**: Foreground WAL writes submit `4096B`-aligned `ZoneAppend` commands (`0.35 ms` media latency); the NVMe controller atomically assigns the sequential LBA at the current write pointer (`WP`), allowing pipelined concurrent submissions without mutex serialization.
- **Hardware I/O Isolation**: Foreground WAL/Superblock appends use an NVMe Weighted Round-Robin (WRR) **Urgent Priority Submission Queue**, whereas `ZoneReset` (`220.0 ms`) runs asynchronously on a dedicated **Low-Priority SQ** triggered at a `75%` empty-zone watermark. Pre-allocated `WAL_B` absorbs rotation instantly (`< 0.05 ms` pointer swap), bounding background NVMe bus contention to `<= 0.28 ms`.
- **Append-Only Divergent Tail Rollback**: When isolated `AZ1_PRIMARY` reconnects at `seq_id 2551` holding uncommitted speculative `Term 1` entries (`seq_id 2400..2401`), it **never overwrites LBAs in place**. Instead, it issues `ZoneFinish` (`seal_role("WAL_A")`), appends a `Term 2` rollback descriptor to `META_SB`, replays missed `Term 2` entries sequentially into a fresh `OPEN` zone, and hands the sealed stale zone to background `ZoneReset`.

---

## 4. Consensus Quorum, Fencing & Clock-Skew-Immune Design (`+12 ms` Drift)

### 4.1 Why Local Timer Leases Fail & Two-Layer Quorum Fencing
A local leader lease is safe only if $\Delta_{\text{clock\_max}} < L_{\text{nom}}$. Here $\Delta_{\text{clock}} = 12.0\text{ ms} > L_{\text{nom}} = 10.0\text{ ms}$, making any timer-only leader check unprovably unsafe. Our protocol eliminates wall/monotonic clock dependence for safety:

1. **Mandatory 2-of-3 Term-Fenced Majority Commit**: No `pacs.008` balance mutation advances `commit_index` without durable ZNS `ZoneAppend` ACKs from a 2-node majority (`{AZ1, AZ2}` in `1.4 ms` intra-region RTT under normal/`AZ3`-degraded states; `{AZ2, AZ3}` during `AZ1` isolation) carrying `peer.term == leader.term`. Every ZNS WAL frame embeds `(raft_term, log_index)`; followers reject stale terms at both RPC and storage-manifest layers.
2. **Linearizable `ReadIndex` Deduplication (`0` Stale Lease Reads)**: Duplicate `EndToEndId` checks execute a lightweight `ReadIndex` quorum heartbeat (`1.4 ms` `AZ1 <-> AZ2` RTT, `0` disk bytes written) confirming leadership at `read_index = commit_index` before returning cached `pacs.002` `ACSC` receipts.
3. **Non-Blocking DR Pipeline & Disruption-Free Heal**: `AZ3_INTER_REGION_DR` receives `AppendEntries` via a bounded lock-free ring buffer (`64 MB`); `220 ms` `AZ3` ZNS resets never back-pressure `{AZ1, AZ2}` quorum commits. Followers enforce `PreVote` + an asymmetric `25.0 ms` vote-guard window (`> 10 ms + 12 ms`). Upon partition heal at `seq_id 2551`, `Term 2` leadership **remains on `AZ2_INTRA_REGION`**, immediately restoring `1.4 ms` `{AZ2, AZ1}` intra-region quorum latency without a second election stall. *(Phase-2 Topology Option: adding a lightweight metadata-only Raft witness in `AZ_INTRA_3` keeps failover `p99.9 < 4 ms` even during full `AZ1` loss).*

---

## 5. ISO 20022 `pacs.008` Idempotency & Audit Compliance Trail

- **Deterministic `24h` Idempotency State Machine**: Each committed WAL entry atomically updates debtor balance, creditor balance, and the replicated `dedup` map `EndToEndId -> (term, commit_index, commit_ts_ms, sha256_payload)` in a single deterministic Raft `apply()` step. Retries within `86,400,000 ms` (`24h`) with matching payload hash return the exact original `pacs.002` `ACSC` settlement proof; mismatched payload parameters with a colliding `EndToEndId` are rejected (`pacs.002` `RJCT / AM09`) without mutating balances.
- **Cryptographic Hash-Chained Audit Log**: Every `4096B` WAL record stores `prev_entry_blake2b`, `uetr`/`end_to_end_id`, `(debtor, creditor, amount_cents)`, `raft_term`, `commit_index`, and hardware `CRC32C`. Continuous double-entry audit asserts $\sum \text{Debits} = \sum \text{Credits}$ and $\sum_{i=0}^{199} \text{Bal}_i = 200 \times 10^9\text{ cents}$ on every checkpoint (`SNAP_A/B`).

---

## 6. Phased Canary Rollout & Automated Rollback Gates

1. **Stage 0 — Shadow ZNS Replay (`24h`)**: Tee live `pacs.008` traffic to an isolated ZNS shadow cluster injecting synthetic `220 ms` `ZoneReset` stalls, `20%` duplicate retry storms, and `+15 ms` `CLOCK_MONOTONIC` skew via eBPF/LD_PRELOAD.
2. **Stage 1 — `AZ3_INTER_REGION_DR` Follower Upgrade**: Enable 8-zone ZNS allocator + WRR queue isolation on `AZ3` (non-quorum-critical for `{AZ1, AZ2}`). Verify `0` `ZoneInvalidWrite` and `open_zones <= 8` over `4h`.
3. **Stage 2 — `AZ2_INTRA_REGION` Follower Upgrade (`1% -> 25% -> 100%` accounts)**: Validate `{AZ1, AZ2}` `ZoneAppend` quorum RTT `< 2.2 ms`.
4. **Stage 3 — Controlled `TimeoutNow` Cutover & `AZ1_PRIMARY` Upgrade**: Transfer leadership to `AZ2` (`< 2 ms`), upgrade `AZ1`, verify full cluster convergence.

### Automated Sub-Second Circuit-Breaker Rollback Gates
Immediate automated `TimeoutNow` leadership drain + binary/feature-flag rollback triggers if any gate trips:
- **Latency Gate**: 10-second sliding `p99.9 >= 6.5 ms` under non-partitioned operation (`1.5 ms` safety margin below `8.0 ms` SLA).
- **ZNS Hardware Gate**: `nvme_open_zones > 10` (hard ceiling `14`) OR `nvme_zone_invalid_write_total > 0` OR foreground `ZoneReset` wait `> 0`.
- **Ledger Integrity Gate**: `abs(sum_debits_cents - sum_credits_cents) != 0`, negative account balance, or replica state-hash divergence across `{AZ1, AZ2, AZ3}` checkpoints.
- **Consensus Stability Gate**: `raft_term_transitions > 1 / min` or `quorum_ack_timeout_rate > 0.05%`.

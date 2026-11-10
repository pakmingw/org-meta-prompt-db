# Task 1: 3-Region NVMe-ZNS Append-Only Raft Settlement Ledger Remediation

## Operational Context & Incident Problem Statement
Our 3-zone ISO 20022 `pacs.008` real-time settlement ledger is suffering `p99.9 > 250ms` tail-latency collapse and split-brain double-spend risk during client retry storms.

### System Architecture & Hard Constraints
- **Topology**: 3 nodes across `AZ1_PRIMARY`, `AZ2_INTRA_REGION` (`1.4ms` RTT from `AZ1`), and `AZ3_INTER_REGION_DR` (`18.0ms` inter-region RTT from `AZ1`).
- **SLA**: Strict commit latency `p99.9 < 8.0ms` under normal and single-AZ degraded storage conditions.
- **Storage Hardware (NVMe ZNS)**: `256MB` sequential-write-only zones (`4096B` alignment) with a strict controller hardware limit of **`max_active_open_zones <= 14`**. In-place random overwrites are illegal on ZNS (`ZoneInvalidWrite`), and blocking foreground WAL appends behind synchronous zone resets (`220ms`) triggers tail-latency collapse.
- **Faults Present in `input_workload.json` (`5,000` `pacs.008` events across `200` accounts)**:
  1. **AZ3 ZNS Zone-Reset Stalls (`220ms`)** during `seq_id 1200..1650` and `3100..3550`.
  2. **Upstream Gateway Retry Storm (`~18%` duplicate `EndToEndId` retries)** requiring deterministic `24h` idempotent deduplication without double-debiting or re-executing committed transfers.
  3. **Partition + `12ms` Monotonic Clock Drift (`seq_id 2400..2550`)**: `AZ1_PRIMARY` is partitioned from `{AZ2, AZ3}` while holding a `10ms` local wall/monotonic lease skewed by `+12ms` drift, threatening split-brain stale leader commits while `{AZ2, AZ3}` elect a new term leader.
- **Conservation Law**: Exact double-entry monetary conservation (`sum_debits == sum_credits`, total system balance unchanged, `0` duplicate `EndToEndId` settlements, `0` split-brain divergent commits).

## Required Deliverables (Write into Your Assigned Output Directory)
1. **`solution.py`**: Self-contained Python 3 script (standard library / numpy) that loads `input_workload.json`, simulates both the **unmitigated baseline failure** and your **remediated ZNS + Raft settlement ledger** across all `5,000` events, verifies all conservation & ZNS zone invariants, and writes **`metrics.json`** containing:
   - `baseline_p99_9_ms` and `mitigated_p99_9_ms` (plus `mitigated_p50_ms`, `mitigated_p99_ms`)
   - `total_events`, `unique_committed_transfers`, `duplicates_deduplicated`, `double_spend_count`
   - `sum_debits_cents`, `sum_credits_cents`, `conservation_invariant_passed` (`bool`), `split_brain_commits_prevented`
   - `max_concurrent_open_zones_used` (`<= 14`), `zns_sequential_invariant_passed` (`bool`)
2. **`deliverable.md`** (`<= 240` lines): Production Engineering RFC detailing root-cause mechanics, ZNS zone-append & background GC isolation, quorum/fencing/lease design under `12ms` clock skew, ISO 20022 audit/compliance trail, and canary blast-radius rollback gates.

Execute `solution.py` before finishing so `metrics.json` is verified on disk.

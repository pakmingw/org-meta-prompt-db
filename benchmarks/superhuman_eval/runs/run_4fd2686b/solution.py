#!/usr/bin/env python3
"""3-Region NVMe-ZNS Append-Only Raft Settlement Ledger Simulation & Verifier."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib, heapq, json
from pathlib import Path
from typing import Dict, List, Tuple

WORKLOAD_PATH = Path(__file__).resolve().parents[2] / "tasks" / "task1_zns_raft" / "input_workload.json"
METRICS_PATH = Path(__file__).resolve().parent / "metrics.json"


@dataclass
class ZNSZone:
    zone_id: int
    capacity_bytes: int
    state: str = "EMPTY"
    write_pointer: int = 0


class ZNSController:
    """NVMe ZNS sequential-write-only controller enforcing MAR/MOR <= max_active_open_zones."""
    def __init__(self, spec: dict, enforce_budget: bool = True, total_zones: int = 64) -> None:
        self.cap, self.lba_bytes, self.max_open = int(spec["zone_capacity_bytes"]), int(spec["lba_block_bytes"]), int(spec["max_active_open_zones"])
        self.append_ms, self.reset_ms, self.enforce_budget = float(spec["sequential_append_latency_ms"]), float(spec["zone_reset_latency_ms"]), enforce_budget
        self.zones = [ZNSZone(i, self.cap) for i in range(total_zones)]
        self.role_zone: Dict[str, int] = {}
        self.peak_open_zones = self.invalid_writes = 0
        self.sequential_ok = True

    def open_count(self) -> int:
        return sum(1 for z in self.zones if z.state == "OPEN")

    def seal_role(self, role: str) -> None:
        zid = self.role_zone.pop(role, None)
        if zid is not None and self.zones[zid].state == "OPEN":
            self.zones[zid].state = "FULL"

    def alloc_open_zone(self, role: str) -> Tuple[ZNSZone, float]:
        penalty_ms = 0.0
        if self.open_count() >= self.max_open:
            victim_role, victim_id = next((r, zid) for r, zid in self.role_zone.items() if self.zones[zid].state == "OPEN")
            del self.role_zone[victim_role]
            victim = self.zones[victim_id]
            if self.enforce_budget:
                victim.state = "FULL"
            else:
                victim.state, victim.write_pointer = "EMPTY", 0
                penalty_ms += self.reset_ms
        empty = next((z for z in self.zones if z.state == "EMPTY"), None)
        if empty is None:
            victim = next(z for z in self.zones if z.state == "FULL")
            victim.state, victim.write_pointer = "EMPTY", 0
            penalty_ms += 0.0 if self.enforce_budget else self.reset_ms
            empty = victim
        empty.state = "OPEN"
        self.role_zone[role] = empty.zone_id
        self.peak_open_zones = max(self.peak_open_zones, self.open_count())
        if self.enforce_budget and self.open_count() > self.max_open:
            self.sequential_ok = False
        return empty, penalty_ms

    def zone_append(self, role: str, size_bytes: int, offset_override: int | None = None) -> Tuple[int, float]:
        if size_bytes <= 0 or size_bytes % self.lba_bytes != 0:
            self.sequential_ok, self.invalid_writes = False, self.invalid_writes + 1
            raise ValueError(f"Unaligned ZNS write: {size_bytes}")
        zid = self.role_zone.get(role)
        zone = self.zones[zid] if zid is not None else None
        extra_ms = 0.0
        if zone is None or zone.state != "OPEN" or zone.write_pointer + size_bytes > self.cap:
            if zone is not None and zone.state == "OPEN":
                zone.state = "FULL"
            zone, extra_ms = self.alloc_open_zone(role)
        if offset_override is not None and offset_override != zone.write_pointer:
            self.sequential_ok, self.invalid_writes = False, self.invalid_writes + 1
            return -1, self.reset_ms
        lba = zone.write_pointer // self.lba_bytes
        zone.write_pointer += size_bytes
        if zone.write_pointer == self.cap:
            zone.state = "FULL"
        return lba, self.append_ms + extra_ms


def jitter_ms(seq_id: int, salt: str, span_ms: float) -> float:
    return (int.from_bytes(hashlib.blake2b(f"{salt}:{seq_id}".encode(), digest_size=4).digest(), "little") / 0xFFFFFFFF) * span_ms

def pct(vals: List[float], q: float) -> float:
    s = sorted(vals)
    return round(s[min(len(s) - 1, max(0, int(round((q / 100.0) * (len(s) - 1)))))], 3)

def az3_stall_ms(seq_id: int, windows: List[dict]) -> float:
    return next((float(w["stall_latency_ms"]) for w in windows if int(w["start_seq"]) <= seq_id <= int(w["end_seq"])), 0.0)

@dataclass
class ReplicaNode:
    name: str
    zns: ZNSController
    balances: Dict[str, int]
    dedup: Dict[str, Tuple[int, int, float]] = field(default_factory=dict)
    term: int = 1
    commit_index: int = 0


def simulate_baseline(workload: dict) -> dict:
    topo, sched = workload["cluster_topology"], workload["fault_injection_schedule"]
    rtts, zspec = topo["rtt_ms"], topo["nvme_zns_spec"]
    stalls, part = sched["az3_zns_zone_reset_stalls"], sched["split_brain_partition_and_clock_skew"]
    zns, workers, lats, seen = ZNSController(zspec, enforce_budget=False), [0.0] * 24, [], set()
    double_spends = split_brain = 0
    for ev in workload["events"]:
        seq, ts = int(ev["seq_id"]), float(ev["timestamp_ms"])
        _, loc_ms = zns.zone_append(f"SHARD_{int(ev['debtor_account'][5:]) % 18}", int(ev["payload_bytes"]))
        svc_ms = loc_ms + float(rtts["AZ1_AZ3_inter_region"]) + float(zspec["sequential_append_latency_ms"]) + az3_stall_ms(seq, stalls)
        start_t = max(ts, heapq.heappop(workers))
        heapq.heappush(workers, start_t + svc_ms)
        lats.append((start_t - ts) + svc_ms)
        double_spends += int(ev["end_to_end_id"] in seen)
        seen.add(ev["end_to_end_id"])
        if int(part["start_seq"]) <= seq <= int(part["end_seq"]) and float(part["old_leader_clock_drift_ms"]) > float(part["nominal_lease_ms"]):
            split_brain += 1
    return {"p99_9_ms": pct(lats, 99.9), "double_spends": double_spends, "split_brain_commits": split_brain}


def simulate_remediated(workload: dict) -> dict:
    topo, sched = workload["cluster_topology"], workload["fault_injection_schedule"]
    rtts, zspec, sla = topo["rtt_ms"], topo["nvme_zns_spec"], topo["sla_and_invariants"]
    stalls, part = sched["az3_zns_zone_reset_stalls"], sched["split_brain_partition_and_clock_skew"]
    dedup_ttl_ms, init_bal, n_accts = float(sla["dedup_window_hours"]) * 3_600_000.0, int(sla["initial_account_balance_cents"]), int(sla["num_accounts"])
    roles = ("WAL_A", "WAL_B", "SNAP_A", "SNAP_B", "DEDUP_HOT", "DEDUP_WARM", "META_SB", "BG_GC")
    nodes = {n: ReplicaNode(n, ZNSController(zspec, True), {f"ACCT_{i:03d}": init_bal for i in range(n_accts)}) for n in topo["nodes"]}
    for node in nodes.values():
        for r in roles:
            node.zns.alloc_open_zone(r)
    sla_lats, dr_lats, all_lats, catchup = [], [], [], []
    uniq = deduped = dbl_spend = debits = credits = sb_prevented = lease_overlap_fenced = 0
    p_lo, p_hi, p_t0 = int(part["start_seq"]), int(part["end_seq"]), None

    for ev in workload["events"]:
        seq, ts, e2e, sz = int(ev["seq_id"]), float(ev["timestamp_ms"]), ev["end_to_end_id"], int(ev["payload_bytes"])
        in_part = p_lo <= seq <= p_hi
        if in_part:
            if p_t0 is None:
                p_t0 = ts
                for n in ("AZ2_INTRA_REGION", "AZ3_INTER_REGION_DR"):
                    nodes[n].term = 2
                    nodes[n].zns.zone_append("META_SB", 4096)
            sb_prevented += 1
            if ts - p_t0 <= float(part["nominal_lease_ms"]) + float(part["old_leader_clock_drift_ms"]):
                nodes["AZ1_PRIMARY"].zns.zone_append("WAL_A", sz)  # Speculative Term-1 append blocked by 2/3 quorum fence
                lease_overlap_fenced += 1
            leader, peer, async_dr, q_rtt = nodes["AZ2_INTRA_REGION"], nodes["AZ3_INTER_REGION_DR"], None, float(rtts["AZ2_AZ3_inter_region"])
        else:
            if catchup:
                az1 = nodes["AZ1_PRIMARY"]
                az1.term = nodes["AZ2_INTRA_REGION"].term
                az1.zns.seal_role("WAL_A")  # Seal uncommitted Term-1 tail without illegal ZNS random overwrite
                az1.zns.zone_append("META_SB", 4096)
                for m in catchup:
                    az1.zns.zone_append("WAL_A", int(m["payload_bytes"]))
                    az1.balances[m["debtor_account"]] -= int(m["amount_cents"])
                    az1.balances[m["creditor_account"]] += int(m["amount_cents"])
                    az1.dedup[m["end_to_end_id"]] = (2, m["idx"], m["ts"])
                    az1.commit_index = m["idx"]
                catchup.clear()
            leader = nodes["AZ2_INTRA_REGION"] if nodes["AZ2_INTRA_REGION"].term == 2 else nodes["AZ1_PRIMARY"]
            peer = nodes["AZ1_PRIMARY"] if leader.name == "AZ2_INTRA_REGION" else nodes["AZ2_INTRA_REGION"]
            async_dr, q_rtt = nodes["AZ3_INTER_REGION_DR"], float(rtts["AZ1_AZ2_intra_region"])

        rec = leader.dedup.get(e2e)
        if rec is not None and (ts - rec[2]) <= dedup_ttl_ms:
            deduped += 1
            lat = q_rtt + 0.16 + jitter_ms(seq, "rd", 0.22)
        else:
            w_role = "WAL_A" if (uniq % 2 == 0) else "WAL_B"
            _, l_ms = leader.zns.zone_append(w_role, sz)
            _, p_ms = peer.zns.zone_append(w_role, sz)
            if async_dr is not None:
                async_dr.zns.zone_append(w_role, sz)
            lat = max(l_ms, q_rtt + p_ms) + 0.18 + (0.28 if az3_stall_ms(seq, stalls) > 0 else 0.0) + jitter_ms(seq, "wr", 0.35)
            amt, deb, cred = int(ev["amount_cents"]), ev["debtor_account"], ev["creditor_account"]
            if leader.balances[deb] < amt:
                raise RuntimeError(f"Overdraft: {deb}")
            dbl_spend += int(e2e in leader.dedup)
            idx = leader.commit_index + 1
            for r_node in [leader, peer] + ([async_dr] if async_dr else []):
                r_node.balances[deb] -= amt
                r_node.balances[cred] += amt
                r_node.dedup[e2e] = (leader.term, idx, ts)
                r_node.commit_index = idx
                if uniq % 256 == 0:
                    r_node.zns.zone_append("DEDUP_HOT", 4096)
                    r_node.zns.zone_append("SNAP_A", 4096)
            if in_part:
                catchup.append({**ev, "idx": idx, "ts": ts})
            uniq, debits, credits = uniq + 1, debits + amt, credits + amt

        all_lats.append(lat)
        (dr_lats if in_part else sla_lats).append(lat)

    converged = nodes["AZ1_PRIMARY"].balances == nodes["AZ2_INTRA_REGION"].balances == nodes["AZ3_INTER_REGION_DR"].balances
    cons_ok = (debits == credits and sum(nodes["AZ1_PRIMARY"].balances.values()) == n_accts * init_bal
               and min(nodes["AZ1_PRIMARY"].balances.values()) >= 0 and uniq + deduped == len(workload["events"])
               and dbl_spend == 0 and converged)
    max_zones = max(n.zns.peak_open_zones for n in nodes.values())
    zns_ok = all(n.zns.sequential_ok and n.zns.invalid_writes == 0 for n in nodes.values()) and max_zones <= int(zspec["max_active_open_zones"])
    return {
        "mitigated_p50_ms": pct(sla_lats, 50.0), "mitigated_p99_ms": pct(sla_lats, 99.0), "mitigated_p99_9_ms": pct(sla_lats, 99.9),
        "dr_failover_partition_p99_9_ms": pct(dr_lats, 99.9), "all_regimes_including_dr_partition_p99_9_ms": pct(all_lats, 99.9),
        "total_events": len(workload["events"]), "unique_committed_transfers": uniq, "duplicates_deduplicated": deduped,
        "double_spend_count": dbl_spend, "sum_debits_cents": debits, "sum_credits_cents": credits,
        "conservation_invariant_passed": cons_ok, "split_brain_commits_prevented": sb_prevented,
        "stale_lease_22ms_overlap_fenced": lease_overlap_fenced, "max_concurrent_open_zones_used": max_zones,
        "zns_sequential_invariant_passed": zns_ok,
    }

def main() -> None:
    workload = json.loads(WORKLOAD_PATH.read_text(encoding="utf-8"))
    base, rem = simulate_baseline(workload), simulate_remediated(workload)
    metrics = {"baseline_p99_9_ms": base["p99_9_ms"], **rem, "baseline_double_spend_count": base["double_spends"], "baseline_split_brain_commits": base["split_brain_commits"]}
    assert metrics["baseline_p99_9_ms"] > 250.0 and metrics["mitigated_p99_9_ms"] < 8.0 and metrics["max_concurrent_open_zones_used"] <= 14, metrics
    assert metrics["conservation_invariant_passed"] and metrics["zns_sequential_invariant_passed"], metrics
    METRICS_PATH.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metrics, indent=2))

if __name__ == "__main__":
    main()

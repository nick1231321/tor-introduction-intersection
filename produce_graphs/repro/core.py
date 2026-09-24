"""Data loading and derived quantities for generate.py.

Reads the per-iteration intersection trajectories and the per-run/stage
metadata from data/ and derives T<=q, T_conv, initial set sizes and per-run
totals from the trajectories.
"""
from __future__ import annotations
import csv, os
from pathlib import Path

STAGES = ["IP", "M1", "VG", "EG"]                    # raw stage codes, in circuit order
RUN_IDS = list(range(4, 13))                          # raw run ids 4..12
PAPER_RUN = {rid: rid - 3 for rid in RUN_IDS}         # paper numbering 1..9
SECONDS_PER_ITER = 31.0                               # delta 30 s + ~1 s handshake

_HERE = Path(__file__).resolve().parent


def _first_dir(*cands):
    for c in cands:
        if c and Path(c).is_dir():
            return Path(c).resolve()
    return Path(cands[-1]).resolve()


# Raw data directory: $REPRO_DATA if set, else ./data
DATA = _first_dir(os.environ.get("REPRO_DATA"), _HERE / "data")


def load_trajectories(path: Path = None):
    """Return {(run_id, stage): [ |I_t| for t=1..T ]} from the raw CSV."""
    path = path or DATA / "trajectories_every_trial.csv"
    if not path.exists():
        raise FileNotFoundError(f"missing raw trajectories: {path}")
    traj: dict[tuple[int, str], list[int]] = {}
    for r in csv.DictReader(open(path)):
        key = (int(r["run_id"]), r["stage"])
        traj.setdefault(key, []).append((int(r["trial"]), int(r["intersection_size"])))
    out = {}
    for key, seq in traj.items():
        seq.sort()                                    # by trial index
        trials = [t for t, _ in seq]
        assert trials == list(range(1, len(seq) + 1)), f"non-contiguous trials for {key}"
        out[key] = [v for _, v in seq]
    # integrity: exactly 9 runs x 4 stages
    got_runs = sorted({rid for rid, _ in out})
    assert got_runs == RUN_IDS, f"expected runs {RUN_IDS}, got {got_runs}"
    for rid in RUN_IDS:
        for s in STAGES:
            assert (rid, s) in out, f"missing stage {s} for run {rid}"
    return out


def load_metrics(path: Path = None):
    """Return {(run_id, stage): row_dict} from the per-run/stage metrics CSV."""
    path = path or DATA / "run_stage_metrics.csv"
    if not path.exists():
        raise FileNotFoundError(f"missing metrics: {path}")
    m = {}
    for r in csv.DictReader(open(path)):
        m[(int(r["run_id"]), r["stage_code"])] = r
    assert len(m) == 36, f"expected 36 run-stage rows, got {len(m)}"
    return m


# ---- derived quantities, computed purely from |I_t| trajectories ----
def T_le(seq, q):
    """First trial index t (1-based) with |I_t| <= q, else None."""
    for i, v in enumerate(seq, start=1):
        if v <= q:
            return i
    return None


def T_conv(seq):
    return T_le(seq, 1)


def initial_set_size(seq):
    return seq[0]


def per_run_total(traj, rid):
    return sum(T_conv(traj[(rid, s)]) for s in STAGES)


def hours(total_iters):
    return total_iters * SECONDS_PER_ITER / 3600.0


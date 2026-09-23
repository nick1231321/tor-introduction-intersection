"""Experiment-structure claims (module 'setup_structure').

Checks the paper's statements about the shape of the experiment -- nine runs,
four stages per run, 36 run--stage observations, stage order, run ids 1--9,
the date span and the run schedule -- against the raw CSVs
(TRAJ = data/trajectories_every_trial.csv, MET = data/run_stage_metrics.csv)
and the per-stage experiment_date / day_label / experiment_time_utc labels in
MET (minute resolution).

Every claim's quoted text is re-located in the CURRENT paper (core.relocate:
the registered file:line first, then the whole file, then every active .tex
file reachable from main.tex); the report shows where it is printed now and
notes "moved from <registered anchor>" when that differs. A quote that is
printed nowhere marks the claim FAIL ('stale registry') regardless of the
numeric outcome, so a restructured paper cannot produce a silent PASS.
Without the paper sources the numeric status is kept (the printed value is
hard-coded here) and the note says the quote was not verified; the two
claims whose paper side is parsed from a table (setup-011, setup-023,
setup-027) report FAIL with "paper sources not available".

Every 'computed' field is derived at call time from traj/metrics only, so
reviewer mode can replay it against claims_snapshot.json.
"""
from __future__ import annotations

import re
from datetime import date

import core as _core   # shared tex/timestamp helpers (single copy in core.py)

STAGES = ["IP", "M1", "VG", "EG"]
RAW_RUNS = list(range(4, 13))


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def _tex_lines(rel):
    """Current (comment-stripped) lines of a .tex file, line numbers preserved."""
    return _core.tex_lines(rel)


_norm = _core.norm_ws


def _hhmm(row):
    """'HH:MM' of a MET row's experiment_time_utc ('HH:MM UTC')."""
    return (row.get("experiment_time_utc") or "").strip().split(" ")[0][:5]


def _stage_date(row):
    """datetime.date of a MET row's experiment_date (YYYY-MM-DD)."""
    return date.fromisoformat((row.get("experiment_date") or "").strip())


def _stage_start(row):
    """(experiment_date, 'HH:MM') of a stage's own MET row: its start day and
    time at minute resolution, chronologically ordered as a tuple."""
    return (_stage_date(row), _hhmm(row))


def _relocate(loc, quote):
    """(status, location, note) of a registry anchor in the CURRENT paper via
    core.relocate (registered file:line first, then the whole file, then every
    active file; comment blocks and %-lines blanked, whitespace normalised).
    A long quote is also tried on its first 40 characters (line-wrapping
    tolerance) before being declared absent."""
    st, where, note = _core.relocate(loc, quote)
    if st == "absent":
        q = _norm(quote)
        if len(q) > 40:
            st2, where2, note2 = _core.relocate(loc, q[:40])
            if st2 == "found":
                return st2, where2, note2
    return st, where, note


def _run_ids(traj, metrics):
    tr = sorted({rid for rid, _ in traj})
    mr = sorted({rid for rid, _ in metrics})
    return tr, mr


def _stage_sets(traj, metrics):
    """{run_id: set(stages)} for TRAJ and for MET."""
    ts, ms = {}, {}
    for rid, s in traj:
        ts.setdefault(rid, set()).add(s)
    for rid, s in metrics:
        ms.setdefault(rid, set()).add(s)
    return ts, ms


def _nine_runs_check(traj, metrics):
    tr, mr = _run_ids(traj, metrics)
    ok = (len(tr) == 9 and tr == RAW_RUNS and len(mr) == 9 and mr == RAW_RUNS)
    span = f"raw ids {tr[0]}..{tr[-1]}" if tr else "no runs"
    comp = f"{len(tr)} runs in TRAJ ({span}), {len(mr)} in MET"
    return ok, comp


def _four_stages_check(traj, metrics):
    ts, ms = _stage_sets(traj, metrics)
    want = set(STAGES)
    ok = all(ts.get(r) == want for r in RAW_RUNS) and \
        all(ms.get(r) == want for r in RAW_RUNS)
    n_t = sorted({len(v) for v in ts.values()})
    n_m = sorted({len(v) for v in ms.values()})
    codes = sorted(set().union(*ms.values())) if ms else []
    comp = f"{'/'.join(map(str, n_t))} stage codes per run in TRAJ, " \
           f"{'/'.join(map(str, n_m))} in MET (codes {codes})"
    return ok, comp


def _stage_order_check(metrics):
    """(experiment_date, HH:MM) strictly increasing IP < M1 < VG < EG within
    each run (each stage's own MET row gives its start day and time)."""
    bad = []
    for rid in RAW_RUNS:
        rows = [metrics.get((rid, s)) for s in STAGES]
        if any(r is None for r in rows):
            bad.append((rid, "missing stage"))
            continue
        ts = [_stage_start(r) for r in rows]
        if not all(ts[i] < ts[i + 1] for i in range(3)):
            order = [s for _, s in sorted(zip(ts, STAGES))]
            bad.append((rid, "->".join(order)))
    return (not bad), bad


# --------------------------------------------------------------------------
def claims(C, traj, metrics):
    out = []
    STALE = "quote not found at location (stale registry)"
    have_tex = _core.paper_present()

    def add(cid, loc, quote, paper, computed, status, note=""):
        """Append a claim whose quote is re-located in the current paper; the
        reported location is where the quote is printed NOW, `loc` only the
        registered fallback anchor. A quote printed nowhere is FAIL (stale
        registry); without sources the status is kept and the note says so."""
        st_, where, mv = _relocate(loc, quote)
        if st_ == "absent":
            status = "FAIL"
            note = (STALE + ("; " + note if note else ""))
            loc = where
        elif st_ == "nofile":
            note = ("paper sources not found; quote not verified" + ("; " + note if note else ""))
        else:
            loc = where
            if mv:
                note = f"[{mv}]" + ("; " + note if note else "")
        out.append({"id": cid, "location": loc, "quote": quote,
                    "paper": str(paper), "computed": str(computed),
                    "status": status, "note": note})

    def st(ok):
        return "PASS" if ok else "FAIL"

    # run labels printed in the appendix table (compared in setup-027)
    app = _tex_lines("sections/appendix_results.tex")
    app_labels = []
    if app is not None:
        m = re.search(r"\\label\{tab:run-stage-thresholds\}.*?\\midrule(.*?)\\bottomrule",
                      "\n".join(app), re.S)
        if m:
            app_labels = re.findall(r"R(\d+)\s*\(Day\s*(\d+),\s*(\d{2}:\d{2})\)", m.group(1))

    # ---- setup-026 (date span) ----
    dates = sorted({_stage_date(r) for r in metrics.values()})
    day_map = {}
    for r in metrics.values():
        day_map.setdefault(r.get("day_label"), set()).add(_stage_date(r))
    day_ok = all(len(v) == 1 for v in day_map.values()) and \
        sorted(day_map) == [f"Day {i}" for i in range(1, 5)] and \
        all(next(iter(day_map[f"Day {i}"])) == date(2026, 1, 6 + i) for i in range(1, 5))
    ok26 = bool(dates) and dates[0] == date(2026, 1, 7) and dates[-1] == date(2026, 1, 10) and day_ok
    add("setup-026", "sections/appendix_results.tex:14",
        "conducted on 7--10~January~2026.", "7--10 January 2026",
        (f"{dates[0].isoformat()} .. {dates[-1].isoformat()} over {len(metrics)} experiment_date; "
         f"day_label Day 1..4 -> {[next(iter(day_map[d])).strftime('%d') for d in sorted(day_map)]} Jan")
        if dates else "no MET rows",
        st(ok26),
        "min/max of MET.experiment_date (per stage row); day_label must map 1:1 onto 07..10 Jan.")

    # ---- setup-027 (run schedule, from the IP-stage row's labels) ----
    got_sched = []
    for rid in RAW_RUNS:
        r = metrics.get((rid, "IP"))
        if r is None:
            got_sched.append((C.PAPER_RUN.get(rid, rid - 3), None, None))
            continue
        got_sched.append((C.PAPER_RUN.get(rid, rid - 3), r.get("day_label"), _hhmm(r)))
    tex_sched = [(int(a), f"Day {b}", c) for a, b, c in app_labels]
    ok27 = bool(tex_sched) and tex_sched == got_sched
    add("setup-027", "sections/appendix_results.tex:26",
        "R1 (Day 1, 02:00)",
        "; ".join(f"R{a} ({b}, {c})" for a, b, c in tex_sched) or "n/a",
        "; ".join(f"R{a} ({b}, {c})" for a, b, c in got_sched),
        st(ok27),
        "Run label = (day_label, HH:MM of experiment_time_utc) of the IP-stage row in MET, "
        "compared with the 9 'Rn (Day d, hh:mm)' labels parsed from the appendix "
        "table (R1..R9 at lines 26 ff.); day_label is anchored to the date by "
        "setup-026. ASSUMPTION: a run is labelled by its IP-stage start (later "
        "stages may begin on a later day, e.g. raw run 9 EG on Day 3)."
        + ("" if have_tex else " paper sources not available."))

    return out

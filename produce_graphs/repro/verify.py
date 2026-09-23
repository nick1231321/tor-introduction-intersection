#!/usr/bin/env python3
"""Verify every measurement-based number printed in the paper against the data.

    python3 verify.py [--module NAME ...] [--full] [--out PATH]

1. Data integrity: the two CSVs must describe the same 36 (run, stage) pairs.
   The released run_stage_metrics.csv carries no precomputed convergence
   columns (it holds run/stage labels and the consensus weight only); every
   convergence quantity is derived from trajectories_every_trial.csv via
   core.T_le / core.T_conv / core.initial_set_size. Should a precomputed
   column (T_le_q, trials_to_convergence, initial_intersection_size,
   n_recorded_iterations) ever be present, it is compared with the
   trajectory-derived value; absent columns are skipped.
2. Every module in checks/ (discovered with pkgutil) exposes
       claims(C, traj, metrics) -> [ {id, location, quote, paper, computed,
                                      status, note}, ... ]
   with status in PASS | FAIL | UNVERIFIABLE | CONSTANT. All records are
   concatenated. A module that fails to import or raises is itself a FAIL row.
3. checks/legacy.py names the module ids that replaced the old hand-written
   registry; an id it names that no module produced is a FAIL row.
4. The report (one row per claim, sorted by paper order of the .tex file and
   then by line) is printed and written to out/verify_report.md.
5. Exit status is 1 iff any claim FAILs or the integrity check finds a mismatch.
"""
from __future__ import annotations

import argparse
import importlib
import os
import pkgutil
import re
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core as C            # noqa: E402
import checks as checks_pkg  # noqa: E402

HERE = Path(__file__).resolve().parent
DEFAULT_OUT = HERE / "out" / "verify_report.md"
STATUSES = ("PASS", "FAIL", "UNVERIFIABLE", "CONSTANT")
COLS = ("id", "location", "paper", "computed", "status", "note")
INTEGRITY_COLS = [("T_le_10", 10), ("T_le_5", 5), ("T_le_3", 3), ("T_le_2", 2), ("T_le_1", 1)]


# --------------------------------------------------------------------------- data
def integrity_check(traj, metrics):
    """Mismatch strings between the metrics CSV and the raw trajectories.

    Both files must cover the same (run, stage) keys. Precomputed convergence
    columns are compared only when the metrics file actually carries them; the
    released file carries none, so with no such column present the result is
    [] (every convergence quantity is trajectory-derived, nothing to compare).
    """
    bad = []
    present = set()
    for row in metrics.values():
        present.update(k for k, v in row.items() if k and str(v).strip() != "")
    cols = {k: (lambda seq, q=q: C.T_le(seq, q)) for k, q in INTEGRITY_COLS if k in present}
    if "trials_to_convergence" in present:
        cols["trials_to_convergence"] = C.T_conv
    if "initial_intersection_size" in present:
        cols["initial_intersection_size"] = C.initial_set_size
    if "n_recorded_iterations" in present:
        cols["n_recorded_iterations"] = len
    for key in sorted(set(traj) | set(metrics)):
        rid, s = key
        if key not in traj:
            bad.append(f"{rid}/{s}: in metrics but no trajectory")
            continue
        if key not in metrics:
            bad.append(f"{rid}/{s}: trajectory but no metrics row")
            continue
        seq, row = traj[key], metrics[key]
        for k, fn in cols.items():
            got = row.get(k, "")
            got = int(float(got)) if str(got).strip() != "" else None
            v = fn(seq)
            if got != v:
                bad.append(f"{rid}/{s} {k}: metrics={got} trajectory={v}")
    return bad


# ------------------------------------------------------------------------- claims
def _normalise(rec, module):
    """Coerce a module record into the six report columns; unknown status -> FAIL."""
    r = {k: str(rec.get(k, "")) for k in ("id", "location", "quote", "paper", "computed", "note")}
    r["status"] = str(rec.get("status", "")).upper()
    r["module"] = module
    if r["status"] not in STATUSES:
        r["note"] = f"module returned unknown status {rec.get('status')!r}; " + r["note"]
        r["status"] = "FAIL"
    if not r["id"]:
        r["id"] = f"{module}-?"
    return r


def load_claims(traj, metrics, only=None):
    rows, covered_by = [], {}
    for mi in sorted(pkgutil.iter_modules(checks_pkg.__path__), key=lambda m: m.name):
        if only and mi.name not in only:
            continue
        qual = f"checks.{mi.name}"
        try:
            mod = importlib.import_module(qual)
            recs = mod.claims(C, traj, metrics)
            rows.extend(_normalise(r, mi.name) for r in recs)
            for name, ids in getattr(mod, "COVERED_BY", {}).items():
                covered_by[name] = (mi.name, list(ids))
        except Exception as e:  # noqa: BLE001 - a broken module must show up, never vanish
            tb = traceback.format_exc().strip().splitlines()[-1]
            rows.append({"id": f"{mi.name} (module error)", "module": mi.name,
                         "location": f"repro/checks/{mi.name}.py:?", "quote": "",
                         "paper": "-", "computed": f"{type(e).__name__}: {e}",
                         "status": "FAIL", "note": tb})
    if not only:   # coverage guard only makes sense when every module ran
        have = {r["id"] for r in rows}
        for name, (mod, ids) in covered_by.items():
            missing = [i for i in ids if i not in have]
            if missing:
                rows.append({"id": f"{mod}-coverage", "module": mod,
                             "location": f"repro/checks/{mod}.py:?", "quote": name,
                             "paper": ", ".join(ids), "computed": f"missing ids: {missing}",
                             "status": "FAIL",
                             "note": f"old registry claim {name!r} is mapped to module ids "
                                     f"that no module produced; update COVERED_BY or re-add the check."})
    # duplicate ids across modules are a registry bug
    seen, dup = {}, set()
    for r in rows:
        seen.setdefault(r["id"], []).append(r["module"])
    for cid, mods in seen.items():
        if len(mods) > 1:
            dup.add(cid)
    if dup:
        rows.append({"id": "verify-duplicate-ids", "module": "verify", "location": "repro/checks:?",
                     "quote": "", "paper": "-", "computed": ", ".join(sorted(dup)),
                     "status": "FAIL", "note": "claim ids must be unique across modules"})
    return rows


# ----------------------------------------------------------------------- ordering
def paper_file_order():
    """Files in the order the paper includes them: main.tex, then each \\input
    of the ACTIVE part of main.tex (recursively), then anything else."""
    order, seen = [], set()

    def walk(rel):
        if rel in seen:
            return
        seen.add(rel)
        order.append(rel)
        for ln in C.tex_lines(rel) or []:
            for m in re.finditer(r"\\input\{([^}]+)\}", ln):
                sub = m.group(1)
                if not sub.endswith(".tex"):
                    sub += ".tex"
                walk(sub)
    walk("main.tex")
    return {rel: i for i, rel in enumerate(order)}


def loc_key(loc, file_rank):
    m = re.match(r"^(.*?):(\d+)?(?:-+\d+)?\??$", loc.strip())
    if not m:
        return (10**6, loc, 10**9)
    rel, line = m.group(1), m.group(2)
    rank = file_rank.get(rel, 10**5 + (0 if rel.startswith("sections/") else 1))
    return (rank, rel, int(line) if line else 10**9)


# ------------------------------------------------------------------------ report
def _cell(s, width=None):
    s = " ".join(str(s).split()).replace("|", "\\|")
    if width and len(s) > width:
        s = s[: width - 1] + "…"
    return s


def render_table(rows, full):
    w = None if full else {"paper": 34, "computed": 48, "note": 72}
    widths = {c: len(c) for c in COLS}
    cells = []
    for r in rows:
        row = {c: _cell(r[c], w and w.get(c)) for c in COLS}
        cells.append(row)
        for c in COLS:
            widths[c] = max(widths[c], len(row[c]))
    lines = ["| " + " | ".join(c.ljust(widths[c]) for c in COLS) + " |",
             "|" + "|".join("-" * (widths[c] + 2) for c in COLS) + "|"]
    for row in cells:
        lines.append("| " + " | ".join(row[c].ljust(widths[c]) for c in COLS) + " |")
    return "\n".join(lines)


def counts(rows):
    return {s: sum(1 for r in rows if r["status"] == s) for s in STATUSES}


def render_report(rows, integ, full):
    n = counts(rows)
    parts = ["# Verification report", "",
             f"Data: `{C.DATA / 'trajectories_every_trial.csv'}` and "
             f"`{C.DATA / 'run_stage_metrics.csv'}`.", "",
             "Rows are sorted by paper order of the .tex file, then line "
             "(`file:?` = quote not located in the current text).", "",
             render_table(rows, full), "",
             "## Counts", "",
             ", ".join(f"{s} {n[s]}" for s in STATUSES)
             + f"; total {len(rows)}; data-integrity mismatches {len(integ)}", ""]
    fails = [r for r in rows if r["status"] == "FAIL"]
    parts += ["## FAIL details", ""]
    if not fails:
        parts.append("none")
    for r in fails:
        parts += [f"### {r['id']} [{r['location']}]", "",
                  f"- quote: `{_cell(r['quote'])}`" if r["quote"] else "- quote: (none)",
                  f"- paper: {_cell(r['paper'])}",
                  f"- computed: {_cell(r['computed'])}",
                  f"- note: {_cell(r['note'])}", ""]
    parts += ["## Data integrity (metrics CSV vs trajectories)", ""]
    parts += ["- " + x for x in integ] if integ else [
        "both CSVs cover the same 36 (run, stage) pairs; the metrics file carries no "
        "precomputed convergence columns (all such quantities are trajectory-derived)"]
    return "\n".join(parts) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--module", action="append", help="run only this checks/ module (repeatable)")
    ap.add_argument("--full", action="store_true", help="do not truncate cells on the console")
    ap.add_argument("--out", default=str(DEFAULT_OUT), help="markdown report path ('' = do not write)")
    a = ap.parse_args(argv)

    traj = C.load_trajectories()
    metrics = C.load_metrics()
    integ = integrity_check(traj, metrics)
    rows = load_claims(traj, metrics, only=set(a.module) if a.module else None)
    no_tex = not (C.ROOT / "main.tex").exists()
    if no_tex:
        # Without the paper sources the printed side of a claim cannot be read, so
        # nothing can PASS or FAIL: keep the recomputed values, mark the rest.
        for r in rows:
            if r["status"] in ("PASS", "FAIL") and not r["id"].endswith("(module error)"):
                r["status"] = "UNVERIFIABLE"
                r["note"] = "paper sources not found (set PAPER_ROOT to the directory holding main.tex); " + r["note"]
    rank = paper_file_order()
    rows.sort(key=lambda r: (loc_key(r["location"], rank), r["id"]))

    if no_tex:
        print(f"NOTE: no main.tex under {C.ROOT}; comparison against the printed values is skipped.\n"
              "      Set PAPER_ROOT=<paper source dir> to check the paper text. Computed values follow.\n")
    print(render_table(rows, a.full or os.environ.get("VERIFY_FULL") == "1"))
    n = counts(rows)
    print("\n" + ", ".join(f"{s} {n[s]}" for s in STATUSES)
          + f"; total {len(rows)}; data-integrity mismatches {len(integ)}")
    if integ:
        print("\nDATA INTEGRITY MISMATCHES:")
        for x in integ:
            print("  " + x)
    if n["FAIL"]:
        print("\nFAILED CLAIMS (full text):")
        for r in rows:
            if r["status"] == "FAIL":
                print(f"  {r['id']} [{r['location']}]\n    paper:    {r['paper']}\n"
                      f"    computed: {r['computed']}\n    note:     {r['note']}")
    if a.out:
        out = Path(a.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_report(rows, integ, full=True), encoding="utf-8")
        print(f"\nreport written to {out}")
    return 1 if (n["FAIL"] or integ) else 0


if __name__ == "__main__":
    sys.exit(main())

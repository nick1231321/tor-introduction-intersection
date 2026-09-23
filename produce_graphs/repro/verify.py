#!/usr/bin/env python3
"""Verify every number the paper derives from the nine experimental runs.

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
   with status PASS or FAIL. Every `computed` value is a function of the two
   CSVs alone. All records are concatenated; a module that fails to import
   or raises is itself a FAIL row.
3. Modes:
   * with the paper sources (PAPER_ROOT/main.tex exists): the printed side of
     each claim is read from the LaTeX text; the run freezes every row into
     claims_snapshot.json;
   * without the sources but with claims_snapshot.json (reviewer mode): the
     sentence, location and printed value come from the snapshot, `computed`
     is recomputed now; PASS iff the snapshot row was PASS and today's value
     equals the frozen one; a claim missing on either side is FAIL;
   * without sources and without snapshot: nothing can be compared, so every
     row is printed with paper "n/a" and status FAIL under a NO-SNAPSHOT
     banner, and the exit status is 2.
4. The report (one row per claim, sorted by paper order of the .tex file and
   then by line) is printed and written to out/verify_report.md; the manual
   checklist to out/manual_checklist.md.
5. Exit status is 1 iff any claim FAILs or the integrity check finds a mismatch
   (2 in the NO-SNAPSHOT case).
"""
from __future__ import annotations

import argparse
import json
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
SNAPSHOT = HERE / "claims_snapshot.json"          # printed values frozen from the submitted paper
CHECKLIST = HERE / "out" / "manual_checklist.md"  # reviewer-facing list
STATUSES = ("PASS", "FAIL")
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
    rows = []
    for mi in sorted(pkgutil.iter_modules(checks_pkg.__path__), key=lambda m: m.name):
        if only and mi.name not in only:
            continue
        qual = f"checks.{mi.name}"
        try:
            mod = importlib.import_module(qual)
            recs = mod.claims(C, traj, metrics)
            rows.extend(_normalise(r, mi.name) for r in recs)
        except Exception as e:  # noqa: BLE001 - a broken module must show up, never vanish
            tb = traceback.format_exc().strip().splitlines()[-1]
            rows.append({"id": f"{mi.name} (module error)", "module": mi.name,
                         "location": f"repro/checks/{mi.name}.py:?", "quote": "",
                         "paper": "-", "computed": f"{type(e).__name__}: {e}",
                         "status": "FAIL", "note": tb})
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


# ------------------------------------------------------------------- snapshot
_TEX_SUBS = [
    (r"\\textbf\{([^}]*)\}", r"\1"), (r"\\textit\{([^}]*)\}", r"\1"), (r"\\emph\{([^}]*)\}", r"\1"),
    (r"\\texttt\{([^}]*)\}", r"\1"), (r"\\mathrm\{([^}]*)\}", r"\1"), (r"\\mathcal\{([^}]*)\}", r"\1"),
    (r"\\tilde\{([^}]*)\}", r"\1"), (r"\\(?:ref|eqref)\{[^}]*\}", "[ref]"), (r"~?\\cite\{[^}]*\}", ""),
    (r"\\label\{[^}]*\}", ""), (r"\\multicolumn\{\d+\}\{[^}]*\}\{([^}]*)\}", r"\1"),
    (r"\\ldots", "..."), (r"\\cdots", "..."), (r"\\leq", "<="), (r"\\geq", ">="), (r"\\max", "max"), (r"\\min", "min"), (r"\\%", "%"),
    (r"\\,", " "), (r"\\\\", ""), (r"\\(?:midrule|toprule|bottomrule|addlinespace|noindent)", ""),
    (r"\$", ""), (r"~", " "), (r"--", "-"), (r"\\&", "&"), (r"[{}]", ""), (r"\s+", " "),
]


def plain(tex: str) -> str:
    """LaTeX snippet -> readable text a reviewer can search for in the PDF."""
    out = tex
    for pat, rep in _TEX_SUBS:
        out = re.sub(pat, rep, out)
    return out.strip()


def write_snapshot(rows):
    """Freeze the paper side of every claim (sentence, printed value) together
    with the value recomputed at that time, so the check can be replayed and
    read without the LaTeX sources."""
    data = [{k: r[k] for k in ("id", "location", "quote", "paper", "computed", "status", "note")}
            for r in rows]
    SNAPSHOT.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return len(data)


def _squash(v):
    return " ".join(str(v).split())


def apply_snapshot(rows, partial=False):
    """Reviewer mode: no LaTeX sources. Take the sentence, location and printed
    value of each claim from the snapshot and recompute the value from data/
    now. PASS iff the snapshot's comparison passed AND today's recomputation
    equals the one frozen with it (a changed dataset or check shows up as
    FAIL). A claim produced now but absent from the snapshot, or frozen in the
    snapshot but not produced now, is FAIL (the latter only when every module
    ran, i.e. partial=False)."""
    snap = {d["id"]: d for d in json.loads(SNAPSHOT.read_text(encoding="utf-8"))}
    seen = set()
    for r in rows:
        d = snap.get(r["id"])
        if d is None:
            r["status"] = "FAIL"
            r["note"] = "claim not in claims_snapshot.json (added after the snapshot); " + r["note"]
            continue
        seen.add(r["id"])
        r["quote"], r["paper"], r["location"] = d["quote"], d["paper"], d["location"]
        same = _squash(r["computed"]) == _squash(d["computed"])
        r["status"] = "PASS" if (d["status"] == "PASS" and same) else "FAIL"
        r["note"] = (("" if same else "RECOMPUTED VALUE DIFFERS from the one frozen in the snapshot "
                      f"({d['computed']}); ") + ("" if d["status"] == "PASS" else
                     "the snapshot already recorded a mismatch with the printed value; ") + d["note"])
    for cid, d in snap.items():
        if cid not in seen and not partial:
            rows.append({**{k: d[k] for k in ("id", "location", "quote", "paper", "computed")},
                         "status": "FAIL", "module": "snapshot",
                         "note": "claim is in the snapshot but no check produced it now; " + d["note"]})
    return rows


_SECTION = [("main.tex", "Abstract"), ("01-", "Section 1"), ("02-", "Section 2"), ("03-", "Section 3"),
            ("04-", "Section 4"), ("05-", "Section 5"), ("06-", "Section 6"), ("07-", "Section 7"),
            ("appendix_results", "Appendix A"), ("implementation", "Appendix B"),
            ("appendix_time", "Appendix C"), ("appendix_relay", "Appendix D")]


def section_of(loc):
    f = loc.split(":")[0]
    for key, name in _SECTION:
        if key in f:
            return name
    return f


def _readable(v):
    v = _squash(v)
    return re.sub(r"\bTRAJ\b", "trajectories", re.sub(r"\bMET\b", "run metadata", v))


def render_simple(rows, integ):
    """What a reviewer reads: per claim, where it is in the paper, what the
    paper says, the value printed there, the value recomputed from data/, and
    PASS/FAIL."""
    n = counts(rows)
    out = []
    cur = None
    for r in rows:
        sec = section_of(r["location"])
        if sec != cur:
            cur = sec
            out += ["", f"== {sec} =="]
        says = plain(r["quote"]) if r["quote"] else f"table row {r['id']}"
        out += [f"[{r['status']}] \"{says}\"",
                f"       paper: {plain(r['paper'])}",
                f"       data:  {_readable(r['computed'])}"]
    out += ["", ", ".join(f"{st} {n[st]}" for st in STATUSES) + f"; total {len(rows)}"
            + (f"; DATA INTEGRITY MISMATCHES {len(integ)}" if integ else "")]
    return "\n".join(out).lstrip("\n") + "\n"


def render_checklist(rows, integ):
    """Markdown list a reviewer can walk through with the PDF open."""
    n = counts(rows)
    parts = ["# Manual verification checklist", "",
             "For each claim: the sentence or table row as printed in the paper (search for it in the PDF),",
             "the value printed there, and the value recomputed from `data/` by `make verify`.",
             "PASS = the recomputed value equals the printed one; FAIL = it does not (the note says why).",
             "Every value is derived from the nine experimental runs in `data/`.", "",
             ", ".join(f"{s} {n[s]}" for s in STATUSES) + f"; total {len(rows)}"
             + (f"; DATA INTEGRITY MISMATCHES {len(integ)}" if integ else ""), ""]
    cur = None
    for r in rows:
        sec = r["location"].split(":")[0]
        if sec != cur:
            cur = sec
            parts += [f"## {sec}", ""]
        parts += [f"- **{r['id']}** — {r['status']}",
                  f"  - says: \"{plain(r['quote'])}\"" if r["quote"] else "  - says: (table row / body digest)",
                  f"  - printed: {plain(r['paper'])}",
                  f"  - recomputed: {_squash(r['computed'])}"]
        if r["status"] != "PASS" and r["note"]:
            parts.append(f"  - note: {_squash(r['note'])}")
        parts.append("")
    return "\n".join(parts) + "\n"


# ----------------------------------------------------------------------- ordering
def paper_file_order():
    """{rel: rank} in the order the paper includes its files (core.paper_files:
    main.tex, then each \\input of its ACTIVE text, recursively)."""
    return {rel: i for i, rel in enumerate(C.paper_files())}


def loc_key(loc, file_rank):
    m = re.match(r"^(.*?):(\d+)?(?:-+\d+)?\??$", loc.strip())
    if not m:
        return (10**6, loc, 10**9)
    rel, line = m.group(1), m.group(2)
    rank = file_rank.get(rel, 10**5 + (0 if rel.startswith("sections/") else 1))
    return (rank, rel, int(line) if line else 10**9)


# ------------------------------------------------------------------------ report
def _cell(s, width=None):
    s = _squash(s).replace("|", "\\|")
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


def _rel(p):
    try:
        return str(Path(p).resolve().relative_to(HERE))
    except ValueError:
        return Path(p).name


def render_report(rows, integ, full):
    n = counts(rows)
    parts = ["# Verification report", "",
             f"Data: `{_rel(C.DATA / 'trajectories_every_trial.csv')}` and "
             f"`{_rel(C.DATA / 'run_stage_metrics.csv')}`.", "",
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
    ap.add_argument("--full", action="store_true", help="developer view: ids, source locations and notes")
    ap.add_argument("--out", default=str(DEFAULT_OUT), help="markdown report path ('' = do not write)")
    a = ap.parse_args(argv)

    traj = C.load_trajectories()
    metrics = C.load_metrics()
    integ = integrity_check(traj, metrics)
    rows = load_claims(traj, metrics, only=set(a.module) if a.module else None)
    no_tex = not (C.ROOT / "main.tex").exists()
    snapshot_mode = no_tex and SNAPSHOT.exists()
    no_snapshot = no_tex and not snapshot_mode
    if snapshot_mode:
        rows = apply_snapshot(rows, partial=bool(a.module))
    elif no_snapshot:
        # No sources and no snapshot: the printed side cannot be read, so no
        # row can pass; keep the recomputed values for inspection.
        for r in rows:
            if not r["id"].endswith("(module error)"):
                r["paper"] = "n/a"
                r["status"] = "FAIL"
                r["note"] = "no printed value available (no paper sources and no claims_snapshot.json)"
    rank = paper_file_order()
    rows.sort(key=lambda r: (loc_key(r["location"], rank), r["id"]))

    if snapshot_mode:
        print("Reviewer mode: no LaTeX sources; the sentence and printed value of each claim come from\n"
              "claims_snapshot.json (frozen from the submitted version), the recomputed value from data/.\n")
    elif no_snapshot:
        print(f"NO-SNAPSHOT: no main.tex under {C.ROOT} and no claims_snapshot.json; nothing to compare\n"
              "             against, every row is FAIL. Set PAPER_ROOT=<paper source dir> or restore\n"
              "             claims_snapshot.json. Recomputed values follow.\n")
    full = a.full or os.environ.get("VERIFY_FULL") == "1"
    n = counts(rows)
    if full:   # developer view: ids, source locations, notes
        print(render_table(rows, True))
        print("\n" + ", ".join(f"{st} {n[st]}" for st in STATUSES)
              + f"; total {len(rows)}; data-integrity mismatches {len(integ)}")
    else:
        print(render_simple(rows, integ), end="")
    if integ:
        print("\nDATA INTEGRITY MISMATCHES:")
        for x in integ:
            print("  " + x)
    if a.out:
        out = Path(a.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("```\n" + render_simple(rows, integ) + "```\n", encoding="utf-8")
        print(f"\nreport written to {out}")
        if not no_tex and not a.module:
            print(f"snapshot of {write_snapshot(rows)} claims written to {SNAPSHOT.name}")
    if no_snapshot:
        return 2
    return 1 if (n["FAIL"] or integ) else 0


if __name__ == "__main__":
    sys.exit(main())

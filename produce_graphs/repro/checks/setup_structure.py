"""Experiment-structure and textual-count claims (module 'setup_structure').

Checks the paper's structural statements -- nine runs, K=4 stages, 36
run--stage observations, stage order, thresholds, date span, run schedule,
figure groupings, output-file layout -- against the shape of the raw CSVs
(TRAJ = generated/trajectories_every_trial.csv, MET =
generated/run_stage_metrics.csv), the per-stage experiment_date / day_label /
experiment_time_utc labels in MET (minute resolution), the files on disk, the text extracted from the committed figure PDFs, the panel grouping
declared in repro/generate.py, and, for purely textual counts, by counting
items in the CURRENT .tex sources (comment environments and %-lines are
stripped before counting).

Every claim's quoted text is re-located in the current .tex at the stated
file:line (a small window around it); a quote that is no longer there marks
the claim FAIL ('stale registry') regardless of the numeric outcome, so a
restructured paper cannot produce a silent PASS.  Textual-count claims find
their paragraph by anchor sentence, not by line number, and report the line
on which the anchor was found.

Nothing is hard-coded from the paper except the printed value being tested;
every 'computed' field is derived at call time from traj/metrics/files.
Pure Python (ast/csv/os/re/datetime/subprocess) -- no numpy/scipy.
"""
from __future__ import annotations

import ast
from pathlib import Path
import csv
import os
import re
import shutil
import subprocess
from datetime import date

import core as _core   # shared tex/timestamp helpers (single copy in core.py)

STAGES = ["IP", "M1", "VG", "EG"]
RAW_RUNS = list(range(4, 13))


# --------------------------------------------------------------------------
# helpers: paths, tex reading (delegated to core.py)
# --------------------------------------------------------------------------
def _root(C):
    """Project root (holds main.tex)."""
    return C.ROOT


def _tex_lines(C, rel):
    """Current (comment-stripped) lines of a .tex file, line numbers preserved."""
    return _core.tex_lines(rel)


def _find_anchor(lines, anchor):
    """1-based line number of the first (non-comment) line containing anchor,
    or None."""
    for k, ln in enumerate(lines, 1):
        if anchor in ln:
            return k
    return None


def _paragraph_around(lines, line_no):
    """Text of the blank-line-delimited paragraph containing 1-based line_no."""
    i = line_no - 1
    lo = i
    while lo > 0 and lines[lo - 1].strip() != "":
        lo -= 1
    hi = i
    while hi + 1 < len(lines) and lines[hi + 1].strip() != "":
        hi += 1
    return "\n".join(lines[lo:hi + 1])


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


def _quote_at(C, loc, quote, window=(1, 3)):
    """True if `quote` (whitespace-normalised) is found in the current .tex in
    the lines loc-window[0] .. loc+window[1]; False if not; None if the file
    cannot be read.  Comment blocks and %-lines are blanked first.  A long
    quote also matches on its first 40 characters (line-wrapping tolerance)."""
    try:
        rel, ln = loc.rsplit(":", 1)
        ln = int(ln)
    except ValueError:
        return None
    found = _core.quote_near(rel, ln, quote, before=window[0], after=window[1])
    if found or found is None:
        return found
    q = _norm(quote)
    return len(q) > 40 and bool(_core.quote_near(rel, ln, q[:40], before=window[0], after=window[1]))


# --------------------------------------------------------------------------
# helpers: structural facts from the CSVs
# --------------------------------------------------------------------------
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


def _pdf_text(path):
    """Raw pdftotext output (content-stream order), or None."""
    if not shutil.which("pdftotext") or not os.path.exists(path):
        return None
    try:
        # -raw keeps content-stream order, so each 'CW n' precedes its 'T=m';
        # -layout collapses the 4-column grid and drops annotations.
        return subprocess.run(["pdftotext", "-raw", str(path), "-"],
                              capture_output=True, text=True, timeout=60).stdout
    except Exception:
        return None


def _pdf_pairs(txt):
    """Multiset of (CW, T) annotation pairs from pdftotext output."""
    toks = re.findall(r"CW\s*(\d+)|T\s*=\s*(\d+)", txt)
    pairs, pending = [], None
    for cw, t in toks:
        if cw:
            pending = int(cw)
        elif pending is not None:
            pairs.append((pending, int(t)))
            pending = None
    return pairs


def _pdf_runs(txt):
    """Sorted set of run labels 'Rn' (as ints) found in pdftotext output."""
    return sorted({int(n) for n in re.findall(r"\bR(\d+)\b", txt)})


def _generate_groups(C):
    """The panel -> raw-run-id grouping declared in repro/generate.py
    (figs_runs_grid: `groups = {...}`), read via ast so matplotlib is not
    imported.  Returns dict or None."""
    p = Path(__file__).resolve().parent.parent / "generate.py"   # this toolkit's generator
    try:
        tree = ast.parse(open(p, encoding="utf-8").read())
    except Exception:
        return None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "figs_runs_grid":
            for sub in ast.walk(node):
                if isinstance(sub, ast.Assign) and any(
                        isinstance(t, ast.Name) and t.id == "groups"
                        for t in sub.targets):
                    try:
                        g = ast.literal_eval(sub.value)
                    except Exception:
                        return None
                    if isinstance(g, dict):
                        return {str(k): list(v) for k, v in g.items()}
    return None


def _figure_captions(app_lines):
    """{suffix: (caption_line, (lo, hi))} for each includegraphics of
    figures/runs_grid_<suffix>.pdf followed by a caption 'Runs~lo--hi'."""
    out = {}
    if app_lines is None:
        return out
    for k, ln in enumerate(app_lines, 1):
        m = re.search(r"runs_grid_([a-z])\.pdf", ln)
        if not m:
            continue
        suf = m.group(1)
        for j in range(k, min(len(app_lines), k + 6)):
            mm = re.search(r"\\caption\{.*?Runs~(\d+)--(\d+)", app_lines[j])
            if mm:
                out[suf] = (j + 1, (int(mm.group(1)), int(mm.group(2))))
                break
    return out


# --------------------------------------------------------------------------
def claims(C, traj, metrics):
    out = []
    root = _root(C)
    STALE = "quote not found at location (stale registry)"

    def add(cid, loc, quote, paper, computed, status, note=""):
        found = _quote_at(C, loc, quote)
        if found is False:
            status = "FAIL"
            note = (STALE + ("; " + note if note else ""))
        elif found is None and status == "PASS":
            status = "UNVERIFIABLE"
            note = ("quoted .tex file unreadable" + ("; " + note if note else ""))
        out.append({"id": cid, "location": loc, "quote": quote,
                    "paper": str(paper), "computed": str(computed),
                    "status": status, "note": note})

    def st(ok):
        return "PASS" if ok else "FAIL"

    nine_ok, nine_comp = _nine_runs_check(traj, metrics)
    four_ok, four_comp = _four_stages_check(traj, metrics)
    order_ok, order_bad = _stage_order_check(metrics)

    # ---- setup-001 ----
    add("setup-001", "main.tex:78", "Across nine end-to-end experiments",
        "nine", nine_comp, st(nine_ok),
        "len(set(run_id)) in TRAJ and MET; raw ids 4..12 = paper runs 1..9.")

    # ---- setup-002 ----
    add("setup-002", "sections/03-attack.tex:347",
        "Reconstruction therefore requires $K=4$ stages in both configurations",
        "4", four_comp, st(four_ok),
        "Distinct stage codes per run in MET and TRAJ must be exactly {IP,M1,VG,EG}.")

    # ---- setup-003 ----
    add("setup-003", "sections/03-attack.tex:348",
        "$r_{m_0},\\ldots,r_{m_3}$ denote the Introduction Point, the middle relay "
        "or layer-3 vanguard, the layer-2 vanguard, and the entry guard",
        "0..3 = IP,M1,VG,EG",
        "IP<M1<VG<EG by (experiment_date, experiment_time_utc) in all 9 runs" if order_ok
        else f"order violated in runs {order_bad}",
        st(order_ok),
        "Stage index order inferred from strictly increasing (experiment_date, HH:MM) of "
        "each stage's own MET row per run (minute resolution).")

    # ---- setup-004 ----
    add("setup-004", "sections/03-attack.tex:521",
        "number of stages $K$ ($K=4$ for a service-side introduction circuit)",
        "4", four_comp, st(four_ok), "Same test as setup-002.")

    # ---- setup-005 (textual, anchor-located) ----
    lines = _tex_lines(C, "sections/03-attack.tex")
    q5 = "reconstruction relies on three assumptions."
    if lines is None:
        add("setup-005", "sections/03-attack.tex:?", q5, "three", "n/a",
            "UNVERIFIABLE", "sections/03-attack.tex not found.")
    else:
        i5 = _find_anchor(lines, "relies on three assumptions")
        if i5 is None:
            out.append({"id": "setup-005", "location": "sections/03-attack.tex:?",
                        "quote": q5, "paper": "three", "computed": "n/a",
                        "status": "FAIL", "note": "quote not found in current .tex"})
        else:
            para = _paragraph_around(lines, i5)
            starters = [w for w in ("First", "Second", "Third", "Fourth", "Fifth")
                        if re.search(r"(^|[.\s])" + w + r",", para)]
            add("setup-005", f"sections/03-attack.tex:{i5}", q5, "three",
                f"{len(starters)} enumerated ({', '.join(starters)})",
                st(len(starters) == 3 and starters == ["First", "Second", "Third"]),
                "Textual count of 'First,/Second,/Third,' sentence starters in the "
                f"paragraph containing the anchor (found at line {i5}).")

    # ---- setup-006 ----
    add("setup-006", "sections/04-setup-and-evaluation.tex:267",
        "we ran Algorithm~\\ref{alg:reconstruction} nine times on the live Tor network",
        "nine", nine_comp, st(nine_ok), "Same test as setup-001.")

    # ---- setup-007 ----
    add("setup-007", "sections/04-setup-and-evaluation.tex:276",
        "we pinned the service's introduction circuit to four public Tor relays of ours",
        "four", four_comp, st(four_ok),
        "One monitored relay per stage; 4 stage codes per run. Relay identities "
        "(fingerprints) are not in the dataset, so only the count is checked.")

    # ---- setup-008 ----
    hdr = None
    try:
        hdr = next(csv.reader(open(C.DATA / "run_stage_metrics.csv")))
    except Exception:
        pass
    qs8 = (10, 3, 2)
    undefined8, nonmono8 = [], []
    for (rid, s), seq in sorted(traj.items()):
        t = [C.T_le(seq, q) for q in qs8]
        if any(v is None for v in t):
            undefined8.append((rid, s, dict(zip(qs8, t))))
        elif not (t[0] <= t[1] <= t[2]):
            nonmono8.append((rid, s, dict(zip(qs8, t))))
    ok8 = len(traj) == 36 and not undefined8 and not nonmono8
    add("setup-008", "sections/04-setup-and-evaluation.tex:304",
        "$T_{\\leq q}=\\min\\{j:|\\mathcal{I}_i^{(j)}|\\leq q\\}$ for $q\\in\\{10,3,2\\}$",
        "10, 3, 2",
        f"T<=q = first trial with |I_t|<=q from TRAJ: defined for "
        f"{len(traj) - len(undefined8)}/{len(traj)} run-stages and all three q, "
        f"T<=10 <= T<=3 <= T<=2 in {len(traj) - len(undefined8) - len(nonmono8)}/{len(traj)}",
        st(ok8),
        "T<=q is derived from trajectories_every_trial.csv alone (core.T_le); the check is "
        "that every one of the 36 run-stages reaches each threshold q in {10,3,2} and that "
        "the thresholds are ordered."
        + (f" undefined: {undefined8[:5]}" if undefined8 else "")
        + (f" non-monotone: {nonmono8[:5]}" if nonmono8 else ""))

    # ---- setup-009 (textual, from tab:impl-components + anchor paragraph) ----
    impl = _tex_lines(C, "sections/implementation.tex")
    comp_rows, n_on_relay = None, None
    if impl is not None:
        txt = "\n".join(impl)
        m = re.search(r"\\label\{tab:impl-components\}.*?\\begin\{tabular\}.*?\\midrule(.*?)\\bottomrule",
                      txt, re.S)
        if m:
            body = m.group(1)
            comp_rows = [r.strip() for r in re.split(r"\\\\", body) if r.strip()]
            comp_rows = [re.split(r"&", r)[0].strip() for r in comp_rows]
            # the onion-service daemon row is the one on the service host
            n_on_relay = sum(1 for r in comp_rows
                             if not re.search(r"onion-service daemon", r, re.I))
    q9 = "The monitored relay runs four processes: (i)~a capture process"
    ev = _tex_lines(C, "sections/04-setup-and-evaluation.tex")
    i9 = _find_anchor(ev, "runs four processes") if ev else None
    if comp_rows is None:
        add("setup-009", f"sections/04-setup-and-evaluation.tex:{i9 or '?'}", q9,
            "four", "n/a", "UNVERIFIABLE", "tab:impl-components not parseable.")
    elif i9 is None:
        out.append({"id": "setup-009", "location": "sections/04-setup-and-evaluation.tex:?",
                    "quote": q9, "paper": "four", "computed": "n/a",
                    "status": "FAIL", "note": "quote not found in current .tex"})
    else:
        para = _paragraph_around(ev, i9)
        romans = re.findall(r"\((i|ii|iii|iv|v|vi)\)~?", para)
        n_rom = len(set(romans))
        ok9 = n_on_relay == 4 and n_rom == 4
        add("setup-009", f"sections/04-setup-and-evaluation.tex:{i9}", q9, "four",
            f"{len(comp_rows)} component rows in tab:impl-components, {n_on_relay} on "
            f"the monitored relay; {n_rom} enumerated processes (i)..({romans[-1] if romans else '-'}) in the paragraph",
            st(ok9),
            "Textual consistency: table rows minus the Onion-service daemon row "
            f"(service host) and the (i)-(iv) enumeration in the paragraph at line {i9}.")

    # ---- setup-010 ----
    add("setup-010", "sections/04-setup-and-evaluation.tex:366",
        "where $N$ is the total number of iterations across the four stages",
        "four", four_comp, st(four_ok), "Same test as setup-002.")

    # ---- setup-011 (nine runs + table rows) ----
    n_rows_e2e = None
    if ev is not None:
        txt = "\n".join(ev)
        m = re.search(r"End-to-end reconstruction cost across the nine experiments.*?"
                      r"\\midrule(.*?)\\midrule", txt, re.S)
        if m:
            n_rows_e2e = len(re.findall(r"^\s*(\d+)\s*&", m.group(1), re.M))
    ok11 = nine_ok and n_rows_e2e == 9
    add("setup-011", "sections/04-setup-and-evaluation.tex:416",
        "End-to-end reconstruction cost across the nine experiments.",
        "nine", f"{nine_comp}; {n_rows_e2e} data rows in tab:end_to_end", st(ok11),
        "Same test as setup-001 plus count of numbered data rows between the "
        "\\midrule markers of the end-to-end table.")

    # ---- setup-012 ----
    add("setup-012", "sections/04-setup-and-evaluation.tex:419",
        "Total is the sum $N$ across the four stages.",
        "four", four_comp, st(four_ok), "Same test as setup-002.")

    # ---- setup-013 ----
    n_pairs = len(set(traj.keys()))
    n_met = len(metrics)
    ok13 = n_pairs == 36 and n_met == 36
    add("setup-013", "sections/05-discussion.tex:48",
        "Across the $36$ stages in our empirical evaluation",
        "36", f"{n_pairs} distinct (run,stage) in TRAJ; {n_met} rows in MET",
        st(ok13), "9 runs x 4 stages.")

    # ---- setup-014 ----
    add("setup-014", "sections/07-conclusion.tex:29",
        "We evaluated the attack in nine end-to-end experiments against a",
        "nine", nine_comp, st(nine_ok), "Same test as setup-001.")

    # ---- setup-015 / 016 (textual) ----
    if comp_rows is None:
        for cid, loc, q, pv in (
            ("setup-015", "sections/implementation.tex:12",
             "Four of the five components (Table~\\ref{tab:impl-components}) run on "
             "the monitored relay's host", "four of five"),
            ("setup-016", "sections/implementation.tex:15",
             "the fifth is the modified onion-service daemon on the service host. "
             "The four move with the observation", "fifth; four")):
            add(cid, loc, q, pv, "n/a", "UNVERIFIABLE",
                "tab:impl-components not parseable.")
    else:
        ok15 = len(comp_rows) == 5 and n_on_relay == 4
        add("setup-015", "sections/implementation.tex:12",
            "Four of the five components (Table~\\ref{tab:impl-components}) run on "
            "the monitored relay's host", "four of five",
            f"{n_on_relay} of {len(comp_rows)} ({', '.join(comp_rows)})", st(ok15),
            "Rows of tab:impl-components; all but the Onion-service daemon run on "
            "the monitored relay.")
        idx = [i for i, r in enumerate(comp_rows, 1)
               if re.search(r"onion-service daemon", r, re.I)]
        ok16 = len(comp_rows) == 5 and idx == [5] and n_on_relay == 4
        add("setup-016", "sections/implementation.tex:15",
            "the fifth is the modified onion-service daemon on the service host. "
            "The four move with the observation", "fifth; four",
            f"Onion-service daemon is row {idx[0] if idx else '?'} of {len(comp_rows)}; "
            f"{n_on_relay} remaining", st(ok16),
            "Textual: position of the Onion-service daemon row in tab:impl-components.")

    # ---- setup-017..019 ----
    for cid, ln, q in (("setup-017", 43, "Pins the target introduction circuit to the four relays we operate."),
                       ("setup-018", 60, "}_{\\textnormal{four public relays we operate}}."),
                       ("setup-019", 64, "Operating the four relays ourselves substitutes for the visibility")):
        add(cid, f"sections/implementation.tex:{ln}", q, "four", four_comp,
            st(four_ok), "One operated relay per stage; same test as setup-002.")

    # ---- setup-020 ----
    add("setup-020", "sections/implementation.tex:67",
        "The four monitored-relay stages walk this circuit in reverse",
        "four (IP->M1->VG->EG)",
        four_comp + ("; stage starts ordered IP<M1<VG<EG in all runs" if order_ok
                     else f"; ORDER VIOLATION {order_bad}"),
        st(four_ok and order_ok),
        "setup-002 plus setup-003 ordering check (reverse of the circuit "
        "guard->vanguard->middle->IP).")

    # ---- setup-021 (files) ----
    gen = C.DATA
    tp, mp = gen / "trajectories_every_trial.csv", gen / "run_stage_metrics.csv"
    csvs = sorted(p.name for p in gen.glob("*.csv")) if gen.exists() else []
    thdr = next(csv.reader(open(tp))) if tp.exists() else None
    need_met = ["run_id", "stage_code", "experiment_date", "day_label",
                "experiment_time_utc", "consensus_weight"]
    missing = [c for c in need_met if hdr is None or c not in hdr]
    extra = [c for c in (hdr or []) if c not in need_met]
    ok21 = (tp.exists() and mp.exists() and len(csvs) == 2
            and thdr == ["run_id", "stage", "trial", "intersection_size"]
            and hdr == need_met)
    add("setup-021", "sections/implementation.tex:144",
        "one CSV records the run, stage, iteration, and intersection cardinality "
        "per observation, a second records stage-level metadata",
        "2 CSVs",
        f"{len(csvs)} CSV(s) in data/ ({', '.join(csvs)}); TRAJ header={thdr}; "
        f"MET header={hdr}" + (f" MISSING {missing}" if missing else "")
        + (f" UNEXPECTED {extra}" if extra else ""),
        st(ok21),
        "File existence, exact TRAJ header, exact MET header and no other CSV in data/. "
        "The released run_stage_metrics.csv is the reduced stage-level metadata file: per "
        "run and stage it holds only the run/stage labels (experiment_date, day_label, "
        "experiment_time_utc) and the monitored relay's consensus weight; every "
        "convergence quantity is derived from the trajectories CSV.")

    # ---- setup-022 (textual) ----
    if impl is None:
        add("setup-022", "sections/implementation.tex:152",
            "We considered each of the TRSB's nine research-safety principles as follows.",
            "nine", "n/a", "UNVERIFIABLE", "implementation.tex not found.")
    else:
        txt = "\n".join(impl)
        m = re.search(r"nine research-safety principles as follows\..*?"
                      r"\\begin\{enumerate\}(.*?)\\end\{enumerate\}", txt, re.S)
        n_items = len(re.findall(r"\\item\b", m.group(1))) if m else None
        add("setup-022", "sections/implementation.tex:152",
            "We considered each of the TRSB's nine research-safety principles as follows.",
            "nine", f"{n_items} \\item entries in the enumerate", st(n_items == 9),
            "Textual: \\item count in the enumerate following the quoted sentence. The "
            "TRSB page itself lists nine considerations (external, not re-fetched).")

    # ---- setup-023 (36 + appendix rows) ----
    app = _tex_lines(C, "sections/appendix_results.tex")
    n_app_rows = None
    app_labels = []
    if app is not None:
        txt = "\n".join(app)
        m = re.search(r"\\label\{tab:run-stage-thresholds\}.*?\\midrule(.*?)\\bottomrule",
                      txt, re.S)
        if m:
            body = m.group(1)
            n_app_rows = len(re.findall(r"&\s*(Intro\. Point|Middle 1|Vanguard|Entry Guard)\s*&", body))
            app_labels = re.findall(r"R(\d+)\s*\(Day\s*(\d+),\s*(\d{2}:\d{2})\)", body)
    add("setup-023", "sections/appendix_results.tex:5",
        "All $36$ individual run--stage observations are presented in",
        "36", f"{n_pairs} (run,stage) in TRAJ; {n_met} MET rows; {n_app_rows} rows in "
        f"tab:run-stage-thresholds", st(ok13 and n_app_rows == 36),
        "Same as setup-013 plus a count of stage rows in the appendix table.")

    # ---- figure grouping inputs (shared by setup-024/028/029/030/031) ----
    figs = Path(os.environ.get("REPRO_FIGS") or
                (root / "figures" if (root / "figures").is_dir()
                 else Path(__file__).resolve().parent.parent / "out" / "figures"))
    groups = _generate_groups(C)                # {suffix: [raw run ids]} from generate.py
    captions = _figure_captions(app)            # {suffix: (line, (lo, hi))} from the .tex
    pdf_txt = {s: _pdf_text(figs / f"runs_grid_{s}.pdf") for s in "abc"}
    tr_ids, _ = _run_ids(traj, metrics)

    # ---- setup-024 (figure files + panel structure) ----
    present = [s for s in "abc" if (figs / f"runs_grid_{s}.pdf").exists()]
    if groups is None:
        g_comp, g_ok = "generate.py figs_runs_grid groups not parseable", False
    else:
        sizes = [len(v) for v in groups.values()]
        covered = sorted(r for v in groups.values() for r in v)
        g_comp = (f"generate.py groups {sum(sizes)} runs into {len(groups)} panels of "
                  f"{'/'.join(map(str, sizes))} (suffixes {','.join(sorted(groups))})")
        g_ok = sorted(groups) == ["a", "b", "c"] and covered == tr_ids
    ref_span = None
    if app is not None:
        mm = re.search(r"Figures~\\ref\{fig:runs-grid-([a-z])\}--\\ref\{fig:runs-grid-([a-z])\}",
                       "\n".join(app))
        if mm:
            ref_span = (mm.group(1), mm.group(2))
    add("setup-024", "sections/appendix_results.tex:7",
        "every run in Figures~\\ref{fig:runs-grid-a}--\\ref{fig:runs-grid-c}.",
        "3 figures (a--c)",
        f"{len(present)} files present (runs_grid_{{{','.join(present)}}}.pdf); {g_comp}; "
        f".tex reference span {ref_span}",
        st(present == ["a", "b", "c"] and g_ok and ref_span == ("a", "c") and nine_ok),
        "File existence for figures/runs_grid_{a,b,c}.pdf; panel grouping read (ast) "
        "from repro/generate.py figs_runs_grid and must cover every TRAJ run once.")

    # ---- setup-025 ----
    _, mr = _run_ids(traj, metrics)
    paper_ids = sorted(C.PAPER_RUN.get(r, r - 3) for r in mr)
    ok25 = len(mr) == 9 and paper_ids == list(range(1, 10))
    add("setup-025", "sections/appendix_results.tex:13",
        "Per-run, per-stage measurements for nine end-to-end runs (IDs~1--9)",
        "nine; 1--9",
        f"{len(mr)} runs; paper ids {paper_ids[0]}..{paper_ids[-1]} (raw {mr[0]}..{mr[-1]})"
        if mr else "no runs in MET",
        st(ok25), "raw run_id - 3 must cover exactly 1..9.")

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
        "stages may begin on a later day, e.g. raw run 9 EG on Day 3).")

    # ---- setup-028 / 030 / 031 (figure groupings, from PDF text + generate.py) ----
    ids = {"a": "setup-028", "b": "setup-030", "c": "setup-031"}
    ts_sets, _ = _stage_sets(traj, metrics)
    for suf in "abc":
        cap = captions.get(suf)
        cap_line, cap_range = (cap if cap else (None, None))
        lab = f"{cap_range[0]}--{cap_range[1]}" if cap_range else "?"
        loc = f"sections/appendix_results.tex:{cap_line or '?'}"
        quote = f"Intersection degradation for Runs~{lab} across the four reconstruction"
        txt = pdf_txt[suf]
        if cap is None:
            out.append({"id": ids[suf], "location": loc, "quote": quote,
                        "paper": "?", "computed": "n/a", "status": "FAIL",
                        "note": f"caption for runs_grid_{suf}.pdf with 'Runs~lo--hi' "
                                "not found in current appendix_results.tex"})
            continue
        want = list(range(cap_range[0], cap_range[1] + 1))
        if txt is None:
            add(ids[suf], loc, quote, f"{lab}; four", "n/a", "UNVERIFIABLE",
                f"figures/runs_grid_{suf}.pdf missing or pdftotext unavailable.")
            continue
        pdf_r = _pdf_runs(txt)
        g_raw = groups.get(suf) if groups else None
        g_paper = sorted(C.PAPER_RUN.get(r, r - 3) for r in g_raw) if g_raw else None
        nst = [len(ts_sets.get(r, ())) for r in (g_raw or [])]
        n_titles = len(re.findall(r"IntroductionPoint|Middle1|Vanguard|EntryGuard", txt))
        okg = (pdf_r == want and g_paper == want and nst == [4] * len(want)
               and n_titles == 4)
        add(ids[suf], loc, quote, f"{lab}; four",
            f"run labels in runs_grid_{suf}.pdf: R{pdf_r}; generate.py panel {suf} raw "
            f"{g_raw} -> paper {g_paper}; stages per run in TRAJ {nst}; "
            f"{n_titles} stage column titles in PDF",
            st(okg),
            "Run labels 'Rn' read with pdftotext from the committed PDF and the panel "
            "grouping parsed (ast) from repro/generate.py figs_runs_grid, both compared "
            "with the caption range parsed from the .tex; each grouped run has 4 stage "
            "codes in TRAJ and the PDF carries 4 stage column titles.")

    # ---- setup-029 (panel annotations = table values) ----
    if groups is None:
        add("setup-029", "sections/appendix_results.tex:89",
            "Each panel reports stage-start consensus weight (CW) and singleton "
            "convergence $T_{\\mathrm{conv}}$.",
            "36 (CW, T_conv) panel annotations", "n/a", "UNVERIFIABLE",
            "generate.py figs_runs_grid groups not parseable.")
    else:
        missing29 = [(rid, s) for rids in groups.values() for rid in rids
                     for s in STAGES if (rid, s) not in metrics or (rid, s) not in traj]
        expected = {suf: sorted((int(metrics[(rid, s)]["consensus_weight"]),
                                 C.T_conv(traj[(rid, s)]))
                                for rid in rids for s in STAGES
                                if (rid, s) in metrics and (rid, s) in traj)
                    for suf, rids in groups.items()}
        n_exp = sum(len(v) for v in expected.values())
        got_all, ok29, detail = 0, not missing29, []
        unverifiable = False
        for suf in sorted(groups):
            txt = pdf_txt.get(suf)
            if txt is None:
                unverifiable = True
                detail.append(f"{suf}: pdftotext/file unavailable")
                continue
            pairs = _pdf_pairs(txt)
            got_all += len(pairs)
            same = sorted(pairs) == expected[suf]
            ok29 &= same
            detail.append(f"{suf}: {len(pairs)} (CW,T) pairs {'match' if same else 'DIFFER'}")
        add("setup-029", "sections/appendix_results.tex:89",
            "Each panel reports stage-start consensus weight (CW) and singleton "
            "convergence $T_{\\mathrm{conv}}$.",
            "36 (CW, T_conv) panel annotations",
            f"{got_all}/{n_exp} annotation pairs read from committed PDFs; " + "; ".join(detail)
            + (f"; run-stages missing from TRAJ/MET: {missing29}" if missing29 else ""),
            "UNVERIFIABLE" if unverifiable else st(ok29 and got_all == n_exp == 36),
            "pdftotext on figures/runs_grid_{a,b,c}.pdf; 'CW n / T=m' pairs compared as "
            "multisets with MET.consensus_weight and T_conv recomputed from TRAJ over "
            "the generate.py panel groups. ASSUMPTION: committed PDFs were produced by "
            "the current generate.py (figures are not regenerated here).")

    # ---- setup-032 (textual, anchor-located) ----
    disc = _tex_lines(C, "sections/05-discussion.tex")
    q32 = "Our evaluation has two main limitations."
    if disc is None:
        add("setup-032", "sections/05-discussion.tex:?", q32, "2", "n/a",
            "UNVERIFIABLE", "05-discussion.tex not found.")
    else:
        i32 = _find_anchor(disc, "two main limitations")
        if i32 is None:
            out.append({"id": "setup-032", "location": "sections/05-discussion.tex:?",
                        "quote": q32, "paper": "2", "computed": "n/a",
                        "status": "FAIL", "note": "quote not found in current .tex"})
        else:
            para = _paragraph_around(disc, i32)
            starters = [w for w in ("First", "Second", "Third", "Fourth")
                        if re.search(r"(^|[.\s])" + w + r",", para)]
            add("setup-032", f"sections/05-discussion.tex:{i32}", q32, "2",
                f"{len(starters)} enumerated ({', '.join(starters)})",
                st(starters == ["First", "Second"]),
                "Textual count of 'First,'/'Second,' sentence starters (and absence of "
                f"'Third,') in the Limitations paragraph containing the anchor (line {i32}).")

    return out

"""Convergence-behaviour claims (module 'convergence').

Success and convergence statistics recomputed from the raw per-trial
intersection trajectories (generated/trajectories_every_trial.csv); the
metrics CSV (generated/run_stage_metrics.csv) contributes only the consensus
weight used to group CW-matched stages.

Shorthand used throughout:
  seq(r,s)   = intersection_size of TRAJ rows (run_id=r, stage=s) ordered by
               trial; trial 1 = |A1| (index 0 of the Python list).
  T<=q(r,s)  = first trial t with seq[t] <= q          (core.T_le)
  Tconv(r,s) = T<=1(r,s)                                (core.T_conv; None if
               the stage never reaches a singleton = NON-CONVERGED)
  N(r)       = sum over stages of len(seq(r,s))         (== sum of Tconv when
               every stage converged and no trials were recorded afterwards)
  paper run p = raw run r - 3                           (core.PAPER_RUN)

Robustness: a stage whose trajectory never reaches |I| = 1 makes core.T_conv
return None. The module treats such a stage as non-converged (the success
claims conv-001/002/005/006/024 then FAIL and name the offending (run,stage)),
uses len(seq) for run totals, and looks up trial t with at(seq, t) which holds
|I| = 1 after convergence. Every claim is additionally computed inside its own
try/except so a malformed stage yields one FAIL row instead of suppressing the
other rows.

Every computed value is derived from the CSVs at call time; nothing is
hard-coded. Where the paper's wording cannot be reproduced from the CSVs alone
(e.g. "correct successor") the note says which part is checked. Every record
is PASS or FAIL; without the paper sources the numeric status is kept (the
printed values are hard-coded here) and the note says the quote was not
verified.
"""
from __future__ import annotations

import statistics as st
import re
import traceback

import core as _core   # shared tex helpers (single copy in core.py)


# ----------------------------------------------------------------------------
# helpers (pure Python, no numpy/scipy)
# ----------------------------------------------------------------------------
def _seq(traj, r, s):
    return traj[(r, s)]


def _at(seq, t):
    """|I| at 1-based trial t. A stage that has already converged holds
    |I| = 1 thereafter, so t beyond the recorded length returns seq[-1]."""
    if not seq:
        raise ValueError("empty trajectory")
    return seq[t - 1] if t <= len(seq) else seq[-1]


def _plateau_len(seq):
    """Number of consecutive trials, ending at the penultimate trial, whose
    value equals seq[-2] (the penultimate trial itself is counted)."""
    if len(seq) < 2:
        return 0
    v = seq[-2]
    n, i = 0, len(seq) - 2
    while i >= 0 and seq[i] == v:
        n += 1
        i -= 1
    return n


def _first_index(seq, value):
    """1-based trial index of the first occurrence of `value`, else None."""
    for i, v in enumerate(seq, start=1):
        if v == value:
            return i
    return None


def _met_int(metrics, key, col):
    v = metrics[key].get(col, "")
    if v is None:
        return None
    v = str(v).strip()
    return int(float(v)) if v != "" else None


def _status(ok):
    return "PASS" if ok else "FAIL"


def _mk(cid, loc, quote, paper, computed, status, note="", relocate=True):
    """Claim record. With relocate=True the quote is re-located in the CURRENT
    paper (core.relocate: registered file:line, then the whole file, then every
    active file) so the reported location is where it is printed now; a quote
    printed nowhere marks the claim FAIL (stale registry)."""
    if relocate and quote:
        st, where, mv = _core.relocate(loc, quote)
        if st == "found":
            loc = where
            if mv:
                note = f"[{mv}] " + note
        elif st == "absent":
            loc, status = where, "FAIL"
            note = f"stale registry: {mv}. " + note
        else:                       # nofile: keep the numeric status; quote not verified
            note = f"{mv}; quote not verified. " + note
    return {"id": cid, "location": loc, "quote": quote, "paper": str(paper),
            "computed": str(computed), "status": status, "note": note}


def _emit(out, cid, loc, quote, paper, fn, note=""):
    """Run fn() -> (computed, status_or_bool[, extra_note]) inside try/except
    so one broken stage never suppresses the other claims."""
    try:
        res = fn()
        computed, status = res[0], res[1]
        extra = res[2] if len(res) > 2 else ""
        if isinstance(status, bool):
            status = _status(status)
        out.append(_mk(cid, loc, quote, paper, computed, status,
                       note + (" " + extra if extra else "")))
    except Exception as e:  # noqa: BLE001 - deliberately broad
        tb = traceback.format_exc().strip().splitlines()[-1]
        out.append(_mk(cid, loc, quote, paper,
                       f"EXCEPTION while computing: {type(e).__name__}: {e}",
                       "FAIL", note + f" [computation raised: {tb}]"))


# ----------------------------------------------------------------------------
def claims(C, traj, metrics):
    out = []
    keys = [(r, s) for r in C.RUN_IDS for s in C.STAGES]

    # ---- shared derived quantities (None / short-sequence tolerant) ------
    def tconv(k):
        return C.T_conv(traj[k])

    nonconverged = [k for k in keys if tconv(k) is None]
    n_stages_singleton = sum(1 for k in keys if traj[k] and traj[k][-1] == 1)
    n_runs_ok = sum(1 for r in C.RUN_IDS
                    if all(tconv((r, s)) is not None and traj[(r, s)][-1] == 1
                           for s in C.STAGES))
    all_runs_ok = (not nonconverged and n_runs_ok == len(C.RUN_IDS))
    all_runs_computed = (f"{n_runs_ok} of {len(C.RUN_IDS)} runs converged at all "
                         f"4 stages ({len(keys) - len(nonconverged)}/{len(keys)} stages "
                         f"reach |I|=1)")
    if nonconverged:
        all_runs_computed += f"; NON-CONVERGED stages (no |I|=1 trial): {nonconverged}"

    # conv-007: per-run totals (len(seq); equals sum Tconv when all converged)
    N = {r: sum(len(traj[(r, s)]) for s in C.STAGES) for r in C.RUN_IDS}

    # conv-008 / conv-009: T<=10 over 36 stages
    t10 = [C.T_le(traj[k], 10) for k in keys]

    # conv-012..015: CW-matched stage groups
    def _tc_str(k):
        t = tconv(k)
        return "None" if t is None else str(t)

    vg1200 = sorted((k[0], _tc_str(k)) for k in keys
                    if metrics[k]["stage_code"] == "VG"
                    and _met_int(metrics, k, "consensus_weight") == 1200)
    m4800 = sorted((k[0], _tc_str(k)) for k in keys
                   if metrics[k]["stage_code"] == "M1"
                   and _met_int(metrics, k, "consensus_weight") == 4800)

    # conv-020 / conv-021: abrupt collapses and plateaus
    abrupt = [k for k in keys
              if len(traj[k]) >= 2 and traj[k][-2] >= 3 and traj[k][-1] == 1]
    plateaus = {k: _plateau_len(traj[k]) for k in abrupt}

    # conv-016..019: paper Runs 1, 4, 6 = raw 4, 7, 9
    raw_runs = [p + 3 for p in (1, 4, 6)]

    # ---------------------------------------------------------------------
    # conv-001
    _emit(out, "conv-001", "main.tex:79",
          "the attack reconstructs the complete Tor\ncircuit in every run",
          "every run (9 of 9)",
          lambda: (all_runs_computed, all_runs_ok),
          "Run converged iff every stage's final trial is a singleton and a "
          "singleton trial exists.")

    # conv-002
    _emit(out, "conv-002", "sections/01-introduction.tex:138",
          "complete target path in all nine experiments (Section~\\ref{sec:eval}).",
          "nine (all nine)",
          lambda: (all_runs_computed, all_runs_ok),
          "Same computation as conv-001.")

    # conv-005
    _emit(out, "conv-005", "sections/04-setup-and-evaluation.tex:352",
          "Across the nine end-to-end experiments, the attack successfully\n"
          "reconstructed the complete introduction path in every run.",
          "nine (9 of 9 succeeded)",
          lambda: (all_runs_computed, all_runs_ok),
          "Same computation as conv-001.")

    # conv-006
    def _c006():
        comp = f"{n_stages_singleton} of {len(keys)} stages end at |I|=1"
        if nonconverged:
            comp += f"; non-converged: {nonconverged}"
        return comp, (n_stages_singleton == 36 and not nonconverged)
    _emit(out, "conv-006", "sections/04-setup-and-evaluation.tex:353",
          "All $36$ stages\nconverged to the correct successor.",
          "36", _c006,
          "Count of stages converging to a singleton is verified. The 'correct "
          "successor' part cannot be checked from the CSVs (pseudonyms and relay "
          "identities were never written to disk); it rests on the pinned-path "
          "ground truth described in the text.")

    # conv-007
    def _c007():
        N_med = st.median(N.values())
        N_min, N_max = min(N.values()), max(N.values())
        n_str = ", ".join(f"R{C.PAPER_RUN[r]}(raw {r})={N[r]}" for r in C.RUN_IDS)
        comp = f"median={N_med:g}; min={N_min}; max={N_max} [N per run: {n_str}]"
        ok = round(N_med) == 260 and N_min == 101 and N_max == 770
        if nonconverged:
            comp += f"; totals include NON-CONVERGED stages {nonconverged}"
            ok = False
        return comp, ok
    _emit(out, "conv-007", "sections/04-setup-and-evaluation.tex:355",
          "median of $260$ iterations, ranging from $101$ to $770$ iterations across\nruns",
          "260; 101; 770", _c007,
          "N(r) = sum of Tconv (= recorded trials) over the four stages; "
          "statistics.median over 9 runs.")

    # conv-008
    def _c008():
        vals = [x for x in t10 if x is not None]
        med = st.median(vals)
        comp = f"median(T<=10 over {len(vals)} stages) = {med:g}"
        if len(vals) != len(t10):
            comp += f"; {len(t10) - len(vals)} stages never reached |I|<=10 (excluded)"
        return comp, (round(med) == 3 and len(vals) == len(t10))
    _emit(out, "conv-008", "sections/05-discussion.tex:49",
          "the median iteration at\nwhich $|\\mathcal{I}_i^{(j)}|\\leq10$ was three",
          "3", _c008,
          "Threshold q=10 is the definition used by the same sentence.")

    # conv-009
    def _c009():
        w5 = sum(1 for x in t10 if x is not None and x <= 5)
        pct = 100.0 * w5 / len(t10)
        return (f"{w5}/{len(t10)} = {pct:.2f}% -> {round(pct)}%", round(pct) == 64)
    _emit(out, "conv-009", "sections/05-discussion.tex:49",
          "and $64\\%$ of stages reached this threshold within five iterations",
          "64%", _c009,
          "Share of stages with T<=10 <= 5, rounded to integer percent. "
          "Cutoff 5 is the definition in the same sentence.")

    # conv-010 / conv-011: per-stage reduction (ratio of per-stage medians)
    def _reduction(t):
        R, R_alt = {}, {}
        for s in C.STAGES:
            m1 = st.median(_at(_seq(traj, r, s), 1) for r in C.RUN_IDS)
            mt = st.median(_at(_seq(traj, r, s), t) for r in C.RUN_IDS)
            R[s] = 100.0 * (1 - mt / m1)
            R_alt[s] = st.median(
                100.0 * (1 - _at(_seq(traj, r, s), t) / _at(_seq(traj, r, s), 1))
                for r in C.RUN_IDS)
        return R, R_alt

    def _c010():
        R2, R2_alt = _reduction(2)
        r_str = ", ".join(f"{s} {R2[s]:.1f}" for s in C.STAGES)
        alt = ", ".join(f"{s} {R2_alt[s]:.1f}" for s in C.STAGES)
        lo, hi = round(min(R2.values())), round(max(R2.values()))
        return (f"{lo}--{hi}% [per stage: {r_str}]", (lo, hi) == (72, 87),
                f"The alternative reading (median of per-run ratios) gives {alt} "
                "and does NOT reproduce the printed range.")
    _emit(out, "conv-010", "sections/05-discussion.tex:51",
          "candidate set shrank by $72$--$87\\%$ after the first intersection",
          "72--87%", _c010,
          "ASSUMPTION: 'per-stage medians' read as RATIO OF MEDIANS, "
          "R2(s)=100*(1 - median_r(|I_2|) / median_r(|I_1|)), rounded to nearest "
          "integer; |I_t| via at(seq,t) (=1 after convergence).")

    def _c011():
        R3, R3_alt = _reduction(3)
        r_str = ", ".join(f"{s} {R3[s]:.1f}" for s in C.STAGES)
        alt = ", ".join(f"{s} {R3_alt[s]:.1f}" for s in C.STAGES)
        lo, hi = round(min(R3.values())), round(max(R3.values()))
        return (f"{lo}--{hi}% [per stage: {r_str}]", (lo, hi) == (85, 96),
                f"Median of per-run ratios gives {alt} and does not reproduce.")
    _emit(out, "conv-011", "sections/05-discussion.tex:52",
          "and by $85$--$96\\%$ by the third iteration, depending on the stage",
          "85--96%", _c011,
          "ASSUMPTION: ratio of medians as in conv-010, 'third iteration' = trial "
          "index 3 (|I_3|).")

    # conv-012 / conv-014: how many CW-matched stages the live sentence claims.
    # Accepts "the X <Stage> stages at CW $cw$" (X = all of them) and
    # "X of the Y <Stage> stages at CW $cw$" (Y = all of them); Y/X is compared
    # with the number of such stages in the data.
    _WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
              "seven": 7, "eight": 8, "nine": 9}

    def _stated_count(stage_word, cw):
        """The live sentence is searched for in every active .tex file
        (core.search_paper), the Discussion first; it currently lives in the
        evaluation section."""
        rel = "sections/05-discussion.tex"
        hit = _core.search_paper(r"(\w+) of the (\w+) %s stages at CW \$%d\$" % (stage_word, cw), rel)
        if hit:
            frel, ln, m = hit
            phrase, total = m.group(0), _WORDS.get(m.group(2).lower())
        else:
            hit = _core.search_paper(r"the (\w+) %s stages at CW \$%d\$" % (stage_word, cw), rel)
            if not hit:
                return None, None, f"{rel}:?"
            frel, ln, m = hit
            phrase, total = m.group(0), _WORDS.get(m.group(1).lower())
        return phrase, total, f"{frel}:{ln}"

    def _cw_claim(cid, stage_word, cw, group, other_id):
        phrase, total, loc = _stated_count(stage_word, cw)
        listing = ", ".join(f"raw {r} (R{C.PAPER_RUN[r]}): Tconv={t}" for r, t in group)
        computed = f"{len(group)} {stage_word} stages at CW {cw} in MET [{listing}]"
        if phrase is None:
            out.append(_mk(cid, loc, f"{stage_word} stages at CW ${cw}$", "n/a", computed,
                           "FAIL", ("paper sources not available" if not _core.paper_present() else
                                    "sentence about CW-matched stages not found in the live text"),
                           relocate=False))
            return
        status = _status(total == len(group))
        moved = ("" if loc.startswith("sections/05-discussion.tex:")
                 else "[moved from sections/05-discussion.tex] ")
        out.append(_mk(cid, loc, phrase, f"{cw}; {total}", computed, status,
                       f"{moved}the sentence must count ALL {stage_word} stages at CW {cw} in the "
                       f"data ('X of the Y ...' counts Y). The listed Tconv values are checked by "
                       f"{other_id}.", relocate=False))

    _cw_claim("conv-012", "Vanguard", 1200, vg1200, "conv-013")

    # conv-013
    def _c013():
        want = {6: 12, 8: 142, 9: 251}
        got = {r: tconv((r, "VG")) for r in want}
        ok = all(got[r] is not None and got[r] == want[r] for r in want)
        return (", ".join(f"{got[r]}" for r in (6, 8, 9)) +
                " [Tconv(VG) of raw 6, 8, 9 = R3, R5, R6]", ok)
    _emit(out, "conv-013", "sections/05-discussion.tex:75",
          "converged after $12$, $142$, and $251$ iterations",
          "12, 142, 251", _c013,
          "Tconv of the VG stages of paper runs 3, 5, 6 (raw 6, 8, 9). See "
          "conv-012 for the omitted CW-1200 VG stages.")

    _cw_claim("conv-014", "Middle", 4800, m4800, "conv-015")

    # conv-015
    def _c015():
        want = {12: 4, 11: 53}
        got = {r: tconv((r, "M1")) for r in want}
        ok = all(got[r] is not None and got[r] == want[r] for r in want)
        return (f"{got[12]}, {got[11]} [Tconv(M1) of raw 12, 11 = R9, R8]", ok)
    _emit(out, "conv-015", "sections/05-discussion.tex:76",
          "required $4$ and $53$",
          "4, 53", _c015,
          "Tconv of the M1 stages of paper runs 9 and 8 (raw 12, 11).")

    # conv-016 (substantive: Runs 1, 4, 6 are exactly the runs whose IP
    # anonymity set falls inside the band spanned by those three runs)
    def _c016():
        init_all = {r: _at(_seq(traj, r, "IP"), 1) for r in C.RUN_IDS}
        lo = min(init_all[r] for r in raw_runs)
        hi = max(init_all[r] for r in raw_runs)
        in_band = {r for r in C.RUN_IDS if lo <= init_all[r] <= hi}
        paper_ids = sorted(C.PAPER_RUN[r] for r in in_band)
        ok = (in_band == set(raw_runs) and paper_ids == [1, 4, 6])
        others = ", ".join(f"raw {r}={init_all[r]}" for r in C.RUN_IDS if r not in raw_runs)
        return (f"runs with |A1|(IP) in [{lo},{hi}]: {sorted(in_band)} -> paper "
                f"R{', R'.join(map(str, paper_ids))} [other runs: {others}]", ok)
    _emit(out, "conv-016", "sections/05-discussion.tex:78",
          "the Introduction Point stages of Runs~1, 4, and~6 started with similar sets of $79$--$84$ candidates",
          "1, 4, 6", _c016,
          "Band [lo,hi] = min/max of |A1|(IP) over raw 4, 7, 9 (paper 1, 4, 6, "
          "map p = r - 3); the claim is substantive because no other run's IP "
          "anonymity set may fall inside that band.")

    # conv-017
    def _c017():
        init = {r: _at(_seq(traj, r, "IP"), 1) for r in raw_runs}
        ok = (min(init.values()) == 79 and max(init.values()) == 84)
        return (f"{min(init.values())}--{max(init.values())} [|A1| raw 4,7,9 = "
                + ", ".join(str(init[r]) for r in raw_runs) + "]", ok)
    _emit(out, "conv-017", "sections/05-discussion.tex:79",
          "started with similar sets of $79$--$84$ candidates",
          "79--84", _c017,
          "seq(r,IP)[1] (= |A1|) for raw runs 4, 7, 9.")

    # conv-018
    def _c018():
        t10ip = {r: C.T_le(_seq(traj, r, "IP"), 10) for r in raw_runs}
        all3 = all(v is not None and v <= 3 for v in t10ip.values())
        return ("T<=10(IP) raw 4,7,9 = " + ", ".join(str(t10ip[r]) for r in raw_runs)
                + f"; all <= 3: {all3}", all3)
    _emit(out, "conv-018", "sections/05-discussion.tex:79",
          "reached $|\\mathcal{I}|\\leq10$ within three iterations",
          "3", _c018,
          "Threshold 10 and cutoff 3 from the same sentence.")

    # conv-019
    def _c019():
        want = {4: 285, 7: 8, 9: 324}
        tc = {r: tconv((r, "IP")) for r in raw_runs}
        ok = all(tc[r] is not None and tc[r] == want[r] for r in raw_runs)
        return (", ".join(str(tc[r]) for r in raw_runs) + " [Tconv(IP) raw 4, 7, 9]", ok)
    _emit(out, "conv-019", "sections/05-discussion.tex:80",
          "yet converged after $285$, $8$, and $324$ iterations, respectively",
          "285, 8, 324", _c019,
          "Tconv of the IP stages of paper runs 1, 4, 6.")

    # conv-020
    def _c020():
        ab_str = ", ".join(f"({r},{s})" for r, s in abrupt)
        return (f"{len(abrupt)} of {len(keys)} [{ab_str}]",
                len(abrupt) == 13 and len(keys) == 36)
    _emit(out, "conv-020", "sections/05-discussion.tex:82",
          "In $13$ of the $36$ stages the intersection still held three or more "
          "candidates at the penultimate iteration and then fell to a singleton in one step",
          "13 of 36", _c020,
          "Stages with seq[-2] >= 3 and seq[-1] == 1; threshold '>= 3' from the "
          "same sentence.")

    # conv-021
    def _c021():
        n10 = sum(1 for L in plateaus.values() if L >= 10)
        pl_str = ", ".join(f"({r},{s}):{L}" for (r, s), L in plateaus.items())
        return (f"{n10} of {len(abrupt)} abrupt-collapse stages have plateau >= 10 "
                f"[plateau lengths: {pl_str}]", n10 == 7)
    _emit(out, "conv-021", "sections/05-discussion.tex:84",
          "In seven of these the cardinality had been constant for at least ten iterations beforehand",
          "7", _c021,
          "ASSUMPTION: plateau length = number of consecutive trials ending at "
          "trial Tconv-1 with value == seq[-2] (the penultimate trial itself is "
          "counted); threshold 10 from the same sentence.")

    # conv-022
    def _c022():
        seq = _seq(traj, 4, "VG")
        tc = tconv((4, "VG"))
        first6 = _first_index(seq, 6)
        last_before = (tc if tc is not None else len(seq)) - 1
        run6 = (first6 is not None and all(v == 6 for v in seq[first6 - 1:last_before]))
        n6 = last_before - first6 + 1 if first6 is not None else 0
        ok = (len(seq) >= 2 and seq[-2] == 6 and run6 and n6 == 57 and tc == 61
              and seq.count(6) == 57)
        return (f"penultimate value={seq[-2] if len(seq) >= 2 else None}; plateau "
                f"trials {first6}..{last_before} ({n6} trials, contiguous={run6}); "
                f"Tconv={tc}", ok)
    _emit(out, "conv-022", "sections/05-discussion.tex:85",
          "The vanguard stage of Run~1 held six candidates for $57$ iterations and converged at iteration~$61$",
          "6; 57; 61", _c022,
          "seq(4,VG): first trial with value 6, run of 6s up to trial Tconv-1, and "
          "T<=1(seq) = Tconv.")

    # conv-023
    def _c023():
        res = {}
        for r in (6, 8):
            s = _seq(traj, r, "IP")
            tc = tconv((r, "IP"))
            f3 = _first_index(s, 3)
            lb = (tc if tc is not None else len(s)) - 1
            contiguous = f3 is not None and all(v == 3 for v in s[f3 - 1:lb])
            res[r] = dict(first=f3, last=lb, n=(lb - f3 + 1) if f3 else 0,
                          count=s.count(3), contiguous=contiguous, tconv=tc,
                          pen=s[-2] if len(s) >= 2 else None)
        ok = (res[6]["pen"] == 3 and res[8]["pen"] == 3
              and res[6]["n"] == 152 and res[8]["n"] == 148
              and res[6]["contiguous"] and res[8]["contiguous"]
              and res[6]["count"] == 152 and res[8]["count"] == 148
              and res[6]["tconv"] == 163 and res[8]["tconv"] == 178)
        return (f"value {res[6]['pen']}/{res[8]['pen']}; plateau {res[6]['n']}, "
                f"{res[8]['n']} (raw 6: trials {res[6]['first']}..{res[6]['last']}, "
                f"raw 8: trials {res[8]['first']}..{res[8]['last']}); Tconv "
                f"{res[6]['tconv']}, {res[8]['tconv']}", ok)
    _emit(out, "conv-023", "sections/05-discussion.tex:87",
          "Introduction Point stages of Runs~3 and~5 held three for $152$ and $148$ "
          "iterations before converging at iterations~$163$ and~$178$",
          "3; 152, 148; 163, 178", _c023,
          "Paper runs 3, 5 = raw 6, 8. Plateau = contiguous run of value 3 from "
          "T<=3 to Tconv-1; equivalently count(seq==3).")

    # conv-024
    _emit(out, "conv-024", "sections/07-conclusion.tex:32",
          "Across all nine experiments, the attack successfully reconstructed",
          "nine (all)",
          lambda: (all_runs_computed, all_runs_ok),
          "Same computation as conv-001.")


    return out

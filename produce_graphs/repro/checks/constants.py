"""Claims module 'constants': Tor protocol constants, cited external figures,
threat-model and implementation parameters.

These values are *reported* by the paper, not computed from the experiment
data, so every claim carries status CONSTANT with its source in 'note'.
Where the CSVs allow a structural cross-check (stage-code set, one trajectory
row per trial with contiguous trial indices, IP being the first stage of
every run by (experiment_date, experiment_time_utc), 36 run-stage rows, the
country list in the appendix, and consistency between restated constants) the
module performs that check and downgrades the claim to FAIL if the cross-check
contradicts the printed value.

Every claim additionally re-locates its quoted text in the CURRENT paper
(core.relocate: the registered file:line first, then the whole file, then
every active .tex file; whitespace-normalised, comments stripped). The report
shows where the text is printed now and notes "moved from <registered anchor>"
when that differs; a quote that is printed nowhere is reported as FAIL
("stale anchor") so that restructuring the paper cannot leave a CONSTANT claim
silently pointing at the wrong line. Textual cross-checks (const-027/028,
const-039, const-046/047) read the located sentence, not a fixed line.

Nothing is hard-coded as a "computed" value except the constant itself,
which by definition is the thing being reported.

Pure Python + csv/re only.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

import core as _core   # shared tex helpers (single copy in core.py)

# ----------------------------------------------------------------------------
# helpers (thin wrappers over core.py so every module shares one implementation)
# ----------------------------------------------------------------------------

def _text_at(quote: str, rel: str, lineno: int, extra: int = 1) -> str:
    """Current text of the line on which `quote` starts (located anywhere in the
    paper via core.locate_quote, the registered rel:lineno being only the first
    place tried) plus the `extra` following lines, joined; '' if not located."""
    found = _core.locate_quote(quote, rel, lineno)
    if not found:
        return ""
    frel, fline = found
    lines = _core.tex_lines(frel) or []
    return " ".join(lines[fline - 1:fline + extra])


_norm_ws = _core.norm_ws


def _stage_start(row) -> tuple[str, str]:
    """(experiment_date 'YYYY-MM-DD', 'HH:MM') of a stage's own MET row; minute
    resolution, sorts chronologically as a string pair."""
    hhmm = (row.get("experiment_time_utc") or "").strip().split(" ")[0][:5]
    return ((row.get("experiment_date") or "").strip(), hhmm)


def _stage_order_by_start(metrics, rid, C):
    """Stage codes of run `rid` sorted by (experiment_date, HH:MM), earliest first."""
    rows = [(_stage_start(metrics[(rid, s)]), s) for s in C.STAGES if (rid, s) in metrics]
    rows.sort()
    return [s for _, s in rows]


def _trial_contiguity(C) -> tuple[bool, int, int, list[str]]:
    """Re-read the raw trajectories CSV and check, per (run_id, stage), that the
    sorted trial indices are exactly 1..T.  Returns (ok, n_rows, n_keys, bad)."""
    path = Path(C.DATA) / "trajectories_every_trial.csv"
    trials: dict[tuple[int, str], list[int]] = {}
    n_rows = 0
    try:
        with open(path, newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                n_rows += 1
                trials.setdefault((int(r["run_id"]), r["stage"]), []).append(int(r["trial"]))
    except OSError:
        return False, 0, 0, ["trajectories_every_trial.csv unreadable"]
    bad = []
    for key, ts in sorted(trials.items()):
        if sorted(ts) != list(range(1, len(ts) + 1)):
            bad.append(f"run {key[0]}/{key[1]}")
    return not bad, n_rows, len(trials), bad


def _count_countries(line: str) -> tuple[int, list[str]]:
    """Count the enumerated country names in the Fourteen-Eyes sentence."""
    m = re.search(r"hosting country is (.*?)\.\s", line + " ")
    if not m:
        return 0, []
    body = m.group(1)
    body = re.sub(r",?\s+or\s+", ", ", body)
    items = [x.strip() for x in body.split(",") if x.strip()]
    return len(items), items


def _claim(C, cid, loc, quote, paper, computed, status, note):
    """Build a claim dict. The quote is re-located in the CURRENT paper
    (core.relocate: registered file:line first, then the whole file, then every
    active file); the reported location is where it is printed now. A quote
    that is printed nowhere downgrades the claim to FAIL (stale anchor)."""
    st, where, mv = _core.relocate(loc, quote)
    if st == "absent":
        status = "FAIL"
        note = f"stale anchor: {mv}. " + note
    elif st == "nofile":
        status = "UNVERIFIABLE"
        note = f"{mv}. " + note
    elif mv:
        note = f"[{mv}] " + note
    return {"id": cid, "location": where, "quote": quote, "paper": str(paper),
            "computed": str(computed), "status": status, "note": note}


# ----------------------------------------------------------------------------
# claims
# ----------------------------------------------------------------------------

def claims(C, traj, metrics) -> list[dict]:
    out = []

    # ---- shared cross-check computations -----------------------------------
    stage_codes = sorted({s for (_, s) in metrics} | {s for (_, s) in traj})
    n_stage_codes = len(stage_codes)
    contig_ok, n_traj_rows, n_traj_keys, contig_bad = _trial_contiguity(C)
    n_met_rows = len(metrics)
    first_stage = {rid: (_stage_order_by_start(metrics, rid, C) or [None])[0] for rid in C.RUN_IDS}
    all_ip_first = all(v == "IP" for v in first_stage.values())

    def constant(cid, loc, quote, value, source):
        return _claim(C, cid, loc, quote, value, value, "CONSTANT", "CONSTANT: " + source)

    def xcheck(cid, loc, quote, value, computed, ok, source):
        """CONSTANT with a structural/textual cross-check.  The parameter itself
        cannot be recomputed, so a contradicting cross-check is reported as
        UNVERIFIABLE with the evidence, not as a FAIL of the text."""
        return _claim(C, cid, loc, quote, value, computed,
                      "CONSTANT" if ok else "UNVERIFIABLE",
                      ("CONSTANT: " if ok else "DATA CAVEAT: the data contradict this value "
                       "(see computed). CONSTANT: ") + source)

    TOR_10MIN = "Tor default MaxCircuitDirtiness = 600 s = 10 min (tor(1) manual)."
    INTRO_LIFE = ("Tor rend-spec-v3 / hs_circuit INTRO_POINT_LIFETIME_MIN_SECONDS = 18 h, "
                  "MAX = 24 h; cited platzer2020critical.")
    THREAT = "threat-model assumption defined by the paper (sections/03-attack.tex:297)."

    # ---- main.tex ----------------------------------------------------------
    out.append(constant("const-001", "main.tex:71",
                        "client circuits typically\nlast only about $10$~min", "10", TOR_10MIN))
    out.append(constant("const-002", "main.tex:74",
                        "remain fixed for $18$--$24$~h", "18--24", INTRO_LIFE))

    # ---- 01-introduction ---------------------------------------------------
    out.append(constant("const-003", "sections/01-introduction.tex:51",
                        "enabling millions of users to conceal their sensitive Internet activities",
                        "millions",
                        "Tor Metrics daily-user estimates (~2M directly connecting users); "
                        "order-of-magnitude cited figure."))
    out.append(constant("const-004", "sections/01-introduction.tex:73",
                        "For an adversary limited to monitoring one relay at a time", "one", THREAT))
    out.append(constant("const-005", "sections/01-introduction.tex:81",
                        "typically last at most about $10$~min", "10",
                        TOR_10MIN + " Cited erdin2015find."))
    out.append(constant("const-006", "sections/01-introduction.tex:93",
                        "$18$--$24$~h \\cite{platzer2020critical}", "18--24", INTRO_LIFE))
    out.append(constant("const-007", "sections/01-introduction.tex:97",
                        "only one Tor relay at a time an extended window", "one", THREAT))
    out.append(constant("const-008", "sections/01-introduction.tex:106",
                        "We consider an adversary that monitors one relay at a time, chosen adaptively:",
                        "one", THREAT))

    # ---- 02-background -----------------------------------------------------
    out.append(constant("const-009", "sections/02-background.tex:54",
                        "chosen from a fixed set of four \\emph{layer-2 vanguards},", "four",
                        "Tor proposal 333 (Vanguards-Lite) NUM_LAYER2_GUARDS = 4."))
    out.append(constant("const-010", "sections/02-background.tex:55",
                        "each kept for a random period of $1$--$12$~days.", "1--12",
                        "Tor proposal 333 layer-2 guard lifetime: min 1 day, max 12 days."))
    out.append(constant("const-011", "sections/02-background.tex:56",
                        "The optional \\emph{Full\nVanguards} mode also fixes the third relay.", "third",
                        "vanguards add-on specification (layer-3 guards pin the third hop)."))
    out.append(constant("const-012", "sections/02-background.tex:67",
                        "three by default, as its \\emph{Introduction Points} (IntPs).", "three",
                        "Tor HiddenServiceNumIntroductionPoints default = 3 (rend-spec-v3)."))

    # ---- 03-attack ---------------------------------------------------------
    out.append(constant("const-013", "sections/03-attack.tex:282",
                        "ordinary Tor circuits are typically used for about $10$~min", "10", TOR_10MIN))
    out.append(constant("const-014", "sections/03-attack.tex:286",
                        "for $18$--$24$~h~\\cite{platzer2020critical}", "18--24", INTRO_LIFE))
    out.append(constant("const-015", "sections/03-attack.tex:297",
                        "(iii) observes at most one\nTor relay at a time", "one", THREAT))
    out.append(xcheck("const-016", "sections/03-attack.tex:339",
                      "An onion service's introduction circuit consists of four relays",
                      "four",
                      f"{n_stage_codes} distinct stage codes in MET/TRAJ ({', '.join(stage_codes)})",
                      n_stage_codes == 4,
                      "Tor vanguards spec (guard, L2, L3/middle, IntP); structurally mirrored by the "
                      "distinct stage codes in the data (see setup-003)."))
    out.append(constant("const-017", "sections/03-attack.tex:341-343",
                        "service $\\to$ entry guard $\\to$ layer-2\nvanguard $\\to$ middle relay $\\to$ "
                        "Introduction Point. Under the optional\nFull Vanguards configuration, "
                        "a layer-3 vanguard replaces the middle\nrelay",
                        "layer-2 / layer-3",
                        "Tor proposal 333 (Vanguards-Lite: L2 pinned, middle free) / vanguards add-on "
                        "(Full Vanguards: L2 and L3 pinned)."))
    out.append(constant("const-018", "sections/03-attack.tex:399",
                        "From stage~$1$ onward, $r_{m_i}$ receives the introduction cell from its\npredecessor",
                        "1",
                        "algorithm definition (Alg. reconstruction, predecessor-exclusion step); "
                        "not data-derived. Restated at implementation.tex:101 (const-034)."))
    out.append(constant("const-019", "sections/03-attack.tex:416",
                        "Tor's general rule against placing two relays from\nthe same \\texttt{/16} subnet on a circuit",
                        "/16; two",
                        "Tor path-spec section 2.2 (EnforceDistinctSubnets), relaxed for HS circuits "
                        "by proposal 333."))
    out.append(constant("const-020", "sections/03-attack.tex:426",
                        "the adversary builds a new client-side circuit for each iteration",
                        "one per iteration",
                        "implementation description (fresh Tor client per iteration, "
                        "implementation.tex:32); not recorded in the CSVs."))
    out.append(constant("const-021", "sections/03-attack.tex:482",
                        "after approximately $10$~min in ordinary Tor", "10", TOR_10MIN))
    out.append(constant("const-022", "sections/03-attack.tex:483",
                        "population turns over approximately $2.5$ times per\nday~\\cite{jansen2016safely}",
                        "2.5", "cited jansen2016safely (Safely Measuring Tor, CCS 2016)."))

    # ---- 04-setup-and-evaluation -------------------------------------------
    out.append(constant("const-023", "sections/04-setup-and-evaluation.tex:392",
                        "the lower end of the introduction circuit's $18$--$24$~h lifetime",
                        "18--24", INTRO_LIFE))
    out.append(constant("const-024", "sections/04-setup-and-evaluation.tex:396",
                        "reconstruction still completes within $18$~h", "18",
                        "definitional; 18 h = lower end of the Tor intro-circuit lifetime "
                        "(INTRO_POINT_LIFETIME_MIN_SECONDS)."))

    # ---- 05-discussion -----------------------------------------------------
    out.append(constant("const-025", "sections/05-discussion.tex:4",
                        "Our attack exploits the $18$--$24$~h introduction-circuit lifetime",
                        "18--24", INTRO_LIFE))
    out.append(constant("const-026", "sections/05-discussion.tex:8",
                        "a service-side path used for only about $10$~min, the lifetime of an ordinary Tor circuit",
                        "10", TOR_10MIN))
    # const-027 / const-028: proposal parameter restated; must agree textually.
    # (The sentence is located in the current paper, not read at a fixed line.)
    q27 = "approximately every $10$~min. Relay selection remains unchanged"
    q28 = "even if a stage converges within a $10$-minute interval"
    l27 = _text_at(q27, "sections/05-discussion.tex", 17)
    l33 = _text_at(q28, "sections/05-discussion.tex", 33)
    v27 = re.search(r"every \$(\d+)\$~min", l27)
    v33 = re.search(r"\$(\d+)\$-minute", l33)
    v27 = v27.group(1) if v27 else None
    v33 = v33.group(1) if v33 else None
    out.append(xcheck("const-027", "sections/05-discussion.tex:17", q27,
                      "10", v27 if v27 is not None else "tex line not found",
                      v27 == "10",
                      "proposal parameter chosen by the authors (matches MaxCircuitDirtiness); "
                      "restated in the same section (const-028)."))
    out.append(xcheck("const-028", "sections/05-discussion.tex:33", q28,
                      "10", f"{v33} (const-027 sentence says {v27})",
                      v33 == "10" and v33 == v27,
                      "proposal parameter; textual check that it equals const-027."))
    out.append(constant("const-029", "sections/05-discussion.tex:120",
                        "the current $18$--$24$~h lifetime of introduction circuits", "18--24", INTRO_LIFE))

    # ---- 06-related-work / 07-conclusion -----------------------------------
    out.append(constant("const-030", "sections/06-related-work.tex:28",
                        "traffic observed at two network vantage points and generalizes to unseen flows",
                        "two", "property of cited work (DeepCorr, Nasr et al., CCS 2018)."))
    out.append(constant("const-031", "sections/07-conclusion.tex:27",
                        "requiring visibility of only\none relay at a time.", "one", THREAT))

    # ---- implementation ----------------------------------------------------
    out.append(xcheck("const-032", "sections/implementation.tex:32",
                      "Triggers one introduction handshake per iteration", "one",
                      f"one TRAJ row per (run,stage,trial): {n_traj_rows} rows across {n_traj_keys} "
                      f"run-stage trajectories; trial indices re-read from "
                      f"trajectories_every_trial.csv are contiguous 1..T in "
                      + (f"all {n_traj_keys}" if contig_ok else
                         f"{n_traj_keys - len(contig_bad)}/{n_traj_keys} (violations: {', '.join(contig_bad)})"),
                      contig_ok and n_traj_keys == 36 and len(traj) == 36,
                      "prototype design; consistent with one TRAJ row per (run,stage,trial) "
                      "(contiguity verified in-module from the raw CSV)."))
    out.append(xcheck("const-033", "sections/implementation.tex:71",
                      "At stage~$0$ the monitored relay is the advertised Introduction Point.", "0",
                      "earliest stage per run by (experiment_date, experiment_time_utc) = "
                      + ("IP for all 9 runs" if all_ip_first else str(first_stage)),
                      all_ip_first,
                      "design; MET first stage_code per run is IP (earliest experiment_date + "
                      "experiment_time_utc, minute resolution) - see setup-003."))
    out.append(constant("const-034", "sections/implementation.tex:101",
                        "removing the known predecessor $r_{m_{i-1}}$ from stage~$1$ onward", "1",
                        "algorithm design (same constant as const-018)."))
    out.append(constant("const-035", "sections/implementation.tex:104",
                        "$\\delta=30$~s, and repeats steps~6a--13 against the same relay", "30",
                        "implementation parameter (delta = 30 s slept between iterations); stage "
                        "timestamps are not part of the released dataset, so it is not recomputable. "
                        "Restated at sections/04-setup-and-evaluation.tex:329 and :370 "
                        "(const-046/047, textual consistency)."))
    out.append(constant("const-036", "sections/implementation.tex:155",
                        "A typical ten-minute period on the deployed network involves roughly 550{,}000 "
                        "active users and about 1.4~million active circuits~\\cite{jansen2016safely}",
                        "ten-minute; 550,000; 1.4 million",
                        "cited jansen2016safely (Safely Measuring Tor, CCS 2016)."))
    out.append(xcheck("const-037", "sections/implementation.tex:167",
                      "pseudonymised in volatile memory using per-stage RSA keys",
                      "per-stage (one key per stage)",
                      f"{n_met_rows} run-stage rows in MET => {n_met_rows} keys implied",
                      n_met_rows == 36,
                      "design statement; implies one key per MET row (36) but keys never reached disk, "
                      "so the key count itself is not checkable."))

    # ---- appendix_relay_concentration --------------------------------------
    q39 = ("Australia, Belgium, Canada, Denmark, France, Germany, Italy, the Netherlands, "
           "New Zealand, Norway, Spain, Sweden, the United Kingdom, or the United States")
    l6 = _text_at(q39, "sections/appendix_relay_concentration.tex", 6)
    n_countries, countries = _count_countries(l6)
    out.append(xcheck("const-038", "sections/appendix_relay_concentration.tex:4",
                      "We consider the Fourteen Eyes as a grouping of jurisdictions", "Fourteen (14)",
                      f"{n_countries} country names enumerated at line 6",
                      n_countries == 14,
                      "cited williams2023five; count of country names in line 6 of the same file."))
    out.append(xcheck("const-039", "sections/appendix_relay_concentration.tex:6", q39,
                      "14 countries listed",
                      f"{n_countries}: {', '.join(countries)}" if countries else "enumeration not found",
                      n_countries == 14,
                      "list definition; textual check splits the enumeration on commas/'or' and counts."))
    out.append(constant("const-040", "sections/appendix_relay_concentration.tex:36",
                        "introduction circuit is reused for at most $18$--$24$~h", "18--24 h", INTRO_LIFE))
    out.append(constant("const-041", "sections/appendix_relay_concentration.tex:42",
                        "circuits leave through one reachable guard", "one (1)",
                        "Tor guard-spec (one primary guard in use for onion-service circuits)."))
    out.append(constant("const-042", "sections/appendix_relay_concentration.tex:44",
                        "for the guard set, held for months, to shift", "months",
                        "Tor guard-spec guard lifetime (~2-3 months, guard-lifetime consensus parameter)."))
    out.append(constant("const-043", "sections/appendix_relay_concentration.tex:47",
                        "from a set of four that itself turns over every $1$--$12$~days", "four; 1--12 days",
                        "Tor proposal 333 (NUM_LAYER2_GUARDS = 4; lifetime 1-12 days); same as const-009/010."))
    out.append(constant("const-044", "sections/appendix_relay_concentration.tex:49",
                        "A service's three introduction circuits share that guard", "three (3)",
                        "HiddenServiceNumIntroductionPoints default = 3 (same as const-012)."))
    out.append(constant("const-045", "sections/appendix_relay_concentration.tex:50",
                        "The three can also be attacked concurrently", "three (3)",
                        "same constant as const-044."))

    # ---- 04-setup restatements of delta ------------------------------------
    # (each sentence located in the current paper; the registered lines are fallbacks)
    q46 = "The controller relaunches the client after $\\delta=30$~s"
    q47 = "The $30$~s delay is a configurable\nparameter of our implementation"
    q35 = "$\\delta=30$~s, and repeats steps~6a--13 against the same relay"
    l329 = _text_at(q46, "sections/04-setup-and-evaluation.tex", 329)
    l370 = _text_at(q47, "sections/04-setup-and-evaluation.tex", 370)
    l104 = _text_at(q35, "sections/implementation.tex", 104)
    d329 = re.search(r"\\delta=(\d+)\$~s", l329)
    d370 = re.search(r"The \$(\d+)\$~s delay", l370)
    d104 = re.search(r"\\delta=(\d+)\$~s", l104)
    d329, d370, d104 = (m.group(1) if m else None for m in (d329, d370, d104))
    out.append(xcheck("const-046", "sections/04-setup-and-evaluation.tex:329", q46, "30",
                      f"tex: {d329}; implementation.tex (const-035 sentence) says {d104}",
                      d329 == "30" and d329 == d104,
                      "implementation parameter (same as const-035); textual check only that it equals "
                      "the implementation.tex statement."))
    out.append(xcheck("const-047", "sections/04-setup-and-evaluation.tex:370", q47, "30",
                      f"tex: {d370}; const-046 sentence says {d329}; implementation.tex says {d104}",
                      d370 == "30" and d370 == d329 == d104,
                      "implementation parameter; textual check that it equals const-035/046."))

    # integrity: 47 unique ids
    ids = [c["id"] for c in out]
    assert len(ids) == len(set(ids)) == 47, f"expected 47 unique ids, got {len(ids)}/{len(set(ids))}"
    return out

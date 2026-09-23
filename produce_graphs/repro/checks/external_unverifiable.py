"""Claims whose inputs lie outside the two generated CSVs.

Three groups:

* Relay ages at experiment start (ext-001). Needs Onionoo ``first_seen`` for
  the four operated relays; ``run_stage_metrics.csv`` carries no fingerprint or
  first_seen column, so this is UNVERIFIABLE. If a ``first_seen`` column is
  ever added, the ages are computed from it and compared with the range parsed
  from the .tex; the claim is never failed from an uncomputed value.

* The introduction-latency appendix (ext-002 .. ext-027). The raw per-trial
  measurements are not in the project; only the per-service means printed in
  ``tab:onion_avg_latency`` exist. Everything that can be checked *within the
  paper* is checked by parsing the current .tex at run time: the printed
  service count against the table row count, the printed total against
  rows x printed trials, the printed min/max range (in the appendix and in the
  Discussion) against the table's min/max, and every cell against the range
  stated in prose. The means themselves and the trial count remain
  UNVERIFIABLE.

* The Onionoo relay snapshot (ext-028 .. ext-034). The snapshot is not in the
  project (repro/README: only a revision log), so the country shares and the
  75% probability-mass claims are UNVERIFIABLE; the recipe that would verify
  them is stated in each note. Textual consistency of the date string and the
  75% figure across mentions is checked by searching the whole
  comment-stripped .tex file.

Every "paper" value used in a PASS/FAIL decision is parsed from the current
.tex at run time; nothing is compared against a literal copied from an older
extraction. The quote strings are documentation only.
"""
from __future__ import annotations

import re
from datetime import date, datetime

import core as _core   # shared tex helpers (single copy in core.py)

LAT_TEX = "sections/appendix_time_of_introduction_handshake_completion.tex"
REL_TEX = "sections/appendix_relay_concentration.tex"
SETUP_TEX = "sections/04-setup-and-evaluation.tex"
DISC_TEX = "sections/05-discussion.tex"

# Row order of tab:onion_avg_latency as printed (name -> extraction quote).
# The numeric literal inside each quote is the *extraction* and is checked
# against the current .tex cell; a mismatch marks the extraction as stale.
LAT_ROW_QUOTES = [
    ("Cryptostamps", "Cryptostamps     & Postage store        & 0.642 \\\\"),
    ("Breaking Bad", "Breaking Bad     & Drug forum           & 0.547 \\\\"),
    ("Black Cloud", "Black Cloud      & Onion pastebin       & 1.780 \\\\"),
    ("Ahmia", "Ahmia            & HS search engine     & 1.019 \\\\"),
    ("Onion ID Serv.", "Onion ID Serv.   & ID/passport store    & 0.879 \\\\"),
    ("ChaTor", "ChaTor           & Onion messenger      & 1.230 \\\\"),
    ("Comic Book Libr.", "Comic Book Libr. & Library              & 0.654 \\\\"),
    ("Apples4Bitcoin", "Apples4Bitcoin   & Onion apple store    & 0.882 \\\\"),
    ("Dread", "Dread            & Onion forum          & 1.060 \\\\"),
    ("Mail2Tor", "Mail2Tor         & Onion mail           & 0.701 \\\\"),
    ("Sonar", "Sonar            & Onion messenger      & 0.805 \\\\"),
    ("FAH", "FAH              & Hiring service       & 1.492 \\\\"),
    ("Mobile Store", "Mobile Store     & Mobile store         & 0.871 \\\\"),
    ("USJUD", "USJUD            & Counterfeit store    & 0.636 \\\\"),
    ("BMG", "BMG              & Gun store            & 0.521 \\\\"),
    ("DarkSearch", "DarkSearch       & Onion search engine  & 0.657 \\\\"),
]
LAT_ROW_IDS = {name: f"ext-{12 + i:03d}" for i, (name, _) in enumerate(LAT_ROW_QUOTES)}

FOURTEEN_EYES = ["au", "be", "ca", "dk", "fr", "de", "it", "nl", "nz", "no",
                 "es", "se", "gb", "us"]

# Regexes for numbers printed in prose (all applied to comment-stripped text).
RE_DATE = re.compile(r"\b(\d{1,2} (?:January|February|March|April|May|June|July|"
                     r"August|September|October|November|December) \d{4})\b")
RE_DATE_SNAPSHOT = re.compile(r"Onionoo on (\d{1,2} [A-Z][a-z]+ \d{4})")
RE_PCT75 = re.compile(r"\$(\d+)\\%\$")
RE_DISC_RANGE = re.compile(r"complete in \$([0-9.]+)\$--\$([0-9.]+)\$~s")
RE_APP_RANGE = re.compile(r"range from \$([0-9.]+)\$~s to \$([0-9.]+)\$~s")
RE_AGE_RANGE = re.compile(r"active for \$(\d+)\$--\$(\d+)\$ days")
RE_SERVICES_A = re.compile(r"handshake for (\d+) publicly")
RE_SERVICES_B = re.compile(r"using (\d+) publicly")
RE_TRIALS = re.compile(r"perform (\d+) independent")
RE_TOTAL = re.compile(r"yielding (\d+) measurements")
RE_CAPTION = re.compile(r"across (\d+) onion services, with (\d+) trials")
RE_TRIALS_REPEAT = re.compile(r"repeating the measurement (\d+) times")
RE_TRIALS_MEAN = re.compile(r"across the (\d+) trials")


# --------------------------------------------------------------------------
# helpers (pure Python)
# --------------------------------------------------------------------------
def _clean(rel: str):
    """[(lineno, text)] of the current .tex: comment lines dropped, '%' tails
    stripped, \\begin{comment}..\\end{comment} blocks excluded (core.tex_active)."""
    return _core.tex_active(rel)


def _find_all(clean, regex):
    """All (lineno, match) of `regex` over cleaned lines."""
    hits = []
    for ln, txt in clean:
        for m in regex.finditer(txt):
            hits.append((ln, m))
    return hits


def _find_first(clean, regex):
    hits = _find_all(clean, regex)
    return hits[0] if hits else (None, None)


def _lines_containing(clean, needle):
    return [ln for ln, txt in clean if needle in txt]


_ROW_RE = re.compile(r"^\s*([^&\\]+?)\s*&\s*([^&\\]+?)\s*&\s*([0-9]+\.[0-9]+)\s*\\\\")


def _parse_latency_table(clean):
    """Return list of (name, type, value_str, lineno) for data rows of
    tab:onion_avg_latency, in printed order."""
    rows, in_tab = [], False
    for ln, line in clean:
        if "\\begin{tabular}" in line:
            in_tab = True
            continue
        if "\\end{tabular}" in line:
            in_tab = False
            continue
        if not in_tab:
            continue
        m = _ROW_RE.match(line)
        if m and "\\textbf" not in line:
            rows.append((m.group(1).strip(), m.group(2).strip(), m.group(3), ln))
    return rows


def _experiment_start(metrics):
    """Earliest experiment_date (YYYY-MM-DD) across all run/stage rows (date)."""
    ds = []
    for row in metrics.values():
        v = (row.get("experiment_date") or "").strip()
        if v:
            try:
                ds.append(date.fromisoformat(v[:10]))
            except ValueError:
                pass
    return min(ds) if ds else None


def _parse_date(v):
    v = (v or "").strip()
    if not v:
        return None
    try:
        return datetime.fromisoformat(v).date()
    except ValueError:
        pass
    try:
        return date.fromisoformat(v[:10])
    except ValueError:
        return None


def _fmt(v, nd=3):
    return f"{v:.{nd}f}"


def _loc(rel, ln):
    return f"{rel}:{ln if ln is not None else '?'}"


# --------------------------------------------------------------------------
def claims(C, traj, metrics) -> list[dict]:
    lat_clean = _clean(LAT_TEX)
    rel_clean = _clean(REL_TEX)
    disc_clean = _clean(DISC_TEX)
    setup_clean = _clean(SETUP_TEX)
    lat_present = bool(lat_clean)

    rows = _parse_latency_table(lat_clean)
    vals = [float(v) for _, _, v, _ in rows]
    n_rows = len(rows)
    vmin = min(vals) if vals else None
    vmax = max(vals) if vals else None
    vmean = (sum(vals) / len(vals)) if vals else None
    rng_str = (f"{_fmt(vmin)}--{_fmt(vmax)}" if vals else "table not found")
    name_min = rows[vals.index(vmin)][0] if vals else "?"
    name_max = rows[vals.index(vmax)][0] if vals else "?"
    by_name = {r[0]: r for r in rows}

    # Numbers printed in prose, located at run time.
    ln_svc_a, m_svc_a = _find_first(lat_clean, RE_SERVICES_A)
    ln_svc_b, m_svc_b = _find_first(lat_clean, RE_SERVICES_B)
    ln_trials, m_trials = _find_first(lat_clean, RE_TRIALS)
    ln_total, m_total = _find_first(lat_clean, RE_TOTAL)
    ln_app_rng, m_app_rng = _find_first(lat_clean, RE_APP_RANGE)
    ln_cap, m_cap = _find_first(lat_clean, RE_CAPTION)
    ln_rep, m_rep = _find_first(lat_clean, RE_TRIALS_REPEAT)
    ln_mean, m_mean = _find_first(lat_clean, RE_TRIALS_MEAN)
    # These two sentences are located anywhere in the active paper (preferred
    # file first): the "complete in a--b s" restatement moved from the
    # Discussion into the evaluation section in a later revision.
    hit = _core.search_paper(RE_DISC_RANGE, DISC_TEX)
    disc_rel, ln_disc_rng, m_disc_rng = hit if hit else (DISC_TEX, None, None)
    hit = _core.search_paper(RE_AGE_RANGE, SETUP_TEX)
    age_rel, ln_age, m_age = hit if hit else (SETUP_TEX, None, None)

    stated_svc_a = int(m_svc_a.group(1)) if m_svc_a else None
    stated_svc_b = int(m_svc_b.group(1)) if m_svc_b else None
    stated_trials = int(m_trials.group(1)) if m_trials else None
    stated_total = int(m_total.group(1)) if m_total else None
    app_rng = (m_app_rng.group(1), m_app_rng.group(2)) if m_app_rng else None
    disc_rng = (m_disc_rng.group(1), m_disc_rng.group(2)) if m_disc_rng else None
    cap_svc = int(m_cap.group(1)) if m_cap else None
    cap_trials = int(m_cap.group(2)) if m_cap else None
    rep_trials = int(m_rep.group(1)) if m_rep else None
    mean_trials = int(m_mean.group(1)) if m_mean else None

    out = []

    # ---- ext-001: relay ages ------------------------------------------------
    t0d = _experiment_start(metrics)
    t0s = t0d.isoformat() if t0d else "unknown"
    age_paper = f"{m_age.group(1)}--{m_age.group(2)}" if m_age else "not found in tex"
    first_seen_vals = sorted({(r.get("first_seen") or "").strip()
                              for r in metrics.values() if (r.get("first_seen") or "").strip()})
    ages = []
    if first_seen_vals and t0d:
        for fs in first_seen_vals:
            d = _parse_date(fs)
            if d is not None:
                ages.append((t0d - d).days)
    if ages and m_age:
        amin, amax = min(ages), max(ages)
        computed = f"{amin}--{amax} (from {len(ages)} distinct first_seen values, t0={t0s})"
        status = ("PASS" if (amin == int(m_age.group(1)) and amax == int(m_age.group(2)))
                  else "FAIL")
        note = ("Computed from a first_seen column found in run_stage_metrics.csv: "
                "(min(experiment_date) - first_seen).days per relay.")
    else:
        computed = "n/a (no relay first_seen in metrics)"
        status = "UNVERIFIABLE"
        note = (f"Needs Onionoo first_seen for the four operated relays; recipe: "
                f"({t0s} - first_seen).days for each relay, expect min/max = {age_paper}. "
                f"Experiment start = min(experiment_date) over run_stage_metrics.csv = {t0s}. "
                f"run_stage_metrics.csv has no fingerprint/first_seen column.")
    if age_rel != SETUP_TEX:
        note = f"[moved from {SETUP_TEX}] " + note
    out.append(dict(
        id="ext-001", location=_loc(age_rel, ln_age),
        quote="The relays had been active for $69$--$126$ days when the experiments began",
        paper=age_paper, computed=computed, status=status, note=note))

    # ---- ext-002: discussion restates the range -----------------------------
    if not vals:
        st2, cmp2 = "UNVERIFIABLE", "table not found"
    elif disc_rng is None:
        st2, cmp2 = "UNVERIFIABLE", rng_str
    else:
        st2 = ("PASS" if (_fmt(vmin) == disc_rng[0] and _fmt(vmax) == disc_rng[1]) else "FAIL")
        cmp2 = rng_str
    out.append(dict(
        id="ext-002", location=_loc(disc_rel, ln_disc_rng),
        quote="complete in $0.521$--$1.780$~s, depending on the service",
        paper=(f"{disc_rng[0]}--{disc_rng[1]}" if disc_rng else "range not found in tex"),
        computed=cmp2, status=st2,
        note=((f"[moved from {DISC_TEX}] " if disc_rel != DISC_TEX else "")
              + f"Range parsed from {disc_rel} at run time and compared with the min/max of "
              f"the {n_rows} Avg dt cells parsed from {LAT_TEX} (min={name_min}, "
              f"max={name_max}). Raw per-trial latencies are not in the project, so the "
              f"means themselves are unverifiable.")))

    # ---- ext-003 / ext-005: printed service count vs table rows -------------
    for cid, ln, stated, quote in [
        ("ext-003", ln_svc_a, stated_svc_a,
         "we measured the introduction handshake for 16 publicly reachable onion services"),
        ("ext-005", ln_svc_b, stated_svc_b,
         "We measure this interval using 16 publicly reachable onion services."),
    ]:
        if not lat_present:
            st, cmp = "UNVERIFIABLE", "table not found"
        elif stated is None:
            st, cmp = "UNVERIFIABLE", f"{n_rows} rows (printed count not found in tex)"
        else:
            st, cmp = ("PASS" if n_rows == stated else "FAIL"), str(n_rows)
        out.append(dict(
            id=cid, location=_loc(LAT_TEX, ln), quote=quote,
            paper=(str(stated) if stated is not None else "not found in tex"),
            computed=cmp, status=st,
            note="Textual: printed service count parsed from the .tex compared with the "
                 "number of data rows in tab:onion_avg_latency."))

    # ---- ext-004 / ext-006 / ext-008: trials per service --------------------
    trial_mentions = {"repeating": rep_trials, "perform": stated_trials,
                      "mean-across": mean_trials, "caption": cap_trials}
    trial_txt = ", ".join(f"{k}={v}" for k, v in trial_mentions.items())
    for cid, ln, stated, quote in [
        ("ext-004", ln_rep, rep_trials, "repeating the measurement 10 times for each service"),
        ("ext-006", ln_trials, stated_trials,
         "For each service, we perform 10 independent introduction handshakes"),
        ("ext-008", ln_mean, mean_trials,
         "reports the mean $\\Delta t$ across the 10 trials for each onion service"),
    ]:
        out.append(dict(
            id=cid, location=_loc(LAT_TEX, ln), quote=quote,
            paper=(str(stated) if stated is not None else "not found in tex"),
            computed="n/a (raw trials absent)", status="UNVERIFIABLE",
            note="Raw per-trial introduction-latency measurements are not in the project; "
                 f"only the per-service means are printed. Trial count as printed at each "
                 f"mention: {trial_txt}."))

    # ---- ext-007: total = rows x printed trials ----------------------------
    prod = (n_rows * stated_trials) if (n_rows and stated_trials is not None) else None
    if prod is None or stated_total is None:
        st7 = "UNVERIFIABLE"
        cmp7 = (f"{n_rows} rows x {stated_trials} stated trials = {prod}"
                if prod is not None else "n/a")
    else:
        st7 = "PASS" if prod == stated_total else "FAIL"
        cmp7 = f"{n_rows} rows x {stated_trials} stated trials = {prod}"
    out.append(dict(
        id="ext-007", location=_loc(LAT_TEX, ln_total),
        quote="yielding 160 measurements in total",
        paper=(str(stated_total) if stated_total is not None else "not found in tex"),
        computed=cmp7, status=st7,
        note=("Arithmetic consistency only: table row count times the trial count "
              "printed in the same paragraph, compared with the printed total; the "
              "trial factor itself is unverifiable (raw trials absent).")))

    # ---- ext-009: range restated in Results ---------------------------------
    if not vals:
        st9, cmp9 = "UNVERIFIABLE", "table not found"
    elif app_rng is None:
        st9, cmp9 = "UNVERIFIABLE", rng_str
    else:
        st9 = ("PASS" if (_fmt(vmin) == app_rng[0] and _fmt(vmax) == app_rng[1]) else "FAIL")
        cmp9 = rng_str
    out.append(dict(
        id="ext-009", location=_loc(LAT_TEX, ln_app_rng),
        quote="The per-service means range from $0.521$~s to $1.780$~s.",
        paper=(f"{app_rng[0]}--{app_rng[1]}" if app_rng else "range not found in tex"),
        computed=cmp9, status=st9,
        note=f"Range parsed from the prose at run time; table-internal min ({name_min}) "
             f"and max ({name_max}) of the parsed Avg dt column."))

    # ---- ext-010: order of seconds ------------------------------------------
    crit_max = 2.0
    ok10 = bool(vals) and all(0.0 < v for v in vals) and vmax < crit_max
    out.append(dict(
        id="ext-010", location=_loc(LAT_TEX, ln_app_rng),
        quote="the complete interval therefore remains on the order of seconds",
        paper="order of seconds",
        computed=(f"all {n_rows} means in [{_fmt(vmin)}, {_fmt(vmax)}] s, mean {_fmt(vmean)} s; "
                  f"criterion 0 < v and max < {crit_max:.1f} s: {ok10}"
                  if vals else "table not found"),
        status="PASS" if ok10 else ("UNVERIFIABLE" if not vals else "FAIL"),
        note=(f"Table-internal: largest per-service mean is {_fmt(vmax)} s ({name_max}); "
              f"criterion used: every mean positive and below {crit_max:.1f} s."
              if vals else "Table not found.")))

    # ---- ext-011a / ext-011b: caption counts --------------------------------
    if not lat_present:
        st11a, cmp11a = "UNVERIFIABLE", "table not found"
    elif cap_svc is None:
        st11a, cmp11a = "UNVERIFIABLE", f"{n_rows} rows (caption count not found)"
    else:
        st11a, cmp11a = ("PASS" if cap_svc == n_rows else "FAIL"), f"{n_rows} rows"
    out.append(dict(
        id="ext-011a", location=_loc(LAT_TEX, ln_cap),
        quote="across 16 onion services, with 10 trials per service",
        paper=(str(cap_svc) if cap_svc is not None else "not found in tex"),
        computed=cmp11a, status=st11a,
        note="Caption service count parsed from the .tex compared with the table row count."))

    if cap_trials is None or stated_trials is None:
        st11b = "UNVERIFIABLE"
        cmp11b = "n/a (raw trials absent; caption or methodology trial count not found)"
    else:
        consistent = (cap_trials == stated_trials)
        st11b = "UNVERIFIABLE" if consistent else "FAIL"
        cmp11b = (f"caption {cap_trials} vs methodology {stated_trials}: "
                  f"consistent={consistent}; raw trials absent")
    out.append(dict(
        id="ext-011b", location=_loc(LAT_TEX, ln_cap),
        quote="across 16 onion services, with 10 trials per service",
        paper=(str(cap_trials) if cap_trials is not None else "not found in tex"),
        computed=cmp11b, status=st11b,
        note="Trials per service cannot be verified (raw trials absent); only textual "
             "consistency with the methodology paragraph is checked, and a disagreement "
             "is reported as FAIL."))

    # ---- ext-012 .. ext-027: per-service means ------------------------------
    prose_lo = float(app_rng[0]) if app_rng else None
    prose_hi = float(app_rng[1]) if app_rng else None
    disc_lo = float(disc_rng[0]) if disc_rng else None
    disc_hi = float(disc_rng[1]) if disc_rng else None
    for name, quote in LAT_ROW_QUOTES:
        cid = LAT_ROW_IDS[name]
        mq = re.search(r"&\s*([0-9]+\.[0-9]+)\s*\\\\", quote)
        extraction_literal = mq.group(1) if mq else None
        r = by_name.get(name)
        if r is None:
            out.append(dict(
                id=cid, location=_loc(LAT_TEX, None), quote=quote,
                paper="row not found in tex", computed="n/a", status="UNVERIFIABLE",
                note="Row could not be parsed from the current .tex."))
            continue
        cell = r[2]
        v = float(cell)
        parts = [f"tex={cell}"]
        status = "UNVERIFIABLE"
        notes = ["Raw per-trial latencies not in project; the mean itself is unverifiable."]
        if prose_lo is not None:
            in_prose = prose_lo <= v <= prose_hi
            parts.append(f"inside prose range [{app_rng[0]},{app_rng[1]}]={in_prose}")
            if not in_prose:
                status = "FAIL"
                notes.append("Cell lies outside the range stated in the Results prose.")
        else:
            parts.append("prose range not found")
        if disc_lo is not None:
            in_disc = disc_lo <= v <= disc_hi
            parts.append(f"inside Discussion range [{disc_rng[0]},{disc_rng[1]}]={in_disc}")
            if not in_disc:
                status = "FAIL"
                notes.append("Cell lies outside the range restated in the Discussion.")
        else:
            parts.append("Discussion range not found")
        parts.append("raw trials absent")
        if extraction_literal is not None and cell != extraction_literal:
            status = "FAIL"
            notes.append(f"Extraction stale: quote literal {extraction_literal} does not "
                         f"match the current tex cell {cell}; re-extract the claim.")
        if prose_lo is not None and v == prose_lo:
            notes.append("Equals the stated minimum.")
        elif prose_hi is not None and v == prose_hi:
            notes.append("Equals the stated maximum.")
        out.append(dict(
            id=cid, location=_loc(LAT_TEX, r[3]), quote=quote,
            paper=cell, computed="; ".join(parts), status=status, note=" ".join(notes)))

    # ---- ext-028 .. ext-034: Onionoo snapshot -------------------------------
    ln_snap, m_snap = _find_first(rel_clean, RE_DATE_SNAPSHOT)
    snapshot_date = m_snap.group(1) if m_snap else None
    date_hits = _lines_containing(rel_clean, snapshot_date) if snapshot_date else []
    other_dates = sorted({m.group(1) for _, m in _find_all(rel_clean, RE_DATE)}
                         - ({snapshot_date} if snapshot_date else set()))
    date_txt = (f"'{snapshot_date}' found on lines {date_hits}"
                + (f"; other dates present: {other_dates}" if other_dates else
                   "; no other date strings in the file")
                if snapshot_date else "snapshot date sentence not found in tex")
    pct_hits = [(ln, m.group(1)) for ln, m in _find_all(rel_clean, RE_PCT75)]
    pct_vals = sorted({p for _, p in pct_hits})
    pct_txt = (f"percentage mentions: {[(ln, p + '%') for ln, p in pct_hits]}"
               + ("; all mentions agree" if len(pct_vals) == 1 else
                  f"; DISAGREE: {pct_vals}" if pct_vals else ""))
    pct_paper = (pct_vals[0] + "%" if len(pct_vals) == 1 else
                 ("/".join(p + "%" for p in pct_vals) if pct_vals else "not found in tex"))
    date_paper = snapshot_date or "not found in tex"
    ln_cap_dist = next((ln for ln in date_hits if any(
        "Geographic distribution" in txt for l2, txt in rel_clean if l2 == ln)), None)
    ln_cap_prob = next((ln for ln in date_hits if any(
        "Aggregate guard and middle" in txt for l2, txt in rel_clean if l2 == ln)), None)
    ln_pct_prose = next((ln for ln, _ in pct_hits if ln != ln_cap_prob), None)

    out.append(dict(
        id="ext-028", location=_loc(REL_TEX, ln_snap),
        quote="We obtain a snapshot of the public Tor relay network from Onionoo on 30 November 2025.",
        paper=date_paper, computed="n/a (snapshot file absent)",
        status="UNVERIFIABLE",
        note=("Onionoo snapshot not in the project (repro/README: only a revision log). "
              "Recipe: read the snapshot's relays_published timestamp and compare its date. "
              f"Textual consistency (whole file searched): {date_txt}.")))

    ln_share = next((ln for ln, txt in rel_clean if "substantial share" in txt), None)
    out.append(dict(
        id="ext-029", location=_loc(REL_TEX, ln_share),
        quote="Germany, the United States, and the Netherlands account for a substantial share of the observed relay population.",
        paper="DE, US, NL: substantial share", computed="n/a (snapshot file absent)",
        status="UNVERIFIABLE",
        note="Recipe: count running relays by 'country'; check that each of de/us/nl is "
             "among the largest country counts and report their combined share "
             "(figures/tor_top15_countries.png is derived from the snapshot)."))

    ln_agg = next((ln for ln, txt in rel_clean if "more relays than all remaining" in txt), None)
    out.append(dict(
        id="ext-030", location=_loc(REL_TEX, ln_agg),
        quote="In aggregate, Fourteen-Eyes jurisdictions host more relays than all remaining jurisdictions combined.",
        paper=">50% of relay count", computed="n/a (snapshot file absent)",
        status="UNVERIFIABLE",
        note=("Recipe: count(country in 14-Eyes)/count(all) > 0.5 with 14-Eyes = "
              f"{{{', '.join(FOURTEEN_EYES)}}}.")))

    out.append(dict(
        id="ext-031", location=_loc(REL_TEX, ln_pct_prose),
        quote="Approximately $75\\%$ of both the guard and the middle selection-probability mass",
        paper=pct_paper, computed="n/a (snapshot file absent)",
        status="UNVERIFIABLE",
        note="Recipe, on the Onionoo snapshot's per-relay guard_probability / "
             "middle_probability (not part of the released dataset): "
             "sum(guard_probability | country in 14-Eyes)/sum(guard_probability) and the same "
             f"for middle_probability; both ~{pct_paper} (figures/14_eyes_probabilities.png). "
             f"Textual: {pct_txt}."))

    ln_most = next((ln for ln, txt in rel_clean if "sits inside a single grouping" in txt), None)
    out.append(dict(
        id="ext-032", location=_loc(REL_TEX, ln_most),
        quote="most of the weight at each of these two positions sits inside a single grouping",
        paper=">50% at both positions", computed="n/a (snapshot file absent)",
        status="UNVERIFIABLE",
        note=f"Implied by ext-031 ({pct_paper} > 50%) but needs the snapshot to confirm."))

    out.append(dict(
        id="ext-033", location=_loc(REL_TEX, ln_cap_dist),
        quote="Geographic distribution of Tor relays in the 30 November 2025 Onionoo snapshot.",
        paper=date_paper,
        computed=(f"date string lines: {date_hits}; caption line "
                  f"{'present' if ln_cap_dist in date_hits else 'absent'}"),
        status="UNVERIFIABLE",
        note=f"Externally unverifiable (snapshot absent); textual consistency: {date_txt}."))

    out.append(dict(
        id="ext-034", location=_loc(REL_TEX, ln_cap_prob),
        quote="in the 30 November 2025 Onionoo snapshot. Approximately $75\\%$ of the probability mass for both positions lies within Fourteen-Eyes jurisdictions.",
        paper=f"{date_paper}; {pct_paper}",
        computed=(f"date string lines: {date_hits}; caption line "
                  f"{'present' if ln_cap_prob in date_hits else 'absent'}; {pct_txt}"),
        status="UNVERIFIABLE",
        note="Needs the snapshot (same recipe as ext-031); textual consistency of the "
             "date and percentage across all mentions is reported in 'computed'."))

    # sanity: unique ids, expected count
    ids = [c["id"] for c in out]
    assert len(ids) == len(set(ids)) == 35, f"claim ids not unique/complete: {ids}"
    return out

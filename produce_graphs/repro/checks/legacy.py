"""Disposition of the OLD verify.py claim registry (module 'legacy').

The original verify.py carried 22 hand-written claims for an earlier draft.
Every one of them was re-checked against the CURRENT .tex (comment blocks and
%-lines ignored) and is either

  * COVERED  - the same printed number is still in the paper and a checks/
               module now recomputes it (id listed in COVERED_BY); or
  * DROPPED  - the text/table it referred to no longer exists in the paper
               (listed in DROPPED with the grep evidence).

claims() therefore emits no positive claim of its own.  It does two guard
jobs so this file cannot go stale silently:

  1. verify.py asserts that every id named in COVERED_BY is produced by some
     module in this run (a renamed/deleted id becomes a FAIL row);
  2. for every DROPPED entry, this module greps the current paper for the
     pattern that would signal the text has come back; if it has, a FAIL row
     asks for the check to be re-added.
"""
from __future__ import annotations

import re

import core as _core

# old claim name  ->  ids of the module claims that now cover it
COVERED_BY = {
    "stages converge (36/36)":            ["conv-006"],
    "runs reconstructed (9/9)":           ["conv-001", "conv-005", "conv-024"],
    "median introductions per run":       ["conv-007"],
    "min introductions per run":          ["conv-007"],
    "max introductions per run":          ["conv-007"],
    "median hours":                       ["time-006", "e2e-010"],
    "min hours":                          ["e2e-009"],          # 0.87 h appears only in tab:end_to_end
    "max hours":                          ["time-006", "e2e-006"],
    "median % of 18h lifetime":           ["time-007"],
    "max % of 18h lifetime":              ["time-007"],
    "median T_conv IP/M1/VG/EG":          ["e2e-010"],          # Median row of tab:end_to_end
    "run-stage threshold rows match":     ["app-001"],          # plus app-002..app-037 row by row
    "median T_<=10 across 36 stages":     ["conv-008"],
    "fraction reaching |I|<=10 within 5": ["conv-009"],
    "RQ2 IP example (runs 1/4/6 T_conv)": ["conv-019"],
    "Appendix E N_g,N_m and combinations": ["ext-028", "ext-029", "ext-030"],
    "~75% Fourteen-Eyes prob. mass":      ["ext-031", "ext-034"],
}

# old claim name -> (tex file(s) to grep, regex that would mean the text is back, reason dropped)
DROPPED = {
    "SD T_conv IP/M1/VG/EG (Table 3 tab:stage_context)": (
        ["sections/04-setup-and-evaluation.tex", "sections/05-discussion.tex",
         "sections/appendix_results.tex"],
        r"tab:stage_context|126\.3|85\.5|59\.4|standard deviation",
        "the stage-context table with per-stage SD (126.3/15.0/85.5/59.4) is not in the "
        "current paper; only tab:end_to_end and tab:stage-contrasts remain "
        "(grep of the active .tex finds none of those values)."),
}


def claims(C, traj, metrics):
    out = []
    for name, (files, pattern, reason) in DROPPED.items():
        rx = re.compile(pattern)
        hits = []
        for rel in files:
            for ln, txt in _core.tex_active(rel):
                if rx.search(txt):
                    hits.append(f"{rel}:{ln}")
        if hits:
            out.append(_core.claim(
                "legacy-dropped", hits[0], name, "-", f"pattern {pattern!r} found at {hits}",
                "FAIL", f"a check dropped from the old registry ({reason}) matches the current "
                        "text again; re-add it to a checks/ module."))
    return out

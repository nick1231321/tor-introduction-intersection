# Manual verification checklist

For each claim: the sentence or table row as printed in the paper (search for it in the PDF),
the value printed there, and the value recomputed from `data/` by `make verify`.
PASS = recomputed value equals the printed one; FROZEN = a textual/structural check that
passed against the paper sources when the snapshot was taken and cannot be recomputed from
data/ alone; CONSTANT = protocol/implementation constant; UNVERIFIABLE = input not part of
the released data (reason given).

PASS 120, FAIL 0, FROZEN 25, UNVERIFIABLE 29, CONSTANT 49; total 223

## main.tex

- **const-001** — CONSTANT
  - says: "client circuits typically last only about 10 min"
  - printed: 10
  - recomputed: 10
  - note: CONSTANT: Tor default MaxCircuitDirtiness = 600 s = 10 min (tor(1) manual).

- **const-002** — CONSTANT
  - says: "remain fixed for 18-24 h"
  - printed: 18-24
  - recomputed: 18--24
  - note: CONSTANT: Tor rend-spec-v3 / hs_circuit INTRO_POINT_LIFETIME_MIN_SECONDS = 18 h, MAX = 24 h; cited platzer2020critical.

- **setup-001** — PASS
  - says: "Across nine end-to-end experiments"
  - printed: nine
  - recomputed: 9 runs in TRAJ (raw ids 4..12), 9 in MET

- **conv-001** — PASS
  - says: "the attack reconstructs the complete Tor circuit in every run"
  - printed: every run (9 of 9)
  - recomputed: 9 of 9 runs converged at all 4 stages (36/36 stages reach |I|=1)

- **time-001** — PASS
  - says: "with an estimated median time of 2.2 h."
  - printed: 2.2
  - recomputed: 2.2

## sections/01-introduction.tex

- **const-003** — CONSTANT
  - says: "enabling millions of users to conceal their sensitive Internet activities"
  - printed: millions
  - recomputed: millions
  - note: CONSTANT: Tor Metrics daily-user estimates (~2M directly connecting users); order-of-magnitude cited figure.

- **const-004** — CONSTANT
  - says: "For an adversary limited to monitoring one relay at a time"
  - printed: one
  - recomputed: one
  - note: CONSTANT: threat-model assumption defined by the paper (sections/03-attack.tex:297).

- **const-005** — CONSTANT
  - says: "typically last at most about 10 min"
  - printed: 10
  - recomputed: 10
  - note: CONSTANT: Tor default MaxCircuitDirtiness = 600 s = 10 min (tor(1) manual). Cited erdin2015find.

- **const-006** — CONSTANT
  - says: "18-24 h"
  - printed: 18-24
  - recomputed: 18--24
  - note: CONSTANT: Tor rend-spec-v3 / hs_circuit INTRO_POINT_LIFETIME_MIN_SECONDS = 18 h, MAX = 24 h; cited platzer2020critical.

- **const-007** — CONSTANT
  - says: "only one Tor relay at a time an extended window"
  - printed: one
  - recomputed: one
  - note: CONSTANT: threat-model assumption defined by the paper (sections/03-attack.tex:297).

- **const-008** — CONSTANT
  - says: "We consider an adversary that monitors one relay at a time, chosen adaptively:"
  - printed: one
  - recomputed: one
  - note: CONSTANT: threat-model assumption defined by the paper (sections/03-attack.tex:297).

- **conv-002** — PASS
  - says: "complete target path in all nine experiments (Section [ref])."
  - printed: nine (all nine)
  - recomputed: 9 of 9 runs converged at all 4 stages (36/36 stages reach |I|=1)

## sections/02-background.tex

- **const-009** — CONSTANT
  - says: "chosen from a fixed set of four layer-2 vanguards,"
  - printed: four
  - recomputed: four
  - note: CONSTANT: Tor proposal 333 (Vanguards-Lite) NUM_LAYER2_GUARDS = 4.

- **const-010** — CONSTANT
  - says: "each kept for a random period of 1-12 days."
  - printed: 1-12
  - recomputed: 1--12
  - note: CONSTANT: Tor proposal 333 layer-2 guard lifetime: min 1 day, max 12 days.

- **const-011** — CONSTANT
  - says: "The optional Full Vanguards mode also fixes the third relay."
  - printed: third
  - recomputed: third
  - note: CONSTANT: vanguards add-on specification (layer-3 guards pin the third hop).

- **const-012** — CONSTANT
  - says: "three by default, as its Introduction Points (IntPs)."
  - printed: three
  - recomputed: three
  - note: CONSTANT: Tor HiddenServiceNumIntroductionPoints default = 3 (rend-spec-v3).

## sections/03-attack.tex

- **const-013** — CONSTANT
  - says: "ordinary Tor circuits are typically used for about 10 min"
  - printed: 10
  - recomputed: 10
  - note: CONSTANT: Tor default MaxCircuitDirtiness = 600 s = 10 min (tor(1) manual).

- **const-014** — CONSTANT
  - says: "for 18-24 h"
  - printed: 18-24
  - recomputed: 18--24
  - note: CONSTANT: Tor rend-spec-v3 / hs_circuit INTRO_POINT_LIFETIME_MIN_SECONDS = 18 h, MAX = 24 h; cited platzer2020critical.

- **const-015** — CONSTANT
  - says: "(iii) observes at most one Tor relay at a time"
  - printed: one
  - recomputed: one
  - note: CONSTANT: threat-model assumption defined by the paper (sections/03-attack.tex:297).

- **const-016** — CONSTANT
  - says: "An onion service's introduction circuit consists of four relays"
  - printed: four
  - recomputed: 4 distinct stage codes in MET/TRAJ (EG, IP, M1, VG)
  - note: CONSTANT: Tor vanguards spec (guard, L2, L3/middle, IntP); structurally mirrored by the distinct stage codes in the data (see setup-003).

- **const-017** — CONSTANT
  - says: "service \to entry guard \to layer-2 vanguard \to middle relay \to Introduction Point. Under the optional Full Vanguards configuration, a layer-3 vanguard replaces the middle relay"
  - printed: layer-2 / layer-3
  - recomputed: layer-2 / layer-3
  - note: CONSTANT: Tor proposal 333 (Vanguards-Lite: L2 pinned, middle free) / vanguards add-on (Full Vanguards: L2 and L3 pinned).

- **setup-002** — PASS
  - says: "Reconstruction therefore requires K=4 stages in both configurations"
  - printed: 4
  - recomputed: 4 stage codes per run in TRAJ, 4 in MET (codes ['EG', 'IP', 'M1', 'VG'])

- **setup-003** — PASS
  - says: "r_m_0,\ldots,r_m_3 denote the Introduction Point, the middle relay or layer-3 vanguard, the layer-2 vanguard, and the entry guard"
  - printed: 0..3 = IP,M1,VG,EG
  - recomputed: IP<M1<VG<EG by (experiment_date, experiment_time_utc) in all 9 runs

- **const-018** — CONSTANT
  - says: "From stage 1 onward, r_m_i receives the introduction cell from its predecessor"
  - printed: 1
  - recomputed: 1
  - note: CONSTANT: algorithm definition (Alg. reconstruction, predecessor-exclusion step); not data-derived. Restated at implementation.tex:101 (const-034).

- **const-019** — CONSTANT
  - says: "Tor's general rule against placing two relays from the same /16 subnet on a circuit"
  - printed: /16; two
  - recomputed: /16; two
  - note: CONSTANT: Tor path-spec section 2.2 (EnforceDistinctSubnets), relaxed for HS circuits by proposal 333.

- **const-020** — CONSTANT
  - says: "the adversary builds a new client-side circuit for each iteration"
  - printed: one per iteration
  - recomputed: one per iteration
  - note: CONSTANT: implementation description (fresh Tor client per iteration, implementation.tex:32); not recorded in the CSVs.

- **conv-003** — PASS
  - says: "Stage i converges at the first iteration j for which |I_i^(j)|=1."
  - printed: 1
  - recomputed: all 36 stages: T<=1(seq) == len(seq) and seq[-1]==1

- **time-005** — FROZEN
  - says: "Each window spans a single handshake, lasting approximately one second"
  - printed: one second (approx.)
  - recomputed: appendix-table:1 s
  - note: textual/structural check; verified against the paper sources when the snapshot was taken, not recomputable from data/ alone; PAPER-INTERNAL, same basis as time-004: mean 0.898 s of the 16 appendix values; raw per-trial data absent. [quote verified in current tex]

- **const-021** — CONSTANT
  - says: "after approximately 10 min in ordinary Tor"
  - printed: 10
  - recomputed: 10
  - note: CONSTANT: Tor default MaxCircuitDirtiness = 600 s = 10 min (tor(1) manual).

- **const-022** — CONSTANT
  - says: "population turns over approximately 2.5 times per day"
  - printed: 2.5
  - recomputed: 2.5
  - note: CONSTANT: cited jansen2016safely (Safely Measuring Tor, CCS 2016).

- **setup-004** — PASS
  - says: "number of stages K (K=4 for a service-side introduction circuit)"
  - printed: 4
  - recomputed: 4 stage codes per run in TRAJ, 4 in MET (codes ['EG', 'IP', 'M1', 'VG'])

- **conv-004** — PASS
  - says: "\If|I_i| = 0"
  - printed: 0
  - recomputed: min(intersection_size) = 1 over 2771 rows

- **setup-005** — FROZEN
  - says: "reconstruction relies on three assumptions."
  - printed: three
  - recomputed: 3 enumerated (First, Second, Third)
  - note: textual/structural check; verified against the paper sources when the snapshot was taken, not recomputable from data/ alone; Textual count of 'First,/Second,/Third,' sentence starters in the paragraph containing the anchor (found at sections/03-attack.tex:580).

## sections/04-setup-and-evaluation.tex

- **setup-006** — PASS
  - says: "we ran Algorithm [ref] nine times on the live Tor network"
  - printed: nine
  - recomputed: 9 runs in TRAJ (raw ids 4..12), 9 in MET

- **setup-007** — PASS
  - says: "we pinned the service's introduction circuit to four public Tor relays of ours"
  - printed: four
  - recomputed: 4 stage codes per run in TRAJ, 4 in MET (codes ['EG', 'IP', 'M1', 'VG'])

- **ext-001** — UNVERIFIABLE
  - says: "The relays had been active for 69-126 days when the experiments began"
  - printed: 69-126
  - recomputed: n/a (no relay first_seen in metrics)
  - note: Needs Onionoo first_seen for the four operated relays; recipe: (2026-01-07 - first_seen).days for each relay, expect min/max = 69--126. Experiment start = min(experiment_date) over run_stage_metrics.csv = 2026-01-07. run_stage_metrics.csv has no fingerprint/first_seen column.

- **setup-008** — PASS
  - says: "T_<= q=min\j:|I_i^(j)|<= q\ for q\in\10,3,2\"
  - printed: 10, 3, 2
  - recomputed: T<=q = first trial with |I_t|<=q from TRAJ: defined for 36/36 run-stages and all three q, T<=10 <= T<=3 <= T<=2 in 36/36

- **setup-009** — FROZEN
  - says: "The monitored relay runs four processes: (i) a capture process"
  - printed: four
  - recomputed: 5 component rows in tab:impl-components, 4 on the monitored relay; 4 enumerated processes (i)..(iv) in the paragraph
  - note: textual/structural check; verified against the paper sources when the snapshot was taken, not recomputable from data/ alone; Textual consistency: table rows minus the Onion-service daemon row (service host) and the (i)-(iv) enumeration in the paragraph at sections/04-setup-and-evaluation.tex:315.

- **const-046** — CONSTANT
  - says: "The controller relaunches the client after \delta=30 s"
  - printed: 30
  - recomputed: tex: None; implementation.tex (const-035 sentence) says None
  - note: CONSTANT: implementation parameter (same as const-035); textual check only that it equals the implementation.tex statement.

- **conv-005** — PASS
  - says: "Across the nine end-to-end experiments, the attack successfully reconstructed the complete introduction path in every run."
  - printed: nine (9 of 9 succeeded)
  - recomputed: 9 of 9 runs converged at all 4 stages (36/36 stages reach |I|=1)

- **conv-006** — PASS
  - says: "All 36 stages converged to the correct successor."
  - printed: 36
  - recomputed: 36 of 36 stages end at |I|=1

- **conv-007** — PASS
  - says: "median of 260 iterations, ranging from 101 to 770 iterations across runs"
  - printed: 260; 101; 770
  - recomputed: median=260; min=101; max=770 [N per run: R1(raw 4)=382, R2(raw 5)=131, R3(raw 6)=260, R4(raw 7)=152, R5(raw 8)=504, R6(raw 9)=770, R7(raw 10)=211, R8(raw 11)=260, R9(raw 12)=101]

- **time-002** — CONSTANT
  - says: "T=(31 s)N+4v,"
  - printed: 31; 4
  - recomputed: n/a; 4
  - note: 31 derived as delta 30 s + round(mean handshake 0.898 s) = 31; core.SECONDS_PER_ITER = 31; 4 = number of stages K = len(core.STAGES) = 4. [quote verified in current tex]

- **setup-010** — PASS
  - says: "where N is the total number of iterations across the four stages"
  - printed: four
  - recomputed: 4 stage codes per run in TRAJ, 4 in MET (codes ['EG', 'IP', 'M1', 'VG'])

- **time-003** — CONSTANT
  - says: "The 31 s iteration cost consists of the \delta=30 s delay between iterations in our experimental setup and approximately 1 s for the introduction handshake itself."
  - printed: 31; 30; 1
  - recomputed: 31; 30; 1
  - note: arithmetic 30 + 1 = 31; 30 s is the implementation parameter delta; handshake ~1 s is PAPER-INTERNAL (appendix table, raw per-trial data absent): n=16, mean=0.898 s, median=0.838 s. [quote verified in current tex]

- **const-047** — CONSTANT
  - says: "The 30 s delay is a configurable parameter of our implementation"
  - printed: 30
  - recomputed: tex: None; const-046 sentence says None; implementation.tex says None
  - note: CONSTANT: implementation parameter; textual check that it equals const-035/046.

- **time-004** — FROZEN
  - says: "approximately 1 s handshake duration is based on measurements of public onion services reported in Appendix [ref]"
  - printed: 1
  - recomputed: appendix-table:1
  - note: textual/structural check; verified against the paper sources when the snapshot was taken, not recomputable from data/ alone; PAPER-INTERNAL consistency (appendix table vs. text), not raw data: mean of the 16 printed Avg dt values = 0.898 s, median = 0.838 s, range [0.521, 1.780] s; 'approximately 1 s' = mean rounded to 0 dp. The 160 raw per-trial handshake measurements are not in the repository. [quote verified in current tex]

- **time-006** — PASS
  - says: "when v=0, the median reconstruction takes 2.24 h and the slowest takes 6.63 h."
  - printed: 2.24; 6.63
  - recomputed: 2.24; 6.63

- **time-007** — PASS
  - says: "correspond to approximately 12% and 37%, respectively, of 18 h"
  - printed: 12%; 37%; 18
  - recomputed: 12%; 37%; 18

- **const-023** — CONSTANT
  - says: "the lower end of the introduction circuit's 18-24 h lifetime"
  - printed: 18-24
  - recomputed: 18--24
  - note: [moved from sections/04-setup-and-evaluation.tex:392] CONSTANT: Tor rend-spec-v3 / hs_circuit INTRO_POINT_LIFETIME_MIN_SECONDS = 18 h, MAX = 24 h; cited platzer2020critical.

- **const-024** — CONSTANT
  - says: "reconstruction still completes within 18 h"
  - printed: 18
  - recomputed: 18
  - note: [moved from sections/04-setup-and-evaluation.tex:396] CONSTANT: definitional; 18 h = lower end of the Tor intro-circuit lifetime (INTRO_POINT_LIFETIME_MIN_SECONDS).

- **time-008** — PASS
  - says: "The median run permits v_max=3.94 h per relay"
  - printed: 3.94
  - recomputed: 3.94

- **time-009** — PASS
  - says: "the most iteration-intensive run, experiment 6, permits 2.84 h."
  - printed: 6; 2.84
  - recomputed: 6; 2.84

- **time-010** — PASS
  - says: "At v=4 h, five of the nine runs exceed the 18 h bound."
  - printed: five of nine; 4; 18
  - recomputed: 5 of 9; 4; 18

- **time-011** — PASS
  - says: "visibility accounts for approximately 64% of the total time at v=1 h and 88% at v=4 h."
  - printed: 64%; 88%
  - recomputed: 64%; 88%

- **time-012** — PASS
  - says: "v_max ranges from 2.84 to 4.28 h despite a more than sevenfold difference in total iteration counts."
  - printed: 2.84-4.28; sevenfold
  - recomputed: 2.84--4.28; 7.62-fold

- **setup-011** — FROZEN
  - says: "End-to-end reconstruction cost across the nine experiments"
  - printed: nine
  - recomputed: 9 runs in TRAJ (raw ids 4..12), 9 in MET; 9 data rows in tab:end_to_end
  - note: textual/structural check; verified against the paper sources when the snapshot was taken, not recomputable from data/ alone; [moved from sections/04-setup-and-evaluation.tex:416]; Same test as setup-001 plus count of numbered data rows between the \midrule markers of the end-to-end table.

- **setup-012** — UNVERIFIABLE
  - says: "Total is the sum N across the four stages."
  - printed: four
  - recomputed: 4 stage codes per run in TRAJ, 4 in MET (codes ['EG', 'IP', 'M1', 'VG'])
  - note: sentence removed from the paper (tab:end_to_end caption shortened; location = the current caption); the four-stage count is still verified by setup-010 and setup-020; Same test as setup-002.

- **time-013** — FROZEN
  - says: "costs v (bold: exceeds 18 h)."
  - printed: 18
  - recomputed: bold cells: 6; cells with T>18: 6
  - note: textual/structural check; verified against the paper sources when the snapshot was taken, not recomputable from data/ alone; checked 30 T cells + 10 v_max cells in tab:end_to_end against T=31N/3600+4v; bold <=> T>18; max T at v<=1 is 10.63 h. [moved from sections/04-setup-and-evaluation.tex:421] [quote verified in current tex]

- **e2e-001** — PASS
  - says: "Table tab:end_to_end row 1 (1 & 285 (830) & ...)"
  - printed: 285 (830); 5 (5000); 61 (1200); 31 (9300); 382; 3.29; 7.29; 19.29; 3.68
  - recomputed: 285 (830); 5 (5000); 61 (1200); 31 (9300); 382; 3.29; 7.29; 19.29; 3.68

- **e2e-002** — PASS
  - says: "Table tab:end_to_end row 2 (2 & 52 (850) & ...)"
  - printed: 52 (850); 13 (5000); 4 (1200); 62 (9300); 131; 1.13; 5.13; 17.13; 4.22
  - recomputed: 52 (850); 13 (5000); 4 (1200); 62 (9300); 131; 1.13; 5.13; 17.13; 4.22

- **e2e-003** — PASS
  - says: "Table tab:end_to_end row 3 (3 & 163 (850) & ...)"
  - printed: 163 (850); 7 (4000); 12 (1200); 78 (9300); 260; 2.24; 6.24; 18.24; 3.94
  - recomputed: 163 (850); 7 (4000); 12 (1200); 78 (9300); 260; 2.24; 6.24; 18.24; 3.94

- **e2e-004** — PASS
  - says: "Table tab:end_to_end row 4 (4 & 8 (850) & ...)"
  - printed: 8 (850); 11 (4000); 10 (1200); 123 (9900); 152; 1.31; 5.31; 17.31; 4.17
  - recomputed: 8 (850); 11 (4000); 10 (1200); 123 (9900); 152; 1.31; 5.31; 17.31; 4.17

- **e2e-005** — PASS
  - says: "Table tab:end_to_end row 5 (5 & 178 (1500) & ...)"
  - printed: 178 (1500); 17 (4100); 142 (1200); 167 (4800); 504; 4.34; 8.34; 20.34; 3.42
  - recomputed: 178 (1500); 17 (4100); 142 (1200); 167 (4800); 504; 4.34; 8.34; 20.34; 3.42

- **e2e-006** — PASS
  - says: "Table tab:end_to_end row 6 (6 & 324 (1400) & ...)"
  - printed: 324 (1400); 10 (4100); 251 (1200); 185 (4800); 770; 6.63; 10.63; 22.63; 2.84
  - recomputed: 324 (1400); 10 (4100); 251 (1200); 185 (4800); 770; 6.63; 10.63; 22.63; 2.84

- **e2e-007** — PASS
  - says: "Table tab:end_to_end row 7 (7 & 11 (1900) & ...)"
  - printed: 11 (1900); 10 (4800); 24 (1300); 166 (4800); 211; 1.82; 5.82; 17.82; 4.05
  - recomputed: 11 (1900); 10 (4800); 24 (1300); 166 (4800); 211; 1.82; 5.82; 17.82; 4.05

- **e2e-008** — PASS
  - says: "Table tab:end_to_end row 8 (8 & 8 (1900) & ...)"
  - printed: 8 (1900); 53 (4800); 6 (1300); 193 (4800); 260; 2.24; 6.24; 18.24; 3.94
  - recomputed: 8 (1900); 53 (4800); 6 (1300); 193 (4800); 260; 2.24; 6.24; 18.24; 3.94

- **e2e-009** — PASS
  - says: "Table tab:end_to_end row 9 (9 & 10 (2000) & ...)"
  - printed: 10 (2000); 4 (4800); 3 (1300); 84 (4400); 101; 0.87; 4.87; 16.87; 4.28
  - recomputed: 10 (2000); 4 (4800); 3 (1300); 84 (4400); 101; 0.87; 4.87; 16.87; 4.28

- **e2e-010** — PASS
  - says: "Table tab:end_to_end Median row (Median & 52 & 10 & ...)"
  - printed: 52; 10; 12; 123; 260; 2.24; 6.24; 18.24; 3.94
  - recomputed: 52; 10; 12; 123; 260; 2.24; 6.24; 18.24; 3.94

- **contr-body** — FROZEN
  - says: ""
  - printed: 11 body lines
  - recomputed: 11 body lines from generate.py
  - note: textual/structural check; verified against the paper sources when the snapshot was taken, not recomputable from data/ alone; tabular body of tab:stage-contrasts equals repro/out/tables/stage_contrasts_body.tex (make tables) modulo whitespace

- **contr-sel-EG** — PASS
  - says: "rows shown for Entry Guard"
  - printed: R1,R4,R6,R8
  - recomputed: R1,R4,R6,R8

- **contr-sel-IP** — PASS
  - says: "rows shown for Introduction Point"
  - printed: R4,R2,R1,R6
  - recomputed: R4,R2,R1,R6

- **contr-sel-M1** — PASS
  - says: "rows shown for Middle 1"
  - printed: R9,R6,R5,R8
  - recomputed: R9,R6,R5,R8

- **contr-sel-VG** — PASS
  - says: "rows shown for Vanguard"
  - printed: R9,R3,R5,R6
  - recomputed: R9,R3,R5,R6

- **contr-001** — PASS
  - says: "R4 D2 02:00 (Introduction Point)"
  - printed: R4; D2 02:00; 850; 81; 3; 4; 4; 8
  - recomputed: R4; D2 02:00; 850; 81; 3; 4; 4; 8

- **contr-002** — PASS
  - says: "R9 D4 10:00 (Vanguard)"
  - printed: R9; D4 10:00; 1300; 48; 2; 3; 3; 3
  - recomputed: R9; D4 10:00; 1300; 48; 2; 3; 3; 3

- **contr-003** — PASS
  - says: "R2 D1 10:00 (Introduction Point)"
  - printed: R2; D1 10:00; 850; 101; 2; 9; 52; 52
  - recomputed: R2; D1 10:00; 850; 101; 2; 9; 52; 52

- **contr-004** — PASS
  - says: "R3 D1 18:00 (Vanguard)"
  - printed: R3; D1 18:00; 1200; 85; 2; 4; 12; 12
  - recomputed: R3; D1 18:00; 1200; 85; 2; 4; 12; 12

- **contr-005** — PASS
  - says: "R1 D1 02:00 (Introduction Point)"
  - printed: R1; D1 02:00; 830; 79; 3; 42; 245; 285
  - recomputed: R1; D1 02:00; 830; 79; 3; 42; 245; 285

- **contr-006** — PASS
  - says: "R5 D2 10:00 (Vanguard)"
  - printed: R5; D2 10:00; 1200; 148; 38; 61; 76; 142
  - recomputed: R5; D2 10:00; 1200; 148; 38; 61; 76; 142

- **contr-007** — PASS
  - says: "R6 D2 18:00 (Introduction Point)"
  - printed: R6; D2 18:00; 1400; 84; 3; 233; 324; 324
  - recomputed: R6; D2 18:00; 1400; 84; 3; 233; 324; 324

- **contr-008** — PASS
  - says: "R6 D2 18:00 (Vanguard)"
  - printed: R6; D2 18:00; 1200; 161; 11; 49; 66; 251
  - recomputed: R6; D2 18:00; 1200; 161; 11; 49; 66; 251

- **contr-009** — PASS
  - says: "R9 D4 10:00 (Middle 1)"
  - printed: R9; D4 10:00; 4800; 90; 2; 3; 3; 4
  - recomputed: R9; D4 10:00; 4800; 90; 2; 3; 3; 4

- **contr-010** — PASS
  - says: "R1 D1 02:00 (Entry Guard)"
  - printed: R1; D1 02:00; 9300; 218; 8; 16; 31; 31
  - recomputed: R1; D1 02:00; 9300; 218; 8; 16; 31; 31

- **contr-011** — PASS
  - says: "R6 D2 18:00 (Middle 1)"
  - printed: R6; D2 18:00; 4100; 147; 3; 9; 10; 10
  - recomputed: R6; D2 18:00; 4100; 147; 3; 9; 10; 10

- **contr-012** — PASS
  - says: "R4 D2 02:00 (Entry Guard)"
  - printed: R4; D2 02:00; 9900; 256; 13; 45; 49; 123
  - recomputed: R4; D2 02:00; 9900; 256; 13; 45; 49; 123

- **contr-013** — PASS
  - says: "R5 D2 10:00 (Middle 1)"
  - printed: R5; D2 10:00; 4100; 158; 6; 13; 16; 17
  - recomputed: R5; D2 10:00; 4100; 158; 6; 13; 16; 17

- **contr-014** — PASS
  - says: "R6 D2 18:00 (Entry Guard)"
  - printed: R6; D2 18:00; 4800; 98; 7; 23; 177; 185
  - recomputed: R6; D2 18:00; 4800; 98; 7; 23; 177; 185

- **contr-015** — PASS
  - says: "R8 D4 02:00 (Middle 1)"
  - printed: R8; D4 02:00; 4800; 198; 7; 14; 14; 53
  - recomputed: R8; D4 02:00; 4800; 198; 7; 14; 14; 53

- **contr-016** — PASS
  - says: "R8 D4 02:00 (Entry Guard)"
  - printed: R8; D4 02:00; 4800; 191; 16; 62; 62; 193
  - recomputed: R8; D4 02:00; 4800; 191; 16; 62; 62; 193

- **conv-008** — PASS
  - says: "the median iteration at which |I_i^(j)|<=10 was three"
  - printed: 3
  - recomputed: median(T<=10 over 36 stages) = 3

- **setup-013** — PASS
  - says: "Across the 36 stages in our empirical evaluation"
  - printed: 36
  - recomputed: 36 distinct (run,stage) in TRAJ; 36 rows in MET

- **conv-009** — PASS
  - says: "and 64% of stages reached this threshold within five iterations"
  - printed: 64%
  - recomputed: 23/36 = 63.89% -> 64%

- **conv-010** — PASS
  - says: "candidate set shrank by 72-87% after the first intersection"
  - printed: 72-87%
  - recomputed: 72--87% [per stage: IP 82.7, M1 79.7, VG 87.4, EG 72.2]

- **conv-011** — PASS
  - says: "and by 85-96% by the third iteration, depending on the stage"
  - printed: 85-96%
  - recomputed: 85--96% [per stage: IP 91.4, M1 92.6, VG 95.8, EG 85.4]

- **ext-002** — FROZEN
  - says: "complete in 0.521-1.780 s, depending on the service"
  - printed: 0.521-1.780
  - recomputed: 0.521--1.780
  - note: textual/structural check; verified against the paper sources when the snapshot was taken, not recomputable from data/ alone; [moved from sections/05-discussion.tex] Range parsed from sections/04-setup-and-evaluation.tex at run time and compared with the min/max of the 16 Avg dt cells parsed from sections/appendix_time_of_introduction_handshake_completion.tex (min=BMG, max=Black Cloud). Raw per-trial latencies are not in the project, so the means themselves are unverifiable.

- **conv-012** — PASS
  - says: "three of the six Vanguard stages at CW 1200"
  - printed: 1200; 6
  - recomputed: 6 Vanguard stages at CW 1200 in MET [raw 4 (R1): Tconv=61, raw 5 (R2): Tconv=4, raw 6 (R3): Tconv=12, raw 7 (R4): Tconv=10, raw 8 (R5): Tconv=142, raw 9 (R6): Tconv=251]

- **conv-013** — PASS
  - says: "converged after 12, 142, and 251 iterations"
  - printed: 12, 142, 251
  - recomputed: 12, 142, 251 [Tconv(VG) of raw 6, 8, 9 = R3, R5, R6]

- **conv-014** — PASS
  - says: "two of the three Middle stages at CW 4800"
  - printed: 4800; 3
  - recomputed: 3 Middle stages at CW 4800 in MET [raw 10 (R7): Tconv=10, raw 11 (R8): Tconv=53, raw 12 (R9): Tconv=4]

- **conv-015** — PASS
  - says: "required 4 and 53"
  - printed: 4, 53
  - recomputed: 4, 53 [Tconv(M1) of raw 12, 11 = R9, R8]

- **conv-016** — PASS
  - says: "the Introduction Point stages of Runs 1, 4, and 6 started with similar sets of 79-84 candidates"
  - printed: 1, 4, 6
  - recomputed: runs with |A1|(IP) in [79,84]: [4, 7, 9] -> paper R1, R4, R6 [other runs: raw 5=101, raw 6=74, raw 8=101, raw 10=75, raw 11=91, raw 12=50]

- **conv-017** — PASS
  - says: "started with similar sets of 79-84 candidates"
  - printed: 79-84
  - recomputed: 79--84 [|A1| raw 4,7,9 = 79, 81, 84]

- **conv-018** — PASS
  - says: "reached |I|<=10 within three iterations"
  - printed: 3
  - recomputed: T<=10(IP) raw 4,7,9 = 3, 3, 3; all <= 3: True

- **conv-019** — PASS
  - says: "yet converged after 285, 8, and 324 iterations, respectively"
  - printed: 285, 8, 324
  - recomputed: 285, 8, 324 [Tconv(IP) raw 4, 7, 9]

- **conv-020** — PASS
  - says: "In 13 of the 36 stages the intersection still held three or more candidates at the penultimate iteration and then fell to a singleton in one step"
  - printed: 13 of 36
  - recomputed: 13 of 36 [(4,M1), (4,VG), (4,EG), (5,IP), (5,M1), (6,IP), (6,M1), (6,VG), (8,IP), (9,IP), (9,M1), (10,EG), (12,VG)]

- **conv-021** — PASS
  - says: "In seven of these the cardinality had been constant for at least ten iterations beforehand"
  - printed: 7
  - recomputed: 7 of 13 abrupt-collapse stages have plateau >= 10 [plateau lengths: (4,M1):1, (4,VG):57, (4,EG):15, (5,IP):43, (5,M1):6, (6,IP):152, (6,M1):1, (6,VG):8, (8,IP):148, (9,IP):91, (9,M1):1, (10,EG):93, (12,VG):1]

- **conv-022** — PASS
  - says: "The vanguard stage of Run 1 held six candidates for 57 iterations and converged at iteration 61"
  - printed: 6; 57; 61
  - recomputed: penultimate value=6; plateau trials 4..60 (57 trials, contiguous=True); Tconv=61

- **conv-023** — PASS
  - says: "Introduction Point stages of Runs 3 and 5 held three for 152 and 148 iterations before converging at iterations 163 and 178"
  - printed: 3; 152, 148; 163, 178
  - recomputed: value 3/3; plateau 152, 148 (raw 6: trials 11..162, raw 8: trials 30..177); Tconv 163, 178

- **setup-032** — FROZEN
  - says: "Our evaluation has two main limitations."
  - printed: 2
  - recomputed: 2 enumerated (First, Second)
  - note: textual/structural check; verified against the paper sources when the snapshot was taken, not recomputable from data/ alone; Textual count of 'First,'/'Second,' sentence starters (and absence of 'Third,') in the Limitations paragraph containing the anchor (sections/04-setup-and-evaluation.tex:584).

- **const-029** — CONSTANT
  - says: "the current 18-24 h lifetime of introduction circuits"
  - printed: 18-24
  - recomputed: 18--24
  - note: [moved from sections/05-discussion.tex:120] CONSTANT: Tor rend-spec-v3 / hs_circuit INTRO_POINT_LIFETIME_MIN_SECONDS = 18 h, MAX = 24 h; cited platzer2020critical.

## sections/05-discussion.tex

- **const-025** — CONSTANT
  - says: "Our attack exploits the 18-24 h introduction-circuit lifetime"
  - printed: 18-24
  - recomputed: 18--24
  - note: CONSTANT: Tor rend-spec-v3 / hs_circuit INTRO_POINT_LIFETIME_MIN_SECONDS = 18 h, MAX = 24 h; cited platzer2020critical.

- **const-026** — CONSTANT
  - says: "a service-side path used for only about 10 min, the lifetime of an ordinary Tor circuit"
  - printed: 10
  - recomputed: 10
  - note: CONSTANT: Tor default MaxCircuitDirtiness = 600 s = 10 min (tor(1) manual).

- **const-027** — CONSTANT
  - says: "approximately every 10 min. Relay selection remains unchanged"
  - printed: 10
  - recomputed: tex line not found
  - note: CONSTANT: proposal parameter chosen by the authors (matches MaxCircuitDirtiness); restated in the same section (const-028).

- **const-028** — CONSTANT
  - says: "even if a stage converges within a 10-minute interval"
  - printed: 10
  - recomputed: None (const-027 sentence says None)
  - note: CONSTANT: proposal parameter; textual check that it equals const-027.

## sections/06-related-work.tex

- **const-030** — CONSTANT
  - says: "traffic observed at two network vantage points and generalizes to unseen flows"
  - printed: two
  - recomputed: two
  - note: CONSTANT: property of cited work (DeepCorr, Nasr et al., CCS 2018).

## sections/07-conclusion.tex

- **const-031** — CONSTANT
  - says: "requiring visibility of only one relay at a time."
  - printed: one
  - recomputed: one
  - note: CONSTANT: threat-model assumption defined by the paper (sections/03-attack.tex:297).

- **setup-014** — PASS
  - says: "We evaluated the attack in nine end-to-end experiments against a"
  - printed: nine
  - recomputed: 9 runs in TRAJ (raw ids 4..12), 9 in MET

- **conv-024** — PASS
  - says: "Across all nine experiments, the attack successfully reconstructed"
  - printed: nine (all)
  - recomputed: 9 of 9 runs converged at all 4 stages (36/36 stages reach |I|=1)

## sections/appendix_relay_concentration.tex

- **const-038** — CONSTANT
  - says: "We consider the Fourteen Eyes as a grouping of jurisdictions"
  - printed: Fourteen (14)
  - recomputed: 0 country names enumerated at line 6
  - note: CONSTANT: cited williams2023five; count of country names in line 6 of the same file.

- **const-039** — CONSTANT
  - says: "Australia, Belgium, Canada, Denmark, France, Germany, Italy, the Netherlands, New Zealand, Norway, Spain, Sweden, the United Kingdom, or the United States"
  - printed: 14 countries listed
  - recomputed: enumeration not found
  - note: CONSTANT: list definition; textual check splits the enumeration on commas/'or' and counts.

- **ext-028** — UNVERIFIABLE
  - says: "We obtain a snapshot of the public Tor relay network from Onionoo on 30 November 2025."
  - printed: 30 November 2025
  - recomputed: n/a (snapshot file absent)
  - note: Onionoo snapshot not in the project (repro/README: only a revision log). Recipe: read the snapshot's relays_published timestamp and compare its date. Textual consistency (whole file searched): '30 November 2025' found on lines [6, 23, 30]; no other date strings in the file.

- **ext-029** — UNVERIFIABLE
  - says: "Germany, the United States, and the Netherlands account for a substantial share of the observed relay population."
  - printed: DE, US, NL: substantial share
  - recomputed: n/a (snapshot file absent)
  - note: Recipe: count running relays by 'country'; check that each of de/us/nl is among the largest country counts and report their combined share (figures/tor_top15_countries.png is derived from the snapshot).

- **ext-030** — UNVERIFIABLE
  - says: "In aggregate, Fourteen-Eyes jurisdictions host more relays than all remaining jurisdictions combined."
  - printed: >50% of relay count
  - recomputed: n/a (snapshot file absent)
  - note: Recipe: count(country in 14-Eyes)/count(all) > 0.5 with 14-Eyes = {au, be, ca, dk, fr, de, it, nl, nz, no, es, se, gb, us}.

- **ext-031** — UNVERIFIABLE
  - says: "Approximately 75% of both the guard and the middle selection-probability mass"
  - printed: 75%
  - recomputed: n/a (snapshot file absent)
  - note: Recipe, on the Onionoo snapshot's per-relay guard_probability / middle_probability (not part of the released dataset): sum(guard_probability | country in 14-Eyes)/sum(guard_probability) and the same for middle_probability; both ~75% (figures/14_eyes_probabilities.png). Textual: percentage mentions: [(13, '75%'), (30, '75%')]; all mentions agree.

- **ext-032** — UNVERIFIABLE
  - says: "most of the weight at each of these two positions sits inside a single grouping"
  - printed: >50% at both positions
  - recomputed: n/a (snapshot file absent)
  - note: Implied by ext-031 (75% > 50%) but needs the snapshot to confirm.

- **ext-033** — UNVERIFIABLE
  - says: "Geographic distribution of Tor relays in the 30 November 2025 Onionoo snapshot."
  - printed: 30 November 2025
  - recomputed: date string lines: []; caption line absent
  - note: Externally unverifiable (snapshot absent); textual consistency: '30 November 2025' found on lines [6, 23, 30]; no other date strings in the file.

- **ext-034** — UNVERIFIABLE
  - says: "in the 30 November 2025 Onionoo snapshot. Approximately 75% of the probability mass for both positions lies within Fourteen-Eyes jurisdictions."
  - printed: 30 November 2025; 75%
  - recomputed: date string lines: []; caption line absent; percentage mentions: []
  - note: Needs the snapshot (same recipe as ext-031); textual consistency of the date and percentage across all mentions is reported in 'computed'.

- **const-040** — CONSTANT
  - says: "introduction circuit is reused for at most 18-24 h"
  - printed: 18-24 h
  - recomputed: 18--24 h
  - note: CONSTANT: Tor rend-spec-v3 / hs_circuit INTRO_POINT_LIFETIME_MIN_SECONDS = 18 h, MAX = 24 h; cited platzer2020critical.

- **const-041** — CONSTANT
  - says: "circuits leave through one reachable guard"
  - printed: one (1)
  - recomputed: one (1)
  - note: CONSTANT: Tor guard-spec (one primary guard in use for onion-service circuits).

- **const-042** — CONSTANT
  - says: "for the guard set, held for months, to shift"
  - printed: months
  - recomputed: months
  - note: CONSTANT: Tor guard-spec guard lifetime (~2-3 months, guard-lifetime consensus parameter).

- **const-043** — CONSTANT
  - says: "from a set of four that itself turns over every 1-12 days"
  - printed: four; 1-12 days
  - recomputed: four; 1--12 days
  - note: CONSTANT: Tor proposal 333 (NUM_LAYER2_GUARDS = 4; lifetime 1-12 days); same as const-009/010.

- **const-044** — CONSTANT
  - says: "A service's three introduction circuits share that guard"
  - printed: three (3)
  - recomputed: three (3)
  - note: CONSTANT: HiddenServiceNumIntroductionPoints default = 3 (same as const-012).

- **const-045** — CONSTANT
  - says: "The three can also be attacked concurrently"
  - printed: three (3)
  - recomputed: three (3)
  - note: CONSTANT: same constant as const-044.

## sections/appendix_results.tex

- **setup-023** — FROZEN
  - says: "All 36 individual run-stage observations are presented in"
  - printed: 36
  - recomputed: 36 (run,stage) in TRAJ; 36 MET rows; 36 rows in tab:run-stage-thresholds
  - note: textual/structural check; verified against the paper sources when the snapshot was taken, not recomputable from data/ alone; Same as setup-013 plus a count of stage rows in the appendix table.

- **setup-024** — FROZEN
  - says: "every run in Figures [ref]-[ref]."
  - printed: 3 figures (a-c)
  - recomputed: 3 files present (runs_grid_{a,b,c}.pdf); generate.py groups 9 runs into 3 panels of 3/3/3 (suffixes a,b,c); .tex reference span ('a', 'c')
  - note: textual/structural check; verified against the paper sources when the snapshot was taken, not recomputable from data/ alone; File existence for figures/runs_grid_{a,b,c}.pdf; panel grouping read (ast) from repro/generate.py figs_runs_grid and must cover every TRAJ run once.

- **setup-025** — PASS
  - says: "Per-run, per-stage measurements for nine end-to-end runs (IDs 1-9)"
  - printed: nine; 1-9
  - recomputed: 9 runs; paper ids 1..9 (raw 4..12)

- **setup-026** — PASS
  - says: "conducted on 7-10 January 2026."
  - printed: 7-10 January 2026
  - recomputed: 2026-01-07 .. 2026-01-10 over 36 experiment_date; day_label Day 1..4 -> ['07', '08', '09', '10'] Jan

- **app-001** — FROZEN
  - says: "T_<= q=min\t:|I_t|<= q\; T_conv=min\t:|I_t|=1\; and"
  - printed: T<=q = min t with |I_t|<=q; Tconv = min t with |I_t|=1; 36 rows
  - recomputed: 36/36 run-stage rows available in TRAJ and MET; T<=q (q in 10,5,3,2), Tconv = T<=1 and |A_1| = |I_1| derived from TRAJ for each; definitions on lines 16-17 present
  - note: textual/structural check; verified against the paper sources when the snapshot was taken, not recomputable from data/ alone; Definitional check: asserts lines 16-17 of the current .tex still carry the T<=q and Tconv definitions and that every one of the 36 (run, stage) pairs has a trajectory and a metrics row; the per-row values are checked by app-002..app-037 and the whole body by app-body.

- **app-002** — PASS
  - says: "R1 (Day 1, 02:00) & Intro. Point & 79 & 3 & 4 & 42 & 245 & 285 & 830"
  - printed: Day 1 02:00; 79; 3; 4; 42; 245; 285; 830
  - recomputed: Day 1 02:00 (IP row day_label / experiment_time_utc); 79; 3; 4; 42; 245; 285; 830

- **app-body** — FROZEN
  - says: ""
  - printed: 44 body lines
  - recomputed: 44 body lines from generate.py
  - note: textual/structural check; verified against the paper sources when the snapshot was taken, not recomputable from data/ alone; tabular body of tab:run-stage-thresholds equals repro/out/tables/run_stage_thresholds_body.tex (make tables) modulo whitespace

- **setup-027** — PASS
  - says: "R1 (Day 1, 02:00)"
  - printed: R1 (Day 1, 02:00); R2 (Day 1, 10:00); R3 (Day 1, 18:00); R4 (Day 2, 02:00); R5 (Day 2, 10:00); R6 (Day 2, 18:00); R7 (Day 3, 18:00); R8 (Day 4, 02:00); R9 (Day 4, 10:00)
  - recomputed: R1 (Day 1, 02:00); R2 (Day 1, 10:00); R3 (Day 1, 18:00); R4 (Day 2, 02:00); R5 (Day 2, 10:00); R6 (Day 2, 18:00); R7 (Day 3, 18:00); R8 (Day 4, 02:00); R9 (Day 4, 10:00)

- **app-003** — PASS
  - says: "& Middle 1 & 137 & 3 & 3 & 4 & 5 & 5 & 5000"
  - printed: 137; 3; 3; 4; 5; 5; 5000
  - recomputed: 137; 3; 3; 4; 5; 5; 5000

- **app-004** — PASS
  - says: "& Vanguard & 112 & 2 & 61 & 61 & 61 & 61 & 1200"
  - printed: 112; 2; 61; 61; 61; 61; 1200
  - recomputed: 112; 2; 61; 61; 61; 61; 1200

- **app-005** — PASS
  - says: "& Entry Guard & 218 & 8 & 16 & 16 & 31 & 31 & 9300"
  - printed: 218; 8; 16; 16; 31; 31; 9300
  - recomputed: 218; 8; 16; 16; 31; 31; 9300

- **app-006** — PASS
  - says: "R2 (Day 1, 10:00) & Intro. Point & 101 & 2 & 3 & 9 & 52 & 52 & 850"
  - printed: Day 1 10:00; 101; 2; 3; 9; 52; 52; 850
  - recomputed: Day 1 10:00 (IP row day_label / experiment_time_utc); 101; 2; 3; 9; 52; 52; 850

- **app-007** — PASS
  - says: "& Middle 1 & 192 & 4 & 5 & 7 & 13 & 13 & 5000"
  - printed: 192; 4; 5; 7; 13; 13; 5000
  - recomputed: 192; 4; 5; 7; 13; 13; 5000

- **app-008** — PASS
  - says: "& Vanguard & 76 & 3 & 3 & 3 & 3 & 4 & 1200"
  - printed: 76; 3; 3; 3; 3; 4; 1200
  - recomputed: 76; 3; 3; 3; 3; 4; 1200

- **app-009** — PASS
  - says: "& Entry Guard & 284 & 10 & 17 & 17 & 21 & 62 & 9300"
  - printed: 284; 10; 17; 17; 21; 62; 9300
  - recomputed: 284; 10; 17; 17; 21; 62; 9300

- **app-010** — PASS
  - says: "R3 (Day 1, 18:00) & Intro. Point & 74 & 3 & 9 & 11 & 163 & 163 & 850"
  - printed: Day 1 18:00; 74; 3; 9; 11; 163; 163; 850
  - recomputed: Day 1 18:00 (IP row day_label / experiment_time_utc); 74; 3; 9; 11; 163; 163; 850

- **app-011** — PASS
  - says: "& Middle 1 & 129 & 3 & 5 & 6 & 7 & 7 & 4000"
  - printed: 129; 3; 5; 6; 7; 7; 4000
  - recomputed: 129; 3; 5; 6; 7; 7; 4000

- **app-012** — PASS
  - says: "& Vanguard & 85 & 2 & 2 & 4 & 12 & 12 & 1200"
  - printed: 85; 2; 2; 4; 12; 12; 1200
  - recomputed: 85; 2; 2; 4; 12; 12; 1200

- **app-013** — PASS
  - says: "& Entry Guard & 249 & 11 & 25 & 26 & 26 & 78 & 9300"
  - printed: 249; 11; 25; 26; 26; 78; 9300
  - recomputed: 249; 11; 25; 26; 26; 78; 9300

- **app-014** — PASS
  - says: "R4 (Day 2, 02:00) & Intro. Point & 81 & 3 & 4 & 4 & 4 & 8 & 850"
  - printed: Day 2 02:00; 81; 3; 4; 4; 4; 8; 850
  - recomputed: Day 2 02:00 (IP row day_label / experiment_time_utc); 81; 3; 4; 4; 4; 8; 850

- **app-015** — PASS
  - says: "& Middle 1 & 148 & 4 & 7 & 8 & 8 & 11 & 4000"
  - printed: 148; 4; 7; 8; 8; 11; 4000
  - recomputed: 148; 4; 7; 8; 8; 11; 4000

- **app-016** — PASS
  - says: "& Vanguard & 107 & 3 & 5 & 5 & 6 & 10 & 1200"
  - printed: 107; 3; 5; 5; 6; 10; 1200
  - recomputed: 107; 3; 5; 5; 6; 10; 1200

- **app-017** — PASS
  - says: "& Entry Guard & 256 & 13 & 21 & 45 & 49 & 123 & 9900"
  - printed: 256; 13; 21; 45; 49; 123; 9900
  - recomputed: 256; 13; 21; 45; 49; 123; 9900

- **app-018** — PASS
  - says: "R5 (Day 2, 10:00) & Intro. Point & 101 & 6 & 11 & 30 & 178 & 178 & 1500"
  - printed: Day 2 10:00; 101; 6; 11; 30; 178; 178; 1500
  - recomputed: Day 2 10:00 (IP row day_label / experiment_time_utc); 101; 6; 11; 30; 178; 178; 1500

- **app-019** — PASS
  - says: "& Middle 1 & 158 & 6 & 10 & 13 & 16 & 17 & 4100"
  - printed: 158; 6; 10; 13; 16; 17; 4100
  - recomputed: 158; 6; 10; 13; 16; 17; 4100

- **app-020** — PASS
  - says: "& Vanguard & 148 & 38 & 60 & 61 & 76 & 142 & 1200"
  - printed: 148; 38; 60; 61; 76; 142; 1200
  - recomputed: 148; 38; 60; 61; 76; 142; 1200

- **app-021** — PASS
  - says: "& Entry Guard & 180 & 7 & 11 & 14 & 15 & 167 & 4800"
  - printed: 180; 7; 11; 14; 15; 167; 4800
  - recomputed: 180; 7; 11; 14; 15; 167; 4800

- **app-022** — PASS
  - says: "R6 (Day 2, 18:00) & Intro. Point & 84 & 3 & 14 & 233 & 324 & 324 & 1400"
  - printed: Day 2 18:00; 84; 3; 14; 233; 324; 324; 1400
  - recomputed: Day 2 18:00 (IP row day_label / experiment_time_utc); 84; 3; 14; 233; 324; 324; 1400

- **app-023** — PASS
  - says: "& Middle 1 & 147 & 3 & 4 & 9 & 10 & 10 & 4100"
  - printed: 147; 3; 4; 9; 10; 10; 4100
  - recomputed: 147; 3; 4; 9; 10; 10; 4100

- **app-024** — PASS
  - says: "& Vanguard & 161 & 11 & 19 & 49 & 66 & 251 & 1200"
  - printed: 161; 11; 19; 49; 66; 251; 1200
  - recomputed: 161; 11; 19; 49; 66; 251; 1200

- **app-025** — PASS
  - says: "& Entry Guard & 98 & 7 & 14 & 23 & 177 & 185 & 4800"
  - printed: 98; 7; 14; 23; 177; 185; 4800
  - recomputed: 98; 7; 14; 23; 177; 185; 4800

- **app-026** — PASS
  - says: "R7 (Day 3, 18:00) & Intro. Point & 75 & 3 & 4 & 4 & 4 & 11 & 1900"
  - printed: Day 3 18:00; 75; 3; 4; 4; 4; 11; 1900
  - recomputed: Day 3 18:00 (IP row day_label / experiment_time_utc); 75; 3; 4; 4; 4; 11; 1900

- **app-027** — PASS
  - says: "& Middle 1 & 164 & 4 & 6 & 7 & 9 & 10 & 4800"
  - printed: 164; 4; 6; 7; 9; 10; 4800
  - recomputed: 164; 4; 6; 7; 9; 10; 4800

- **app-028** — PASS
  - says: "& Vanguard & 95 & 3 & 3 & 6 & 20 & 24 & 1300"
  - printed: 95; 3; 3; 6; 20; 24; 1300
  - recomputed: 95; 3; 3; 6; 20; 24; 1300

- **app-029** — PASS
  - says: "& Entry Guard & 212 & 14 & 21 & 73 & 166 & 166 & 4800"
  - printed: 212; 14; 21; 73; 166; 166; 4800
  - recomputed: 212; 14; 21; 73; 166; 166; 4800

- **app-030** — PASS
  - says: "R8 (Day 4, 02:00) & Intro. Point & 91 & 3 & 5 & 6 & 6 & 8 & 1900"
  - printed: Day 4 02:00; 91; 3; 5; 6; 6; 8; 1900
  - recomputed: Day 4 02:00 (IP row day_label / experiment_time_utc); 91; 3; 5; 6; 6; 8; 1900

- **app-031** — PASS
  - says: "& Middle 1 & 198 & 7 & 11 & 14 & 14 & 53 & 4800"
  - printed: 198; 7; 11; 14; 14; 53; 4800
  - recomputed: 198; 7; 11; 14; 14; 53; 4800

- **app-032** — PASS
  - says: "& Vanguard & 89 & 3 & 3 & 4 & 4 & 6 & 1300"
  - printed: 89; 3; 3; 4; 4; 6; 1300
  - recomputed: 89; 3; 3; 4; 4; 6; 1300

- **app-033** — PASS
  - says: "& Entry Guard & 191 & 16 & 28 & 62 & 62 & 193 & 4800"
  - printed: 191; 16; 28; 62; 62; 193; 4800
  - recomputed: 191; 16; 28; 62; 62; 193; 4800

- **app-034** — PASS
  - says: "R9 (Day 4, 10:00) & Intro. Point & 50 & 2 & 2 & 3 & 6 & 10 & 2000"
  - printed: Day 4 10:00; 50; 2; 2; 3; 6; 10; 2000
  - recomputed: Day 4 10:00 (IP row day_label / experiment_time_utc); 50; 2; 2; 3; 6; 10; 2000

- **app-035** — PASS
  - says: "& Middle 1 & 90 & 2 & 3 & 3 & 3 & 4 & 4800"
  - printed: 90; 2; 3; 3; 3; 4; 4800
  - recomputed: 90; 2; 3; 3; 3; 4; 4800

- **app-036** — PASS
  - says: "& Vanguard & 48 & 2 & 2 & 3 & 3 & 3 & 1300"
  - printed: 48; 2; 2; 3; 3; 3; 1300
  - recomputed: 48; 2; 2; 3; 3; 3; 1300

- **app-037** — PASS
  - says: "& Entry Guard & 86 & 5 & 18 & 40 & 40 & 84 & 4400"
  - printed: 86; 5; 18; 40; 40; 84; 4400
  - recomputed: 86; 5; 18; 40; 40; 84; 4400

- **setup-028** — FROZEN
  - says: "Intersection degradation for Runs 1-3 across the four reconstruction"
  - printed: 1-3; four
  - recomputed: run labels in runs_grid_a.pdf: R[1, 2, 3]; generate.py panel a raw [4, 5, 6] -> paper [1, 2, 3]; stages per run in TRAJ [4, 4, 4]; 4 stage column titles in PDF
  - note: textual/structural check; verified against the paper sources when the snapshot was taken, not recomputable from data/ alone; Run labels 'Rn' read with pdftotext from the committed PDF and the panel grouping parsed (ast) from repro/generate.py figs_runs_grid, both compared with the caption range parsed from the .tex; each grouped run has 4 stage codes in TRAJ and the PDF carries 4 stage column titles.

- **setup-029** — PASS
  - says: "Each panel reports stage-start consensus weight (CW) and singleton convergence T_conv."
  - printed: 36 (CW, T_conv) panel annotations
  - recomputed: 36/36 annotation pairs read from committed PDFs; a: 12 (CW,T) pairs match; b: 12 (CW,T) pairs match; c: 12 (CW,T) pairs match

- **setup-030** — FROZEN
  - says: "Intersection degradation for Runs 4-6 across the four reconstruction"
  - printed: 4-6; four
  - recomputed: run labels in runs_grid_b.pdf: R[4, 5, 6]; generate.py panel b raw [7, 8, 9] -> paper [4, 5, 6]; stages per run in TRAJ [4, 4, 4]; 4 stage column titles in PDF
  - note: textual/structural check; verified against the paper sources when the snapshot was taken, not recomputable from data/ alone; Run labels 'Rn' read with pdftotext from the committed PDF and the panel grouping parsed (ast) from repro/generate.py figs_runs_grid, both compared with the caption range parsed from the .tex; each grouped run has 4 stage codes in TRAJ and the PDF carries 4 stage column titles.

- **setup-031** — FROZEN
  - says: "Intersection degradation for Runs 7-9 across the four reconstruction"
  - printed: 7-9; four
  - recomputed: run labels in runs_grid_c.pdf: R[7, 8, 9]; generate.py panel c raw [10, 11, 12] -> paper [7, 8, 9]; stages per run in TRAJ [4, 4, 4]; 4 stage column titles in PDF
  - note: textual/structural check; verified against the paper sources when the snapshot was taken, not recomputable from data/ alone; Run labels 'Rn' read with pdftotext from the committed PDF and the panel grouping parsed (ast) from repro/generate.py figs_runs_grid, both compared with the caption range parsed from the .tex; each grouped run has 4 stage codes in TRAJ and the PDF carries 4 stage column titles.

## sections/appendix_time_of_introduction_handshake_completion.tex

- **ext-003** — FROZEN
  - says: "we measured the introduction handshake for 16 publicly reachable onion services"
  - printed: 16
  - recomputed: 16
  - note: textual/structural check; verified against the paper sources when the snapshot was taken, not recomputable from data/ alone; Textual: printed service count parsed from the .tex compared with the number of data rows in tab:onion_avg_latency.

- **ext-004** — UNVERIFIABLE
  - says: "repeating the measurement 10 times for each service"
  - printed: 10
  - recomputed: n/a (raw trials absent)
  - note: Raw per-trial introduction-latency measurements are not in the project; only the per-service means are printed. Trial count as printed at each mention: repeating=10, perform=10, mean-across=10, caption=10.

- **ext-005** — FROZEN
  - says: "We measure this interval using 16 publicly reachable onion services."
  - printed: 16
  - recomputed: 16
  - note: textual/structural check; verified against the paper sources when the snapshot was taken, not recomputable from data/ alone; Textual: printed service count parsed from the .tex compared with the number of data rows in tab:onion_avg_latency.

- **ext-006** — UNVERIFIABLE
  - says: "For each service, we perform 10 independent introduction handshakes"
  - printed: 10
  - recomputed: n/a (raw trials absent)
  - note: Raw per-trial introduction-latency measurements are not in the project; only the per-service means are printed. Trial count as printed at each mention: repeating=10, perform=10, mean-across=10, caption=10.

- **ext-007** — FROZEN
  - says: "yielding 160 measurements in total"
  - printed: 160
  - recomputed: 16 rows x 10 stated trials = 160
  - note: textual/structural check; verified against the paper sources when the snapshot was taken, not recomputable from data/ alone; Arithmetic consistency only: table row count times the trial count printed in the same paragraph, compared with the printed total; the trial factor itself is unverifiable (raw trials absent).

- **ext-008** — UNVERIFIABLE
  - says: "reports the mean \Delta t across the 10 trials for each onion service"
  - printed: 10
  - recomputed: n/a (raw trials absent)
  - note: Raw per-trial introduction-latency measurements are not in the project; only the per-service means are printed. Trial count as printed at each mention: repeating=10, perform=10, mean-across=10, caption=10.

- **ext-009** — FROZEN
  - says: "The per-service means range from 0.521 s to 1.780 s."
  - printed: 0.521-1.780
  - recomputed: 0.521--1.780
  - note: textual/structural check; verified against the paper sources when the snapshot was taken, not recomputable from data/ alone; Range parsed from the prose at run time; table-internal min (BMG) and max (Black Cloud) of the parsed Avg dt column.

- **ext-010** — FROZEN
  - says: "the complete interval therefore remains on the order of seconds"
  - printed: order of seconds
  - recomputed: all 16 means in [0.521, 1.780] s, mean 0.899 s; criterion 0 < v and max < 2.0 s: True
  - note: textual/structural check; verified against the paper sources when the snapshot was taken, not recomputable from data/ alone; Table-internal: largest per-service mean is 1.780 s (Black Cloud); criterion used: every mean positive and below 2.0 s.

- **ext-011a** — FROZEN
  - says: "across 16 onion services, with 10 trials per service"
  - printed: 16
  - recomputed: 16 rows
  - note: textual/structural check; verified against the paper sources when the snapshot was taken, not recomputable from data/ alone; Caption service count parsed from the .tex compared with the table row count.

- **ext-011b** — UNVERIFIABLE
  - says: "across 16 onion services, with 10 trials per service"
  - printed: 10
  - recomputed: n/a (raw trials absent; caption or methodology trial count not found)
  - note: Trials per service cannot be verified (raw trials absent); only textual consistency with the methodology paragraph is checked, and a disagreement is reported as FAIL.

- **ext-012** — UNVERIFIABLE
  - says: "Cryptostamps & Postage store & 0.642"
  - printed: 0.642
  - recomputed: n/a
  - note: Raw per-trial latencies not in project; the mean itself is unverifiable.

- **ext-013** — UNVERIFIABLE
  - says: "Breaking Bad & Drug forum & 0.547"
  - printed: 0.547
  - recomputed: n/a
  - note: Raw per-trial latencies not in project; the mean itself is unverifiable.

- **ext-014** — UNVERIFIABLE
  - says: "Black Cloud & Onion pastebin & 1.780"
  - printed: 1.780
  - recomputed: n/a
  - note: Raw per-trial latencies not in project; the mean itself is unverifiable. Equals the stated maximum.

- **ext-015** — UNVERIFIABLE
  - says: "Ahmia & HS search engine & 1.019"
  - printed: 1.019
  - recomputed: n/a
  - note: Raw per-trial latencies not in project; the mean itself is unverifiable.

- **ext-016** — UNVERIFIABLE
  - says: "Onion ID Serv. & ID/passport store & 0.879"
  - printed: 0.879
  - recomputed: n/a
  - note: Raw per-trial latencies not in project; the mean itself is unverifiable.

- **ext-017** — UNVERIFIABLE
  - says: "ChaTor & Onion messenger & 1.230"
  - printed: 1.230
  - recomputed: n/a
  - note: Raw per-trial latencies not in project; the mean itself is unverifiable.

- **ext-018** — UNVERIFIABLE
  - says: "Comic Book Libr. & Library & 0.654"
  - printed: 0.654
  - recomputed: n/a
  - note: Raw per-trial latencies not in project; the mean itself is unverifiable.

- **ext-019** — UNVERIFIABLE
  - says: "Apples4Bitcoin & Onion apple store & 0.882"
  - printed: 0.882
  - recomputed: n/a
  - note: Raw per-trial latencies not in project; the mean itself is unverifiable.

- **ext-020** — UNVERIFIABLE
  - says: "Dread & Onion forum & 1.060"
  - printed: 1.060
  - recomputed: n/a
  - note: Raw per-trial latencies not in project; the mean itself is unverifiable.

- **ext-021** — UNVERIFIABLE
  - says: "Mail2Tor & Onion mail & 0.701"
  - printed: 0.701
  - recomputed: n/a
  - note: Raw per-trial latencies not in project; the mean itself is unverifiable.

- **ext-022** — UNVERIFIABLE
  - says: "Sonar & Onion messenger & 0.805"
  - printed: 0.805
  - recomputed: n/a
  - note: Raw per-trial latencies not in project; the mean itself is unverifiable.

- **ext-023** — UNVERIFIABLE
  - says: "FAH & Hiring service & 1.492"
  - printed: 1.492
  - recomputed: n/a
  - note: Raw per-trial latencies not in project; the mean itself is unverifiable.

- **ext-024** — UNVERIFIABLE
  - says: "Mobile Store & Mobile store & 0.871"
  - printed: 0.871
  - recomputed: n/a
  - note: Raw per-trial latencies not in project; the mean itself is unverifiable.

- **ext-025** — UNVERIFIABLE
  - says: "USJUD & Counterfeit store & 0.636"
  - printed: 0.636
  - recomputed: n/a
  - note: Raw per-trial latencies not in project; the mean itself is unverifiable.

- **ext-026** — UNVERIFIABLE
  - says: "BMG & Gun store & 0.521"
  - printed: 0.521
  - recomputed: n/a
  - note: Raw per-trial latencies not in project; the mean itself is unverifiable. Equals the stated minimum.

- **ext-027** — UNVERIFIABLE
  - says: "DarkSearch & Onion search engine & 0.657"
  - printed: 0.657
  - recomputed: n/a
  - note: Raw per-trial latencies not in project; the mean itself is unverifiable.

## sections/implementation.tex

- **setup-015** — FROZEN
  - says: "Four of the five components (Table [ref]) run on the monitored relay's host"
  - printed: four of five
  - recomputed: 4 of 5 (Controller, Probe-client daemon, Intersection plugin, \texttt{tcpdump}, Onion-service daemon)
  - note: textual/structural check; verified against the paper sources when the snapshot was taken, not recomputable from data/ alone; Rows of tab:impl-components; all but the Onion-service daemon run on the monitored relay.

- **setup-016** — FROZEN
  - says: "the fifth is the modified onion-service daemon on the service host. The four move with the observation"
  - printed: fifth; four
  - recomputed: Onion-service daemon is row 5 of 5; 4 remaining
  - note: textual/structural check; verified against the paper sources when the snapshot was taken, not recomputable from data/ alone; Textual: position of the Onion-service daemon row in tab:impl-components.

- **const-032** — CONSTANT
  - says: "Triggers one introduction handshake per iteration"
  - printed: one
  - recomputed: one TRAJ row per (run,stage,trial): 2771 rows across 36 run-stage trajectories; trial indices re-read from trajectories_every_trial.csv are contiguous 1..T in all 36
  - note: CONSTANT: prototype design; consistent with one TRAJ row per (run,stage,trial) (contiguity verified in-module from the raw CSV).

- **setup-017** — PASS
  - says: "Pins the target introduction circuit to the four relays we operate."
  - printed: four
  - recomputed: 4 stage codes per run in TRAJ, 4 in MET (codes ['EG', 'IP', 'M1', 'VG'])

- **setup-018** — PASS
  - says: "_\textnormalfour public relays we operate."
  - printed: four
  - recomputed: 4 stage codes per run in TRAJ, 4 in MET (codes ['EG', 'IP', 'M1', 'VG'])

- **setup-019** — PASS
  - says: "Operating the four relays ourselves substitutes for the visibility"
  - printed: four
  - recomputed: 4 stage codes per run in TRAJ, 4 in MET (codes ['EG', 'IP', 'M1', 'VG'])

- **setup-020** — PASS
  - says: "The four monitored-relay stages walk this circuit in reverse"
  - printed: four (IP->M1->VG->EG)
  - recomputed: 4 stage codes per run in TRAJ, 4 in MET (codes ['EG', 'IP', 'M1', 'VG']); stage starts ordered IP<M1<VG<EG in all runs

- **const-033** — CONSTANT
  - says: "At stage 0 the monitored relay is the advertised Introduction Point."
  - printed: 0
  - recomputed: earliest stage per run by (experiment_date, experiment_time_utc) = IP for all 9 runs
  - note: CONSTANT: design; MET first stage_code per run is IP (earliest experiment_date + experiment_time_utc, minute resolution) - see setup-003.

- **const-034** — CONSTANT
  - says: "removing the known predecessor r_m_i-1 from stage 1 onward"
  - printed: 1
  - recomputed: 1
  - note: CONSTANT: algorithm design (same constant as const-018).

- **conv-025** — PASS
  - says: "If the intersection still holds more than one pseudonym, the controller kills the probe client"
  - printed: more than one
  - recomputed: all 36 stages: |I_t| > 1 for every t < Tconv and |I_Tconv| = 1 (no trial recorded after convergence)

- **const-035** — CONSTANT
  - says: "\delta=30 s, and repeats steps 6a-13 against the same relay"
  - printed: 30
  - recomputed: 30
  - note: CONSTANT: implementation parameter (delta = 30 s slept between iterations); stage timestamps are not part of the released dataset, so it is not recomputable. Restated at sections/04-setup-and-evaluation.tex:329 and :370 (const-046/047, textual consistency).

- **conv-026** — PASS
  - says: "If the cumulative intersection holds a single pseudonym, the stage is done"
  - printed: single (1)
  - recomputed: all 36 stages: T<=1(seq) == len(seq) and seq[-1]==1

- **conv-027** — PASS
  - says: "If the intersection is empty, the pinned path no longer holds and the run ends with the error \textscIntroductionCircuitDropped."
  - printed: empty (0)
  - recomputed: min(intersection_size) = 1 over 2771 rows; no empty intersection recorded

- **setup-021** — PASS
  - says: "one CSV records the run, stage, iteration, and intersection cardinality per observation, a second records stage-level metadata"
  - printed: 2 CSVs
  - recomputed: 2 CSV(s) in data/ (run_stage_metrics.csv, trajectories_every_trial.csv); TRAJ header=['run_id', 'stage', 'trial', 'intersection_size']; MET header=['run_id', 'stage_code', 'experiment_date', 'day_label', 'experiment_time_utc', 'consensus_weight']

- **setup-022** — FROZEN
  - says: "We considered each of the TRSB's nine research-safety principles as follows."
  - printed: nine
  - recomputed: 9 \item entries in the enumerate
  - note: textual/structural check; verified against the paper sources when the snapshot was taken, not recomputable from data/ alone; Textual: \item count in the enumerate following the quoted sentence. The TRSB page itself lists nine considerations (external, not re-fetched).

- **const-036** — CONSTANT
  - says: "A typical ten-minute period on the deployed network involves roughly 550,000 active users and about 1.4 million active circuits"
  - printed: ten-minute; 550,000; 1.4 million
  - recomputed: ten-minute; 550,000; 1.4 million
  - note: CONSTANT: cited jansen2016safely (Safely Measuring Tor, CCS 2016).

- **const-037** — CONSTANT
  - says: "pseudonymised in volatile memory using per-stage RSA keys"
  - printed: per-stage (one key per stage)
  - recomputed: 36 run-stage rows in MET => 36 keys implied
  - note: CONSTANT: design statement; implies one key per MET row (36) but keys never reached disk, so the key count itself is not checkable.


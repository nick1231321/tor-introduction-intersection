# Manual verification checklist

For each claim: the sentence or table row as printed in the paper (search for it in the PDF),
the value printed there, and the value recomputed from `data/` by `make verify`.
PASS = the recomputed value equals the printed one; FAIL = it does not (the note says why).
Every value is derived from the nine experimental runs in `data/`.

PASS 115, FAIL 0; total 115

## main.tex

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

- **conv-002** — PASS
  - says: "complete target path in all nine experiments (Section [ref])."
  - printed: nine (all nine)
  - recomputed: 9 of 9 runs converged at all 4 stages (36/36 stages reach |I|=1)

## sections/03-attack.tex

- **setup-003** — PASS
  - says: "r_m_0,\ldots,r_m_3 denote the Introduction Point, the middle relay or layer-3 vanguard, the layer-2 vanguard, and the entry guard"
  - printed: 0..3 = IP,M1,VG,EG
  - recomputed: IP<M1<VG<EG by (experiment_date, experiment_time_utc) in all 9 runs

- **conv-003** — PASS
  - says: "Stage i converges at the first iteration j for which |I_i^(j)|=1."
  - printed: 1
  - recomputed: all 36 stages: T<=1(seq) == len(seq) and seq[-1]==1

- **conv-004** — PASS
  - says: "\If|I_i| = 0"
  - printed: 0
  - recomputed: min(intersection_size) = 1 over 2771 rows

## sections/04-setup-and-evaluation.tex

- **setup-006** — PASS
  - says: "we ran Algorithm [ref] nine times on the live Tor network"
  - printed: nine
  - recomputed: 9 runs in TRAJ (raw ids 4..12), 9 in MET

- **setup-007** — PASS
  - says: "we pinned the service's introduction circuit to four public Tor relays of ours"
  - printed: four
  - recomputed: 4 stage codes per run in TRAJ, 4 in MET (codes ['EG', 'IP', 'M1', 'VG'])

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

- **setup-010** — PASS
  - says: "where N is the total number of iterations across the four stages"
  - printed: four
  - recomputed: 4 stage codes per run in TRAJ, 4 in MET (codes ['EG', 'IP', 'M1', 'VG'])

- **time-006** — PASS
  - says: "when v=0, the median reconstruction takes 2.24 h and the slowest takes 6.63 h."
  - printed: 2.24; 6.63
  - recomputed: 2.24; 6.63

- **time-007** — PASS
  - says: "correspond to approximately 12% and 37%, respectively, of 18 h"
  - printed: 12%; 37%
  - recomputed: 12%; 37%

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
  - printed: five of nine
  - recomputed: 5 of 9

- **time-011** — PASS
  - says: "visibility accounts for approximately 64% of the total time at v=1 h and 88% at v=4 h."
  - printed: 64%; 88%
  - recomputed: 64%; 88%

- **time-012** — PASS
  - says: "v_max ranges from 2.84 to 4.28 h despite a more than sevenfold difference in total iteration counts."
  - printed: 2.84-4.28; sevenfold
  - recomputed: 2.84--4.28; 7.62-fold

- **setup-011** — PASS
  - says: "End-to-end reconstruction cost across the nine experiments"
  - printed: nine; 9 data rows in tab:end_to_end
  - recomputed: 9 runs in TRAJ (raw ids 4..12), 9 in MET

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

- **contr-body** — PASS
  - says: ""
  - printed: 11 lines, sha1 e9c8820d2742
  - recomputed: 11 lines, sha1 e9c8820d2742

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

## sections/07-conclusion.tex

- **setup-014** — PASS
  - says: "We evaluated the attack in nine end-to-end experiments against a"
  - printed: nine
  - recomputed: 9 runs in TRAJ (raw ids 4..12), 9 in MET

- **conv-024** — PASS
  - says: "Across all nine experiments, the attack successfully reconstructed"
  - printed: nine (all)
  - recomputed: 9 of 9 runs converged at all 4 stages (36/36 stages reach |I|=1)

## sections/appendix_results.tex

- **setup-023** — PASS
  - says: "All 36 individual run-stage observations are presented in"
  - printed: 36; 36 rows in tab:run-stage-thresholds
  - recomputed: 36 (run,stage) in TRAJ; 36 MET rows

- **setup-025** — PASS
  - says: "Per-run, per-stage measurements for nine end-to-end runs (IDs 1-9)"
  - printed: nine; 1-9
  - recomputed: 9 runs; paper ids 1..9 (raw 4..12)

- **setup-026** — PASS
  - says: "conducted on 7-10 January 2026."
  - printed: 7-10 January 2026
  - recomputed: 2026-01-07 .. 2026-01-10 over 36 experiment_date; day_label Day 1..4 -> ['07', '08', '09', '10'] Jan

- **app-002** — PASS
  - says: "R1 (Day 1, 02:00) & Intro. Point & 79 & 3 & 4 & 42 & 245 & 285 & 830"
  - printed: Day 1 02:00; 79; 3; 4; 42; 245; 285; 830
  - recomputed: Day 1 02:00 (IP row day_label / experiment_time_utc); 79; 3; 4; 42; 245; 285; 830

- **app-body** — PASS
  - says: ""
  - printed: 44 lines, sha1 ff95511ba9d7
  - recomputed: 44 lines, sha1 ff95511ba9d7

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

## sections/implementation.tex

- **conv-025** — PASS
  - says: "If the intersection still holds more than one pseudonym, the controller kills the probe client"
  - printed: more than one
  - recomputed: all 36 stages: |I_t| > 1 for every t < Tconv and |I_Tconv| = 1 (no trial recorded after convergence)

- **conv-026** — PASS
  - says: "If the cumulative intersection holds a single pseudonym, the stage is done"
  - printed: single (1)
  - recomputed: all 36 stages: T<=1(seq) == len(seq) and seq[-1]==1

- **conv-027** — PASS
  - says: "If the intersection is empty, the pinned path no longer holds and the run ends with the error \textscIntroductionCircuitDropped."
  - printed: empty (0)
  - recomputed: min(intersection_size) = 1 over 2771 rows; no empty intersection recorded


```
== Abstract ==
[PASS] "the attack reconstructs the complete Tor circuit in every run"
       paper: every run (9 of 9)
       data:  9 of 9 runs converged at all 4 stages (36/36 stages reach |I|=1)
[PASS] "with an estimated median time of 2.2 h."
       paper: 2.2
       data:  2.2

== Section 1 ==
[PASS] "complete target path in all nine experiments (Section [ref])."
       paper: nine (all nine)
       data:  9 of 9 runs converged at all 4 stages (36/36 stages reach |I|=1)

== Section 4 ==
[PASS] "Across the nine end-to-end experiments, the attack successfully reconstructed the complete introduction path in every run."
       paper: nine (9 of 9 succeeded)
       data:  9 of 9 runs converged at all 4 stages (36/36 stages reach |I|=1)
[PASS] "All 36 stages converged to the correct successor."
       paper: 36
       data:  36 of 36 stages end at |I|=1
[PASS] "median of 260 iterations, ranging from 101 to 770 iterations across runs"
       paper: 260; 101; 770
       data:  median=260; min=101; max=770 [N per run: R1(raw 4)=382, R2(raw 5)=131, R3(raw 6)=260, R4(raw 7)=152, R5(raw 8)=504, R6(raw 9)=770, R7(raw 10)=211, R8(raw 11)=260, R9(raw 12)=101]
[PASS] "when v=0, the median reconstruction takes 2.24 h and the slowest takes 6.63 h."
       paper: 2.24; 6.63
       data:  2.24; 6.63
[PASS] "correspond to approximately 12% and 37%, respectively, of 18 h"
       paper: 12%; 37%
       data:  12%; 37%
[PASS] "The median run permits v_max=3.94 h per relay"
       paper: 3.94
       data:  3.94
[PASS] "the most iteration-intensive run, experiment 6, permits 2.84 h."
       paper: 6; 2.84
       data:  6; 2.84
[PASS] "At v=4 h, five of the nine runs exceed the 18 h bound."
       paper: five of nine
       data:  5 of 9
[PASS] "visibility accounts for approximately 64% of the total time at v=1 h and 88% at v=4 h."
       paper: 64%; 88%
       data:  64%; 88%
[PASS] "v_max ranges from 2.84 to 4.28 h despite a more than sevenfold difference in total iteration counts."
       paper: 2.84-4.28; sevenfold
       data:  2.84--4.28; 7.62-fold
[PASS] "Table tab:end_to_end row 1 (1 & 285 (830) & ...)"
       paper: 285 (830); 5 (5000); 61 (1200); 31 (9300); 382; 3.29; 7.29; 19.29; 3.68
       data:  285 (830); 5 (5000); 61 (1200); 31 (9300); 382; 3.29; 7.29; 19.29; 3.68
[PASS] "Table tab:end_to_end row 2 (2 & 52 (850) & ...)"
       paper: 52 (850); 13 (5000); 4 (1200); 62 (9300); 131; 1.13; 5.13; 17.13; 4.22
       data:  52 (850); 13 (5000); 4 (1200); 62 (9300); 131; 1.13; 5.13; 17.13; 4.22
[PASS] "Table tab:end_to_end row 3 (3 & 163 (850) & ...)"
       paper: 163 (850); 7 (4000); 12 (1200); 78 (9300); 260; 2.24; 6.24; 18.24; 3.94
       data:  163 (850); 7 (4000); 12 (1200); 78 (9300); 260; 2.24; 6.24; 18.24; 3.94
[PASS] "Table tab:end_to_end row 4 (4 & 8 (850) & ...)"
       paper: 8 (850); 11 (4000); 10 (1200); 123 (9900); 152; 1.31; 5.31; 17.31; 4.17
       data:  8 (850); 11 (4000); 10 (1200); 123 (9900); 152; 1.31; 5.31; 17.31; 4.17
[PASS] "Table tab:end_to_end row 5 (5 & 178 (1500) & ...)"
       paper: 178 (1500); 17 (4100); 142 (1200); 167 (4800); 504; 4.34; 8.34; 20.34; 3.42
       data:  178 (1500); 17 (4100); 142 (1200); 167 (4800); 504; 4.34; 8.34; 20.34; 3.42
[PASS] "Table tab:end_to_end row 6 (6 & 324 (1400) & ...)"
       paper: 324 (1400); 10 (4100); 251 (1200); 185 (4800); 770; 6.63; 10.63; 22.63; 2.84
       data:  324 (1400); 10 (4100); 251 (1200); 185 (4800); 770; 6.63; 10.63; 22.63; 2.84
[PASS] "Table tab:end_to_end row 7 (7 & 11 (1900) & ...)"
       paper: 11 (1900); 10 (4800); 24 (1300); 166 (4800); 211; 1.82; 5.82; 17.82; 4.05
       data:  11 (1900); 10 (4800); 24 (1300); 166 (4800); 211; 1.82; 5.82; 17.82; 4.05
[PASS] "Table tab:end_to_end row 8 (8 & 8 (1900) & ...)"
       paper: 8 (1900); 53 (4800); 6 (1300); 193 (4800); 260; 2.24; 6.24; 18.24; 3.94
       data:  8 (1900); 53 (4800); 6 (1300); 193 (4800); 260; 2.24; 6.24; 18.24; 3.94
[PASS] "Table tab:end_to_end row 9 (9 & 10 (2000) & ...)"
       paper: 10 (2000); 4 (4800); 3 (1300); 84 (4400); 101; 0.87; 4.87; 16.87; 4.28
       data:  10 (2000); 4 (4800); 3 (1300); 84 (4400); 101; 0.87; 4.87; 16.87; 4.28
[PASS] "Table tab:end_to_end Median row (Median & 52 & 10 & ...)"
       paper: 52; 10; 12; 123; 260; 2.24; 6.24; 18.24; 3.94
       data:  52; 10; 12; 123; 260; 2.24; 6.24; 18.24; 3.94
[PASS] ""
       paper: 11 lines, sha1 e9c8820d2742
       data:  11 lines, sha1 e9c8820d2742
[PASS] "rows shown for Entry Guard"
       paper: R1,R4,R6,R8
       data:  R1,R4,R6,R8
[PASS] "rows shown for Introduction Point"
       paper: R4,R2,R1,R6
       data:  R4,R2,R1,R6
[PASS] "rows shown for Middle 1"
       paper: R9,R6,R5,R8
       data:  R9,R6,R5,R8
[PASS] "rows shown for Vanguard"
       paper: R9,R3,R5,R6
       data:  R9,R3,R5,R6
[PASS] "R4 D2 02:00 (Introduction Point)"
       paper: R4; D2 02:00; 850; 81; 3; 4; 4; 8
       data:  R4; D2 02:00; 850; 81; 3; 4; 4; 8
[PASS] "R9 D4 10:00 (Vanguard)"
       paper: R9; D4 10:00; 1300; 48; 2; 3; 3; 3
       data:  R9; D4 10:00; 1300; 48; 2; 3; 3; 3
[PASS] "R2 D1 10:00 (Introduction Point)"
       paper: R2; D1 10:00; 850; 101; 2; 9; 52; 52
       data:  R2; D1 10:00; 850; 101; 2; 9; 52; 52
[PASS] "R3 D1 18:00 (Vanguard)"
       paper: R3; D1 18:00; 1200; 85; 2; 4; 12; 12
       data:  R3; D1 18:00; 1200; 85; 2; 4; 12; 12
[PASS] "R1 D1 02:00 (Introduction Point)"
       paper: R1; D1 02:00; 830; 79; 3; 42; 245; 285
       data:  R1; D1 02:00; 830; 79; 3; 42; 245; 285
[PASS] "R5 D2 10:00 (Vanguard)"
       paper: R5; D2 10:00; 1200; 148; 38; 61; 76; 142
       data:  R5; D2 10:00; 1200; 148; 38; 61; 76; 142
[PASS] "R6 D2 18:00 (Introduction Point)"
       paper: R6; D2 18:00; 1400; 84; 3; 233; 324; 324
       data:  R6; D2 18:00; 1400; 84; 3; 233; 324; 324
[PASS] "R6 D2 18:00 (Vanguard)"
       paper: R6; D2 18:00; 1200; 161; 11; 49; 66; 251
       data:  R6; D2 18:00; 1200; 161; 11; 49; 66; 251
[PASS] "R9 D4 10:00 (Middle 1)"
       paper: R9; D4 10:00; 4800; 90; 2; 3; 3; 4
       data:  R9; D4 10:00; 4800; 90; 2; 3; 3; 4
[PASS] "R1 D1 02:00 (Entry Guard)"
       paper: R1; D1 02:00; 9300; 218; 8; 16; 31; 31
       data:  R1; D1 02:00; 9300; 218; 8; 16; 31; 31
[PASS] "R6 D2 18:00 (Middle 1)"
       paper: R6; D2 18:00; 4100; 147; 3; 9; 10; 10
       data:  R6; D2 18:00; 4100; 147; 3; 9; 10; 10
[PASS] "R4 D2 02:00 (Entry Guard)"
       paper: R4; D2 02:00; 9900; 256; 13; 45; 49; 123
       data:  R4; D2 02:00; 9900; 256; 13; 45; 49; 123
[PASS] "R5 D2 10:00 (Middle 1)"
       paper: R5; D2 10:00; 4100; 158; 6; 13; 16; 17
       data:  R5; D2 10:00; 4100; 158; 6; 13; 16; 17
[PASS] "R6 D2 18:00 (Entry Guard)"
       paper: R6; D2 18:00; 4800; 98; 7; 23; 177; 185
       data:  R6; D2 18:00; 4800; 98; 7; 23; 177; 185
[PASS] "R8 D4 02:00 (Middle 1)"
       paper: R8; D4 02:00; 4800; 198; 7; 14; 14; 53
       data:  R8; D4 02:00; 4800; 198; 7; 14; 14; 53
[PASS] "R8 D4 02:00 (Entry Guard)"
       paper: R8; D4 02:00; 4800; 191; 16; 62; 62; 193
       data:  R8; D4 02:00; 4800; 191; 16; 62; 62; 193
[PASS] "the median iteration at which |I_i^(j)|<=10 was three"
       paper: 3
       data:  median(T<=10 over 36 stages) = 3
[PASS] "and 64% of stages reached this threshold within five iterations"
       paper: 64%
       data:  23/36 = 63.89% -> 64%
[PASS] "candidate set shrank by 72-87% after the first intersection"
       paper: 72-87%
       data:  72--87% [per stage: IP 82.7, M1 79.7, VG 87.4, EG 72.2]
[PASS] "and by 85-96% by the third iteration, depending on the stage"
       paper: 85-96%
       data:  85--96% [per stage: IP 91.4, M1 92.6, VG 95.8, EG 85.4]
[PASS] "three of the six Vanguard stages at CW 1200"
       paper: 1200; 6
       data:  6 Vanguard stages at CW 1200 in run metadata [raw 4 (R1): Tconv=61, raw 5 (R2): Tconv=4, raw 6 (R3): Tconv=12, raw 7 (R4): Tconv=10, raw 8 (R5): Tconv=142, raw 9 (R6): Tconv=251]
[PASS] "converged after 12, 142, and 251 iterations"
       paper: 12, 142, 251
       data:  12, 142, 251 [Tconv(VG) of raw 6, 8, 9 = R3, R5, R6]
[PASS] "two of the three Middle stages at CW 4800"
       paper: 4800; 3
       data:  3 Middle stages at CW 4800 in run metadata [raw 10 (R7): Tconv=10, raw 11 (R8): Tconv=53, raw 12 (R9): Tconv=4]
[PASS] "required 4 and 53"
       paper: 4, 53
       data:  4, 53 [Tconv(M1) of raw 12, 11 = R9, R8]
[PASS] "the Introduction Point stages of Runs 1, 4, and 6 started with similar sets of 79-84 candidates"
       paper: 1, 4, 6
       data:  runs with |A1|(IP) in [79,84]: [4, 7, 9] -> paper R1, R4, R6 [other runs: raw 5=101, raw 6=74, raw 8=101, raw 10=75, raw 11=91, raw 12=50]
[PASS] "started with similar sets of 79-84 candidates"
       paper: 79-84
       data:  79--84 [|A1| raw 4,7,9 = 79, 81, 84]
[PASS] "reached |I|<=10 within three iterations"
       paper: 3
       data:  T<=10(IP) raw 4,7,9 = 3, 3, 3; all <= 3: True
[PASS] "yet converged after 285, 8, and 324 iterations, respectively"
       paper: 285, 8, 324
       data:  285, 8, 324 [Tconv(IP) raw 4, 7, 9]
[PASS] "In 13 of the 36 stages the intersection still held three or more candidates at the penultimate iteration and then fell to a singleton in one step"
       paper: 13 of 36
       data:  13 of 36 [(4,M1), (4,VG), (4,EG), (5,IP), (5,M1), (6,IP), (6,M1), (6,VG), (8,IP), (9,IP), (9,M1), (10,EG), (12,VG)]
[PASS] "In seven of these the cardinality had been constant for at least ten iterations beforehand"
       paper: 7
       data:  7 of 13 abrupt-collapse stages have plateau >= 10 [plateau lengths: (4,M1):1, (4,VG):57, (4,EG):15, (5,IP):43, (5,M1):6, (6,IP):152, (6,M1):1, (6,VG):8, (8,IP):148, (9,IP):91, (9,M1):1, (10,EG):93, (12,VG):1]
[PASS] "The vanguard stage of Run 1 held six candidates for 57 iterations and converged at iteration 61"
       paper: 6; 57; 61
       data:  penultimate value=6; plateau trials 4..60 (57 trials, contiguous=True); Tconv=61
[PASS] "Introduction Point stages of Runs 3 and 5 held three for 152 and 148 iterations before converging at iterations 163 and 178"
       paper: 3; 152, 148; 163, 178
       data:  value 3/3; plateau 152, 148 (raw 6: trials 11..162, raw 8: trials 30..177); Tconv 163, 178

== Section 7 ==
[PASS] "Across all nine experiments, the attack successfully reconstructed"
       paper: nine (all)
       data:  9 of 9 runs converged at all 4 stages (36/36 stages reach |I|=1)

== Appendix A ==
[PASS] "conducted on 7-10 January 2026."
       paper: 7-10 January 2026
       data:  2026-01-07 .. 2026-01-10 over 36 experiment_date; day_label Day 1..4 -> ['07', '08', '09', '10'] Jan
[PASS] "R1 (Day 1, 02:00) & Intro. Point & 79 & 3 & 4 & 42 & 245 & 285 & 830"
       paper: Day 1 02:00; 79; 3; 4; 42; 245; 285; 830
       data:  Day 1 02:00 (IP row day_label / experiment_time_utc); 79; 3; 4; 42; 245; 285; 830
[PASS] ""
       paper: 44 lines, sha1 ff95511ba9d7
       data:  44 lines, sha1 ff95511ba9d7
[PASS] "R1 (Day 1, 02:00)"
       paper: R1 (Day 1, 02:00); R2 (Day 1, 10:00); R3 (Day 1, 18:00); R4 (Day 2, 02:00); R5 (Day 2, 10:00); R6 (Day 2, 18:00); R7 (Day 3, 18:00); R8 (Day 4, 02:00); R9 (Day 4, 10:00)
       data:  R1 (Day 1, 02:00); R2 (Day 1, 10:00); R3 (Day 1, 18:00); R4 (Day 2, 02:00); R5 (Day 2, 10:00); R6 (Day 2, 18:00); R7 (Day 3, 18:00); R8 (Day 4, 02:00); R9 (Day 4, 10:00)
[PASS] "& Middle 1 & 137 & 3 & 3 & 4 & 5 & 5 & 5000"
       paper: 137; 3; 3; 4; 5; 5; 5000
       data:  137; 3; 3; 4; 5; 5; 5000
[PASS] "& Vanguard & 112 & 2 & 61 & 61 & 61 & 61 & 1200"
       paper: 112; 2; 61; 61; 61; 61; 1200
       data:  112; 2; 61; 61; 61; 61; 1200
[PASS] "& Entry Guard & 218 & 8 & 16 & 16 & 31 & 31 & 9300"
       paper: 218; 8; 16; 16; 31; 31; 9300
       data:  218; 8; 16; 16; 31; 31; 9300
[PASS] "R2 (Day 1, 10:00) & Intro. Point & 101 & 2 & 3 & 9 & 52 & 52 & 850"
       paper: Day 1 10:00; 101; 2; 3; 9; 52; 52; 850
       data:  Day 1 10:00 (IP row day_label / experiment_time_utc); 101; 2; 3; 9; 52; 52; 850
[PASS] "& Middle 1 & 192 & 4 & 5 & 7 & 13 & 13 & 5000"
       paper: 192; 4; 5; 7; 13; 13; 5000
       data:  192; 4; 5; 7; 13; 13; 5000
[PASS] "& Vanguard & 76 & 3 & 3 & 3 & 3 & 4 & 1200"
       paper: 76; 3; 3; 3; 3; 4; 1200
       data:  76; 3; 3; 3; 3; 4; 1200
[PASS] "& Entry Guard & 284 & 10 & 17 & 17 & 21 & 62 & 9300"
       paper: 284; 10; 17; 17; 21; 62; 9300
       data:  284; 10; 17; 17; 21; 62; 9300
[PASS] "R3 (Day 1, 18:00) & Intro. Point & 74 & 3 & 9 & 11 & 163 & 163 & 850"
       paper: Day 1 18:00; 74; 3; 9; 11; 163; 163; 850
       data:  Day 1 18:00 (IP row day_label / experiment_time_utc); 74; 3; 9; 11; 163; 163; 850
[PASS] "& Middle 1 & 129 & 3 & 5 & 6 & 7 & 7 & 4000"
       paper: 129; 3; 5; 6; 7; 7; 4000
       data:  129; 3; 5; 6; 7; 7; 4000
[PASS] "& Vanguard & 85 & 2 & 2 & 4 & 12 & 12 & 1200"
       paper: 85; 2; 2; 4; 12; 12; 1200
       data:  85; 2; 2; 4; 12; 12; 1200
[PASS] "& Entry Guard & 249 & 11 & 25 & 26 & 26 & 78 & 9300"
       paper: 249; 11; 25; 26; 26; 78; 9300
       data:  249; 11; 25; 26; 26; 78; 9300
[PASS] "R4 (Day 2, 02:00) & Intro. Point & 81 & 3 & 4 & 4 & 4 & 8 & 850"
       paper: Day 2 02:00; 81; 3; 4; 4; 4; 8; 850
       data:  Day 2 02:00 (IP row day_label / experiment_time_utc); 81; 3; 4; 4; 4; 8; 850
[PASS] "& Middle 1 & 148 & 4 & 7 & 8 & 8 & 11 & 4000"
       paper: 148; 4; 7; 8; 8; 11; 4000
       data:  148; 4; 7; 8; 8; 11; 4000
[PASS] "& Vanguard & 107 & 3 & 5 & 5 & 6 & 10 & 1200"
       paper: 107; 3; 5; 5; 6; 10; 1200
       data:  107; 3; 5; 5; 6; 10; 1200
[PASS] "& Entry Guard & 256 & 13 & 21 & 45 & 49 & 123 & 9900"
       paper: 256; 13; 21; 45; 49; 123; 9900
       data:  256; 13; 21; 45; 49; 123; 9900
[PASS] "R5 (Day 2, 10:00) & Intro. Point & 101 & 6 & 11 & 30 & 178 & 178 & 1500"
       paper: Day 2 10:00; 101; 6; 11; 30; 178; 178; 1500
       data:  Day 2 10:00 (IP row day_label / experiment_time_utc); 101; 6; 11; 30; 178; 178; 1500
[PASS] "& Middle 1 & 158 & 6 & 10 & 13 & 16 & 17 & 4100"
       paper: 158; 6; 10; 13; 16; 17; 4100
       data:  158; 6; 10; 13; 16; 17; 4100
[PASS] "& Vanguard & 148 & 38 & 60 & 61 & 76 & 142 & 1200"
       paper: 148; 38; 60; 61; 76; 142; 1200
       data:  148; 38; 60; 61; 76; 142; 1200
[PASS] "& Entry Guard & 180 & 7 & 11 & 14 & 15 & 167 & 4800"
       paper: 180; 7; 11; 14; 15; 167; 4800
       data:  180; 7; 11; 14; 15; 167; 4800
[PASS] "R6 (Day 2, 18:00) & Intro. Point & 84 & 3 & 14 & 233 & 324 & 324 & 1400"
       paper: Day 2 18:00; 84; 3; 14; 233; 324; 324; 1400
       data:  Day 2 18:00 (IP row day_label / experiment_time_utc); 84; 3; 14; 233; 324; 324; 1400
[PASS] "& Middle 1 & 147 & 3 & 4 & 9 & 10 & 10 & 4100"
       paper: 147; 3; 4; 9; 10; 10; 4100
       data:  147; 3; 4; 9; 10; 10; 4100
[PASS] "& Vanguard & 161 & 11 & 19 & 49 & 66 & 251 & 1200"
       paper: 161; 11; 19; 49; 66; 251; 1200
       data:  161; 11; 19; 49; 66; 251; 1200
[PASS] "& Entry Guard & 98 & 7 & 14 & 23 & 177 & 185 & 4800"
       paper: 98; 7; 14; 23; 177; 185; 4800
       data:  98; 7; 14; 23; 177; 185; 4800
[PASS] "R7 (Day 3, 18:00) & Intro. Point & 75 & 3 & 4 & 4 & 4 & 11 & 1900"
       paper: Day 3 18:00; 75; 3; 4; 4; 4; 11; 1900
       data:  Day 3 18:00 (IP row day_label / experiment_time_utc); 75; 3; 4; 4; 4; 11; 1900
[PASS] "& Middle 1 & 164 & 4 & 6 & 7 & 9 & 10 & 4800"
       paper: 164; 4; 6; 7; 9; 10; 4800
       data:  164; 4; 6; 7; 9; 10; 4800
[PASS] "& Vanguard & 95 & 3 & 3 & 6 & 20 & 24 & 1300"
       paper: 95; 3; 3; 6; 20; 24; 1300
       data:  95; 3; 3; 6; 20; 24; 1300
[PASS] "& Entry Guard & 212 & 14 & 21 & 73 & 166 & 166 & 4800"
       paper: 212; 14; 21; 73; 166; 166; 4800
       data:  212; 14; 21; 73; 166; 166; 4800
[PASS] "R8 (Day 4, 02:00) & Intro. Point & 91 & 3 & 5 & 6 & 6 & 8 & 1900"
       paper: Day 4 02:00; 91; 3; 5; 6; 6; 8; 1900
       data:  Day 4 02:00 (IP row day_label / experiment_time_utc); 91; 3; 5; 6; 6; 8; 1900
[PASS] "& Middle 1 & 198 & 7 & 11 & 14 & 14 & 53 & 4800"
       paper: 198; 7; 11; 14; 14; 53; 4800
       data:  198; 7; 11; 14; 14; 53; 4800
[PASS] "& Vanguard & 89 & 3 & 3 & 4 & 4 & 6 & 1300"
       paper: 89; 3; 3; 4; 4; 6; 1300
       data:  89; 3; 3; 4; 4; 6; 1300
[PASS] "& Entry Guard & 191 & 16 & 28 & 62 & 62 & 193 & 4800"
       paper: 191; 16; 28; 62; 62; 193; 4800
       data:  191; 16; 28; 62; 62; 193; 4800
[PASS] "R9 (Day 4, 10:00) & Intro. Point & 50 & 2 & 2 & 3 & 6 & 10 & 2000"
       paper: Day 4 10:00; 50; 2; 2; 3; 6; 10; 2000
       data:  Day 4 10:00 (IP row day_label / experiment_time_utc); 50; 2; 2; 3; 6; 10; 2000
[PASS] "& Middle 1 & 90 & 2 & 3 & 3 & 3 & 4 & 4800"
       paper: 90; 2; 3; 3; 3; 4; 4800
       data:  90; 2; 3; 3; 3; 4; 4800
[PASS] "& Vanguard & 48 & 2 & 2 & 3 & 3 & 3 & 1300"
       paper: 48; 2; 2; 3; 3; 3; 1300
       data:  48; 2; 2; 3; 3; 3; 1300
[PASS] "& Entry Guard & 86 & 5 & 18 & 40 & 40 & 84 & 4400"
       paper: 86; 5; 18; 40; 40; 84; 4400
       data:  86; 5; 18; 40; 40; 84; 4400

PASS 100, FAIL 0; total 100
```

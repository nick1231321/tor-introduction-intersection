# Reproducibility targets. Data lives in ../generated/ (never edited here).
#   make verify            recompute + check every claim (exit != 0 on FAIL / data mismatch)
#   make checks MOD=name   run one checks/ module only (e.g. MOD=convergence)
#   make tables            regenerate \input-able table bodies + figures from the data
#   make report            open the last verify report
.PHONY: verify checks tables figures all report clean
verify:  ; python3 verify.py
checks:  ; python3 verify.py $(if $(MOD),--module $(MOD),) --out ''
tables:  ; python3 generate.py
figures: tables
all: verify tables
report:  ; @cat out/verify_report.md
clean:   ; rm -f out/verify_report.md out/tables/*.tex

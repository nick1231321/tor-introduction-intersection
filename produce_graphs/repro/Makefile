# Regenerate every data-derived table body and figure of the paper from data/.
.PHONY: tables figures clean
tables:  ; python3 generate.py
figures: tables
clean:   ; rm -f out/tables/*.tex out/figures/*.pdf

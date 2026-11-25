PY ?= python3
.PHONY: verify fetch-data
verify:
	$(PY) -I verify.py CLAIMS.md
fetch-data:
	$(PY) data/fetch_metr.py

# MOSAIC RESCUE, reproduction entry points.
#
# This is a thin wrapper. The implementation lives in src/verify.py so that the
# same checks run identically on a machine without make, which is where this
# analysis was actually produced.
#
# `make verify` needs no patient data. `make all` needs the local dataset
# declared in config/paths.yaml, which is gitignored.

PY ?= python

.PHONY: help verify figures notebooks all

help:
	@echo "verify     everything that runs without patient data (src/verify.py)"
	@echo "figures    re-render all publication figures (needs local data)"
	@echo "notebooks  rebuild and execute the eight notebooks (needs local data)"
	@echo "all        figures + notebooks + verify"

verify:
	@$(PY) src/verify.py

figures:
	@$(PY) src/figures/render_all.py

notebooks:
	@$(PY) src/nb/build_all.py

all: figures notebooks verify

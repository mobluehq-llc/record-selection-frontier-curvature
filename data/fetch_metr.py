#!/usr/bin/env python3
"""Fetch the METR public run files and verify them against the pinned SHA-256 (stdlib only).
The METR repository (github.com/METR/eval-analysis-public) carries no licence file, so these files are NOT redistributed here.
Needed only to RE-RUN the simulations/real-data runs; `make verify` does not need them (it reads the stored results).
Usage (from the bundle root): python3 data/fetch_metr.py"""
import hashlib, os, sys, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://raw.githubusercontent.com/METR/eval-analysis-public/main/"
FILES = [("reports/time-horizon-1-0/data/raw/runs.jsonl", "data/metr/runs_v1_0.jsonl"),
         ("reports/time-horizon-1-1/data/raw/runs.jsonl", "holdout_data/runs_v1_1.jsonl"),
         ("data/external/release_dates.yaml", "data/metr/release_dates.yaml"),
         ("data/external/release_dates.yaml", "holdout_data/release_dates_main.yaml")]
want = {l.split()[1]: l.split()[0] for l in open(os.path.join(ROOT, "data", "SHA256SUMS_METR.txt")) if l.strip()}
bad = 0
for src, dst in FILES:
    p = os.path.join(ROOT, dst); os.makedirs(os.path.dirname(p), exist_ok=True)
    data = urllib.request.urlopen(BASE + src, timeout=120).read(); h = hashlib.sha256(data).hexdigest()
    if h != want[dst]: print("MISMATCH %s want %s got %s" % (dst, want[dst], h)); bad += 1; continue
    open(p, "wb").write(data); print("ok", dst, h)
sys.exit(1 if bad else 0)

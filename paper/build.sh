#!/bin/bash
# numbers and tables, figures, then main.pdf and supplement.pdf (two passes each so that cross-document references resolve)
set -e; cd "$(dirname "$0")"
/usr/local/bin/python3 -I make_numbers.py
/usr/local/bin/python3 make_figs.py
for i in 1 2 3; do tectonic -X compile --keep-intermediates --outdir . main.tex 2>&1 | grep -iE "^error|warning: .*undefined|Overfull" || true; tectonic -X compile --keep-intermediates --outdir . supplement.tex 2>&1 | grep -iE "^error|undefined" || true; done

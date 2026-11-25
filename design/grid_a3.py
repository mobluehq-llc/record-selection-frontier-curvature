"""EXPLORATORY Design Amendment 3 cell table (idea F).  Every A3 cell REUSES an Amendment-2 cell (same simulator config, same seeds [79, a2_index, rep] for the data), so A3 rows pair with A2 rows by (cell, rep).
The A3 tests use new randomness: SeedSequence([83, a3_index, rep]).  reps = the A2 count (so every paired comparison has the full A2 sample)."""
import hashlib, json
import grid_a2 as g2
NAMES = [c['name'] for c in g2.CELLS]
USE = ['R_null_cal', 'R_null_val', 'R_rr0.5', 'R_rr1.25', 'R_rr1.5', 'R_rr2', 'R_rr3', 'R_rr4', 'R_logi_dec', 'R_logi_mid',
       'E_null_val', 'E_rr2', 'K2_null_val', 'K2_rr2', 'N50_null_val', 'N50_rr2', 'MF1_null_val']
CELLS = []
for nm in USE:
    c2 = g2.CELLS[NAMES.index(nm)]
    CELLS.append(dict(name=nm, a2_index=NAMES.index(nm), fam=c2['fam'], role=c2['role'], reps=c2['reps'], chunk=500, cost=0.05, cfg=c2['cfg']))
def grid_hash(): return hashlib.sha256(json.dumps(CELLS, sort_keys=True).encode()).hexdigest()[:16]
if __name__ == '__main__':
    print(len(CELLS), 'cells; grid', grid_hash(), '; reps', sum(c['reps'] for c in CELLS), '; est core-h', round(sum(c['reps'] * c['cost'] for c in CELLS) / 3600, 1))

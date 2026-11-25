#!/usr/bin/env python3
"""F bundle: (1) regenerate every number and table of the paper from the stored results and require identity with the arXiv v10 files; (2) re-run each CLAIMS.md row's check from its evidence file. Exit 1 on any mismatch,
unreadable evidence, or unverifiable row. Silence is never a pass (never silent).

CLAIMS.md row:  | # | claim | evidence | check | status |
  evidence = path (relative to CLAIMS.md) of the file the check reads
  check    = one of
     json:<dotted.path> <op> <value> [+-tol]    e.g.  json:coverage.e4r >= 0.95
                                                       json:fpr.E1 == 0.043 +- 0.0005
     csv:<column>@<col>=<val> <op> <value>      first row where col==val, read column
     grep:<regex>                               regex must match at least once in evidence
     count:<regex> == <n>                       exact number of matches
     sha256:<hex>                               hash of evidence file
     manual                                     FAILS (exit 1) unless --allow-manual; list is printed
  ops: == != >= <= > <
Status column: 'frozen'/'verified'/anything is ignored except 'dropped' (row skipped, and printed).
Usage: verify.py CLAIMS.md [--allow-manual]
"""
import sys, re, json, csv, hashlib, operator
from pathlib import Path
OPS = {"==": operator.eq, "!=": operator.ne, ">=": operator.ge, "<=": operator.le, ">": operator.gt, "<": operator.lt}

def rows(md):
    for ln, line in enumerate(md.splitlines(), 1):
        if not line.strip().startswith("|"): continue
        cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
        if len(cells) < 5 or set("".join(cells)) <= set("-: ") or cells[0] == "#": continue
        yield ln, cells[0], cells[1], cells[2].strip("`"), cells[3], cells[4]

def cmp(got, expr):
    m = re.match(r"\s*(==|!=|>=|<=|>|<)\s*(\S+)(?:\s*(?:\+-|±)\s*(\S+))?\s*$", expr)
    if not m: raise ValueError("bad comparison: " + expr)
    op, want, tol = m.group(1), m.group(2), m.group(3)
    try:
        g, w = float(got), float(want)
        if tol is not None and op == "==": return abs(g - w) <= float(tol), f"got {g} want {w} +-{tol}"
        return OPS[op](g, w), f"got {g} want {op} {w}"
    except (TypeError, ValueError):
        return OPS[op](str(got), want.strip("'\"")), f"got {got!r} want {op} {want}"

def run(path, check, base):
    ev = base / path
    if not ev.is_file(): return False, f"MISSING evidence file {path}"
    kind, _, rest = check.partition(":")
    if kind == "sha256":
        h = hashlib.sha256(ev.read_bytes()).hexdigest()
        ok = h == rest.strip().lower(); return ok, ("sha256 " + h[:16] + "..." if ok else f"MISMATCH want {rest.strip()} got {h}")
    text = ev.read_text(errors="replace")
    if kind == "grep":
        ok = re.search(rest, text, re.M) is not None
        return ok, "pattern found" if ok else f"MISMATCH pattern {rest!r} not found"
    if kind == "count":
        m = re.match(r"(.*)\s*==\s*(\d+)\s*$", rest)
        if not m: return False, "bad count check"
        n = len(re.findall(m.group(1).strip(), text, re.M))
        return n == int(m.group(2)), f"MISMATCH want {m.group(2)} got {n}" if n != int(m.group(2)) else f"count {n}"
    if kind == "json":
        m = re.match(r"([^\s=!<>]+)\s*(.*)$", rest)
        cur = json.loads(text)
        try:
            for p in m.group(1).split("."): cur = cur[int(p)] if isinstance(cur, list) else cur[p]
        except (KeyError, IndexError, ValueError, TypeError):
            return False, f"MISMATCH path {m.group(1)} not found"
        ok, msg = cmp(cur, m.group(2)); return ok, ("" if ok else "MISMATCH ") + msg
    if kind == "csv":
        m = re.match(r"([^@\s]+)@([^=\s]+)=(\S+)\s*(.*)$", rest)
        if not m: return False, "bad csv check"
        col, kc, kv, expr = m.groups()
        for r in csv.DictReader(text.splitlines()):
            if r.get(kc) == kv:
                if col not in r: return False, f"MISMATCH no column {col}"
                ok, msg = cmp(r[col], expr); return ok, ("" if ok else "MISMATCH ") + msg
        return False, f"MISMATCH no row with {kc}={kv}"
    return False, f"unknown check type {kind!r}"

def regen(base):
    """Re-run paper/make_numbers.py on the stored results in a temp copy of paper/ and require numbers.tex and every shipped table_*.tex to be identical."""
    import subprocess, tempfile, shutil, os
    paper = base / "paper"; tmp = Path(tempfile.mkdtemp()) / "paper"; shutil.copytree(paper, tmp)
    r = subprocess.run([sys.executable, "-I", "make_numbers.py"], cwd=tmp, env=dict(os.environ, F_ROOT=str(base.resolve())), capture_output=True, text=True)
    if r.returncode: print("FAIL  regen: make_numbers.py exited", r.returncode, r.stderr[-400:]); return 1
    strip = lambda p: "\n".join(l for l in p.read_text().splitlines() if not l.startswith("% generated"))
    bad = 0; names = ["numbers.tex"] + sorted(p.name for p in paper.glob("table_*.tex"))
    for nme in names:
        if not (tmp / nme).is_file() or strip(tmp / nme) != strip(paper / nme): print("FAIL  regen: " + nme + " differs from the shipped arXiv v10 file"); bad += 1
    nm = len((tmp / "numbers.tex").read_text().split("\\newcommand")) - 1
    nmi = len(re.findall(r"^[A-Za-z]+ = ", (paper / "numbers_manifest.txt").read_text(), re.M))
    if nm != nmi: print(f"FAIL  regen: {nm} macros vs {nmi} manifest lines"); bad += 1
    if (tmp / "numbers_manifest.txt").read_text() != (paper / "numbers_manifest.txt").read_text(): print("FAIL  regen: numbers_manifest.txt differs"); bad += 1
    if not bad: print(f"PASS  regen: numbers.tex ({nm} macros) and {len(names)-1} tables regenerated from stored results and identical to the arXiv v10 files")
    shutil.rmtree(tmp.parent); return bad

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    allow_manual = "--allow-manual" in sys.argv
    if not args: sys.exit("usage: verify.py CLAIMS.md [--allow-manual]")
    cp = Path(args[0]); base = cp.parent
    n = 1; bad = regen(base); manual = []
    for ln, num, claim, ev, check, status in rows(cp.read_text()):
        if status.lower() == "dropped": print(f"SKIP  #{num} (dropped)"); continue
        n += 1
        if check.strip() == "manual" or not check.strip():
            manual.append(num); print(f"MANUAL #{num}: {claim[:60]}")
            if not allow_manual: bad += 1
            continue
        try: ok, msg = run(ev, check.strip(), base)
        except Exception as e: ok, msg = False, f"ERROR {type(e).__name__}: {e}"
        print(("PASS  " if ok else "FAIL  ") + f"#{num} [{ev}] {msg}")
        bad += (not ok)
    if n == 0: print("FAIL: no checkable rows in CLAIMS.md (cannot measure)"); sys.exit(1)
    print(f"\n{n - bad}/{n} rows verified; {bad} failing; manual rows: {manual or 'none'}")
    sys.exit(1 if bad else 0)

if __name__ == "__main__": main()

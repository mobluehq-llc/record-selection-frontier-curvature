#!/usr/bin/env python3
"""Build the arXiv version of paper F: F_arxiv_v18.pdf, F_arxiv_supplement_v18.pdf, F_arxiv_source_v18.tar.gz.
Run after ./build.sh (needs the current main.bbl, supplement.bbl, main.aux, supplement.aux, numbers.tex, table_*.tex, figs/).
Usage: python3 make_arxiv.py OUTDIR
The source bundle holds sanitized copies (comments removed, draft marking branches resolved to the arXiv form).
The PDFs are compiled from the sanitized bundle itself, in a fresh directory."""
import os, re, sys, shutil, subprocess, tarfile, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.abspath(sys.argv[1]); os.makedirs(OUT, exist_ok=True)
FLAGLINE = r"\newif\ifarxiv \IfFileExists{arxiv.flag}{\arxivtrue}{\arxivfalse}"
HOOK = r"\ifarxiv\else\AddToHook{shipout/foreground}{\put(0.5\paperwidth,-0.42in){\makebox[0pt]{\small\sffamily DRAFT, not for distribution}}}\fi"
DATE = r"\date{\ifarxiv 26 November 2026\else Draft v18 of 26 November 2026. DRAFT, not for distribution.\fi}"
def strip_comments(s):
    out = []
    for ln in s.split("\n"):
        if ln.lstrip().startswith("%"): continue
        ln = re.sub(r"(?<!\\)%.*$", "%", ln) if re.search(r"(?<!\\)%", ln) else ln
        if ln == "%": ln = "%"
        out.append(ln)
    return "\n".join(out)
def sanitize(name, s):
    if name in ("main.tex", "supplement.tex"):
        s = strip_comments(s)
        for a, b in ((FLAGLINE, ""), (HOOK, ""), (DATE, r"\date{26 November 2026}")):
            assert a in s, (name, a[:40]); s = s.replace(a, b)
        s = s.replace(r"\ifarxiv", "")  # no leftovers expected
        assert "arxiv.flag" not in s and "arxivtrue" not in s and "DRAFT, not" not in s, name
    if name.endswith(".bbl"):
        return s  # bibtex output; its %Control lines are bst settings, harmless
    return strip_comments(s)
src = tempfile.mkdtemp(prefix="arxsrc_"); files = ["main.tex", "supplement.tex", "numbers.tex", "main.bbl", "supplement.bbl", "refs.bib"]
files += sorted(f for f in os.listdir(HERE) if f.startswith("table_") and f.endswith(".tex"))
used = set(re.findall(r"\\input\{([^}]+)\}", open(os.path.join(HERE, "main.tex")).read() + open(os.path.join(HERE, "supplement.tex")).read()))
files = [f for f in files if f in ("main.tex","supplement.tex","main.bbl","supplement.bbl","refs.bib") or f in used]
for f in files:
    s = open(os.path.join(HERE, f), encoding="utf-8").read(); open(os.path.join(src, f), "w", encoding="utf-8").write(sanitize(f, s))
figs = sorted(set(re.findall(r"figs/[\w.]+\.pdf", open(os.path.join(HERE, "main.tex")).read() + open(os.path.join(HERE, "supplement.tex")).read())))
os.makedirs(os.path.join(src, "figs"))
for f in figs: shutil.copy(os.path.join(HERE, f), os.path.join(src, f))
open(os.path.join(src, "00README.XXX"), "w").write("main.tex toplevelfile\nsupplement.tex ignore\n")
def compile_dir(d, passes=3):
    for i in range(passes):
        for t in ("main", "supplement"):
            cmd = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", t + ".tex"] if shutil.which("pdflatex") else ["tectonic", "-X", "compile", "--keep-intermediates", "--outdir", d, os.path.join(d, t + ".tex")]  # arXiv's default engine when present
            r = subprocess.run(cmd, capture_output=True, text=True, cwd=d)
            if r.returncode != 0: print(r.stdout[-3000:], r.stderr[-3000:]); sys.exit("COMPILE FAILED " + t)
            if i == passes - 1: yield t, r.stderr + open(os.path.join(d, t + ".log"), errors="replace").read() if os.path.exists(os.path.join(d, t + ".log")) else r.stderr
# cross-document references: arXiv strips .aux, so the bundle ships with literal numbers (read from the first-pass aux files) and no xr/externaldocument
w = tempfile.mkdtemp(prefix="arxbuild_"); shutil.copytree(src, w, dirs_exist_ok=True)
logs = dict(compile_dir(w))
for t in logs: assert re.search(r"undefined|Error|error:", logs[t]) is None, (t, logs[t][-1500:])
def labels(aux): return dict(re.findall(r"\\newlabel\{([^}]+)\}\{\{([^}]*)\}", open(aux).read()))
for t, other, pre, ex in (("main", "supplement", "S-", r"\\externaldocument\[S-\]\{supplement\}"), ("supplement", "main", "M-", r"\\externaldocument\[M-\]\{main\}")):
    lab = labels(os.path.join(w, other + ".aux")); fp = os.path.join(src, t + ".tex"); s_ = open(fp, encoding="utf-8").read()
    s_, n_ = re.subn(r"\\ref\{" + re.escape(pre) + r"([^}]+)\}", lambda m: lab[m.group(1)], s_); assert n_ > 0, t
    s_, n2 = re.subn(ex, "", s_); assert n2 == 1, t
    s_ = s_.replace("\\usepackage{xr}", ""); assert "externaldocument" not in s_ and "\\usepackage{xr" not in s_ and "\\ref{" + pre not in s_, t
    open(fp, "w", encoding="utf-8").write(s_)
# the bundle now needs no .aux: rebuild from it in a fresh directory, none supplied
w = tempfile.mkdtemp(prefix="arxbuild_"); shutil.copytree(src, w, dirs_exist_ok=True)
assert not [f for f in os.listdir(w) if f.endswith(".aux")]
logs = dict(compile_dir(w, passes=3))
for t in logs: assert re.search(r"undefined|Error|error:", logs[t]) is None, (t, logs[t][-1500:])
for f in ("main.bbl", "supplement.bbl"): assert os.path.exists(os.path.join(src, f))
for t in ("main", "supplement"):
    txt = subprocess.run(["pdftotext", os.path.join(w, t + ".pdf"), "-"], capture_output=True, text=True).stdout
    assert "[?" not in txt and "?]" not in txt and "??" not in txt, (t, "unresolved citation")
    nb = open(os.path.join(src, t + ".bbl")).read().count("\\bibitem"); assert nb >= (25 if t == "main" else 4), (t, nb); print(t, "bibitems", nb)
shutil.copy(os.path.join(w, "main.pdf"), os.path.join(OUT, "F_arxiv_v18.pdf")); shutil.copy(os.path.join(w, "supplement.pdf"), os.path.join(OUT, "F_arxiv_supplement_v18.pdf"))
tp = os.path.join(OUT, "F_arxiv_source_v18.tar.gz")
with tarfile.open(tp, "w:gz") as tf:
    for root, _, fs in os.walk(src):
        for f in sorted(fs): p = os.path.join(root, f); tf.add(p, arcname=os.path.relpath(p, src), filter=lambda ti: (setattr(ti, "uid", 0), setattr(ti, "gid", 0), setattr(ti, "uname", ""), setattr(ti, "gname", ""), setattr(ti, "mtime", 0), ti)[-1])
print("bundle files:", sorted(os.path.relpath(os.path.join(r, f), src) for r, _, fs in os.walk(src) for f in fs)); print("wrote", OUT)

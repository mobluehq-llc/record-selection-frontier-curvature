"""Write numbers.tex, the generated tables and numbers_manifest.txt from the committed result files of idea F (and U).
Every macro records the file and key it came from; a missing key or table row is a hard error.  No number in main.tex or
supplement.tex is typed by hand except dates, counts of amendments and definitions.  Run: python3 -I make_numbers.py"""
import json, os, re, csv
HERE = os.path.dirname(os.path.abspath(__file__)); F = os.environ.get('F_ROOT') or os.path.dirname(HERE); U = os.path.join(F, "U_frontier_trend_forecast_coverage")
MAN, TEX = [], []


def rel(p): p = os.path.abspath(p); return ('paper/' + os.path.relpath(p, HERE)) if p.startswith(HERE + os.sep) else os.path.relpath(p, F)
def put(name, value, src, how=""):
    assert re.fullmatch(r"[A-Za-z]+", name), name
    assert not any(l.startswith("\\newcommand{\\%s}" % name) for l in TEX), "duplicate " + name
    TEX.append("\\newcommand{\\%s}{%s}" % (name, value)); MAN.append("%s = %s   <- %s %s" % (name, value, src, how))
def f(x, d): return "%.*f" % (d, float(x))
def sgn(x, d): return ("+" if float(x) >= 0 else "$-$") + "%.*f" % (d, abs(float(x)))
def neg(x, d): return ("$-$" if float(x) < 0 else "") + "%.*f" % (d, abs(float(x)))
def commas(x): return "{:,}".format(int(x)).replace(",", "{,}")
def pv(p):
    p = float(p)
    return "%.4f" % p if p < 0.01 else ("%.3f" % p if p < 0.1 else "%.2f" % p)
def write(name, lines): open(os.path.join(HERE, name), "w").write("\n".join(l.replace("[", "{[}").replace("]", "{]}").replace(",", ", ").replace(",  ", ", ").replace("{, }", "{,}") for l in lines) + "\n")

# ------------------------------------------------------------------ real data (exploratory)
RP = os.path.join(F, "real_data", "out", "real_v10.json"); R = json.load(open(RP)); src = rel(RP)
put("nModels", R["M"], src, "M"); put("nRecords", R["n_records"], src, "n_records"); put("nNonRecords", R["M"] - R["n_records"], src, "M - n_records")
put("spanYears", f(R["span_years"], 2), src, "span_years"); put("linSlope", f(R["linear_slope_dbl_per_yr"], 2), src, "linear_slope_dbl_per_yr")
put("linDbl", f(R["linear_doubling_days"], 0), src, "linear_doubling_days")
g = R["reg"]
put("betaAll", sgn(g["reg_c"], 3), src, "reg.reg_c"); put("hcT", f(g["hc3_z"], 2), src, "reg.hc3_z"); put("olsT", f(g["ols_z"], 2), src, "reg.ols_z")
put("hcPup", pv(g["hc3_pup"]), src, "reg.hc3_pup"); put("hcPdn", pv(g["hc3_pdn"]), src, "reg.hc3_pdn"); put("olsPup", pv(g["ols_pup"]), src, "reg.ols_pup")
put("wildPup", pv(g["wild_pup"]), src, "reg.wild_pup"); put("permPup", pv(g["perm_pup"]), src, "reg.perm_pup")
put("wildOverHc", f(g["wild_pup"] / g["hc3_pup"], 1), src, "reg.wild_pup / reg.hc3_pup")
put("hcCiLo", sgn(R["hc3_ci95_beta2"][0], 3), src, "hc3_ci95_beta2[0]"); put("hcCiHi", sgn(R["hc3_ci95_beta2"][1], 3), src, "hc3_ci95_beta2[1]")
put("hcSe", f(R["hc3_se"], 3), src, "hc3_se"); put("rrEqAll", f(R["rr_eq_allmodel"], 1), src, "rr_eq_allmodel")
c = R["calendar_allmodel"]
put("rateStart", f(c["rate_start"], 2), src, "calendar_allmodel.rate_start"); put("rateEnd", f(c["rate_end"], 2), src, "calendar_allmodel.rate_end")
put("dblStart", f(c["dbl_days_start"], 0), src, "calendar_allmodel.dbl_days_start"); put("dblEnd", f(c["dbl_days_end"], 0), src, "calendar_allmodel.dbl_days_end")
put("rrHat", f(c["rr_hat"], 1), src, "calendar_allmodel.rr_hat")
p = R["pb"]; put("pbDraws", commas(p["sota_nvalid"]), src, "pb.sota_nvalid")
NAMES = dict(sota="Sota", mir="Mir", heck="Heck", ipw="Ipw", audit="Audit", rrate="Rrate", gap="Gap", contr="Contr", thr="Thr", ccl="Ccl", tcl="Tcl")
for k in ("sota", "mir", "heck", "ipw", "audit", "contr", "thr"):
    put("real%sBeta" % NAMES[k], sgn(p[k + "_c"], 3), src, "pb.%s_c" % k); put("real%sNull" % NAMES[k], sgn(p[k + "_nullmean"], 3), src, "pb.%s_nullmean" % k)
for k in ("sota", "mir", "heck", "ipw", "audit", "rrate", "gap", "contr", "thr"):
    put("real%sPup" % NAMES[k], pv(p[k + "_pup"]), src, "pb.%s_pup" % k); put("real%sPdn" % NAMES[k], pv(p[k + "_pdn"]), src, "pb.%s_pdn" % k)
put("realGapObs", neg(p["gap_c"], 2), src, "pb.gap_c"); put("realGapNull", neg(p["gap_nullmean"], 2), src, "pb.gap_nullmean")
put("realRrateObs", neg(p["rrate_c"], 2), src, "pb.rrate_c"); put("realRrateNull", neg(p["rrate_nullmean"], 2), src, "pb.rrate_nullmean")
for k in ("sota", "mir", "heck", "ipw", "audit"): put("real%sRrEq" % NAMES[k], f(R["rr_eq_" + k], 1), src, "rr_eq_" + k)
a = R["audit_draws"]
put("auditMed", sgn(a["median"], 3), src, "audit_draws.median"); put("auditQlo", f(a["q25"], 3), src, "audit_draws.q25"); put("auditQhi", f(a["q75"], 3), src, "audit_draws.q75")
put("auditMin", f(a["min"], 3), src, "audit_draws.min"); put("auditMax", f(a["max"], 3), src, "audit_draws.max")
mb = R["model_bootstrap"]
for k in ("all", "sota", "heck", "audit"):
    K = dict(all="All", sota="Sota", heck="Heck", audit="Audit")[k]
    put("mb%sLo" % K, sgn(mb[k]["lo"], 3), src, "model_bootstrap.%s.lo" % k); put("mb%sHi" % K, sgn(mb[k]["hi"], 3), src, "model_bootstrap.%s.hi" % k)
put("mbDraws", commas(mb["all"]["n"]), src, "model_bootstrap.all.n"); put("mbAllRrEqLo", f(mb["all"]["rr_eq_lo"], 1), src, "model_bootstrap.all.rr_eq_lo")
r = mb["rr_hat_allmodel"]
put("rrHatLo", f(r["lo"], 1), src, "model_bootstrap.rr_hat_allmodel.lo"); put("rrHatHi", f(r["hi"], 1), src, "model_bootstrap.rr_hat_allmodel.hi")
put("rrHatMed", f(r["median"], 1), src, "model_bootstrap.rr_hat_allmodel.median"); put("rrHatNonpos", r["n_start_rate_nonpositive"], src, "model_bootstrap.rr_hat_allmodel.n_start_rate_nonpositive")
put("loroMax", f(p["loro_max"], 3), src, "pb.loro_max"); put("loroSd", f(p["loro_sd"], 3), src, "pb.loro_sd")
put("preregReal", "\\texttt{%s}" % R["pins"]["prereg_commit"], src, "pins.prereg_commit")
put("numpyV", R["pins"]["numpy"], src, "pins.numpy"); put("scipyV", R["pins"]["scipy"], src, "pins.scipy")
put("runsSha", "\\texttt{%s\\ldots}" % R["pins"]["runs_sha256"][:16], src, "pins.runs_sha256[:16]")
hz = {m[0]: m[2] for m in R["model_horizons"]}
put("lastHorizonH", f(2 ** hz["Claude Opus 4.5"] / 60, 1), src, "2^model_horizons[Claude Opus 4.5]/60 (hours, our refit)")
# Holm step-down over the pre-registered family of six (upward p)
fam = ["hc3", "audit", "heck", "rrate", "contr", "thr"]; pu = dict(hc3=g["hc3_pup"], **{k: p[k + "_pup"] for k in fam[1:]})
order = sorted(fam, key=lambda k: pu[k]); holm, run = {}, 0.0
for i, k in enumerate(order): run = max(run, min(1.0, (len(fam) - i) * pu[k])); holm[k] = run
for k, K in (("hc3", "Hc"), ("audit", "Audit"), ("heck", "Heck"), ("rrate", "Rrate"), ("contr", "Contr"), ("thr", "Thr")):
    put("holm" + K, pv(holm[k]) if holm[k] < 1 else "1", src, "Holm step-down over the six upward p-values (computed here)")
# the original one-shot
OP = os.path.join(F, "results", "F_real.json"); O = json.load(open(OP)); src = rel(OP)
put("hbCiLo", sgn(O["hb_ci_lo"], 3), src, "hb_ci_lo"); put("hbCiHi", sgn(O["hb_ci_hi"], 3), src, "hb_ci_hi"); put("iidFp", pv(O["iid_F_p"]), src, "iid_F_p")

# ------------------------------------------------------------------ original pre-registered size bars (confirmatory, simulation)
SP = os.path.join(F, "results", "F_size_summary.json"); S = json.load(open(SP)); src = rel(SP)
for key, K in (("T-iid (SOTA, F-test t^2, two-sided 5%)", "origIid"), ("T-hb (SOTA, B=400 percentile 95% CI excludes 0)", "origHb"),
               ("[secondary] T-iid all-models regression", "origIidAll"), ("[secondary] T-hb all-models regression", "origHbAll")):
    s = S[key]; put(K, f(100 * s["size"], 1), src, key); put(K + "Lo", f(100 * s["cp_lo"], 1), src, key + " cp_lo"); put(K + "Hi", f(100 * s["cp_hi"], 1), src, key + " cp_hi")
    put(K + "K", s["k"], src, key + " k"); put(K + "N", commas(s["n"]), src, key + " n")
ST = os.path.join(F, "results", "F_size_summary.txt"); t = open(ST).read()
put("origMeanRecords", re.search(r"mean nSOTA ([0-9.]+)", t).group(1), rel(ST), "mean nSOTA")
assert "BAR1_PASS" in t and "BAR2_FAIL" in t

# ------------------------------------------------------------------ simulator
VP = os.path.join(F, "results", "F_simulator_validation.json"); V = json.load(open(VP)); src = rel(VP)
put("sigmaM", f(V["params"]["sigma_m"], 2), src, "params.sigma_m"); put("sigmaJ", f(V["params"]["sigma_j"], 2), src, "params.sigma_j"); put("phiFam", f(V["params"]["phi"], 2), src, "params.phi")
put("simAZero", neg(V["params"]["a0"], 2), src, "params.a0"); put("rateNull", f(V["params"]["rate_null"], 2), src, "params.rate_null"); put("dblNull", f(365.25 / V["params"]["rate_null"], 0), src, "365.25/params.rate_null")
put("simValN", V["validation_n"], src, "validation_n")
lab = dict(sd_all="residual SD, all models", sd_sota="residual SD, records", crosscorr="cross-model correlation of task outcomes", icc="family intraclass correlation", slope_all="slope, all models (doublings/y)")
write("table_simval.tex", ["%s & %.3f & %.3f & [%.3f, %.3f] & %.2f \\\\" % (lab[k], m["real"], m["sim_median"], m["sim_p05"], m["sim_p95"], m["real_pctile_in_sim"]) for k, m in V["metrics"].items()])
MAN.append("table_simval.tex   <- %s metrics.*" % src)
assert all(m["sim_p05"] <= m["real"] <= m["sim_p95"] for m in V["metrics"].values())

# ------------------------------------------------------------------ Amendment 3 (pre-registered, exploratory, synthetic)
AP = os.path.join(F, "design", "results_a3", "summary_a3.md"); A = open(AP).read(); src = rel(AP)
def table(header_start):
    i = A.index(header_start); rows = []
    for ln in A[i:].split("\n"):
        if not ln.startswith("|"):
            if rows: break
            continue
        cells = [x.strip() for x in ln.strip().strip("|").split("|")]
        if set(cells[0]) <= set("-: "): continue
        rows.append(cells)
    return rows[1:]
size = {(r[0], r[2]): r for r in table("| test | kind | cell | n valid |")}
cls = {r[0]: r for r in table("| test | size-valid | robust |")}
bias = {r[0]: r for r in table("| estimator | mean beta2 |")}
cal = {r[0]: r for r in table("| alt | start rate |")}
raw = {(r[0], r[1]): r for r in table("| test | alt | n | up5 |")}
adj = {(r[0], r[3]): r for r in table("| test | validated size up [CP] |")}
loro = {r[0]: r for r in table("| cell | n rejecting |")}
TESTS = ["ccl", "tcl", "mir", "heck", "ipw", "audit", "rrate", "gap", "contr", "thr", "sota"]
LBL = dict(ccl="censored-crossing likelihood", tcl="record-truncated likelihood", mir="mirror envelope", heck="inverse-Mills correction", ipw="naive inverse-probability weights",
           audit="random audit (25\\%)", rrate="record timing", gap="record-gap trend", contr="record-minus-all contrast", thr="threshold perturbation", sota="record-only fit", all="all-model fit")
SH = dict(ccl="censored likelihood", tcl="truncated likelihood", mir="mirror envelope", heck="inverse-Mills", ipw="naive weighting", audit="random audit", rrate="record timing", gap="record-gap trend", contr="record$-$all contrast", thr="threshold perturb.", sota="record-only fit", all="all-model fit")
FAMS = ["R_null_val", "E_null_val", "K2_null_val", "N50_null_val", "MF1_null_val"]
def rate(s): return float(s.split()[0])
def cpi(s): return s.split("[")[1].rstrip("]").split(",")
def mark(v): return {"OK": "", "inconclusive": "$^{\\dagger}$", "OUT": "$^{\\ddagger}$"}[v]
assert all((k, c_) in size for k in TESTS for c_ in FAMS)
# bias
for k in ("sota", "mir", "heck", "ipw", "audit", "all"):
    K = dict(NAMES, all="All")[k]
    put("bias" + K, f(bias[k][1], 4), src, "B4 table row %s mean beta2" % k); put("biasRr" + K, f(bias[k][4], 2), src, "B4 table row %s rr_eq" % k)
    put("biasSe" + K, f(bias[k][2], 4), src, "B4 table row %s SE" % k)
write("table_bias.tex", ["%s & %s & %s & %s & %s \\\\" % (SH[k], f(bias[k][1], 4), f(bias[k][2], 4), f(bias[k][4], 2), bias[k][5]) for k in ("sota", "ipw", "mir", "heck", "audit", "all")])
# size, main table and full table
rows = []
for k in ["sota", "ipw", "mir", "ccl", "tcl", "heck", "audit", "rrate", "gap", "contr", "thr"]:
    r = size[(k, "R_null_val")]; lo, hi = cpi(r[4])
    cells = ["%s [%s, %s]%s" % (f(rate(r[4]), 1), f(lo, 1), f(hi, 1), mark(r[7])), "%s%s" % (f(rate(r[5]), 1), mark(r[8]))]
    for c_ in FAMS[1:]: x = size[(k, c_)]; cells.append("%s%s" % (f(rate(x[4]), 1), mark(x[7])))
    rows.append("%s & %s & %s & %s \\\\" % (LBL[k], " & ".join(cells), cls[k][1], cls[k][2]))
write("table_size.tex", rows)
def r1_(x): return re.sub(r"\d+\.\d+", lambda m_: "%.1f" % float(m_.group(0)), x)  # one decimal in the compact full tables (verdicts use the unrounded values)
def nc_(x): return re.sub(r" (\{\[\}|\[).*?(\{\]\}|\])", "", x)  # rate only
def vc_(a, b): return "%s/%s" % (a.replace("inconclusive", "inc."), b.replace("inconclusive", "inc."))
write("table_sizefull.tex", ["%s & %s & %s & %s & %s & %s \\\\" % (SH[k] if c_ == "R_null_val" else "", c_.replace("_null_val", ""), r1_(size[(k, c_)][4]), r1_(nc_(size[(k, c_)][5])), r1_(nc_(size[(k, c_)][6])),
                                                                         vc_(size[(k, c_)][7], size[(k, c_)][8])) for k in TESTS for c_ in FAMS] + ["\\hline\\hline"])
for k in TESTS:
    r = size[(k, "R_null_val")]; K = NAMES[k]
    put("size%sUp" % K, f(rate(r[4]), 1), src, "size table %s R_null_val up5" % k); put("size%sTwo" % K, f(rate(r[5]), 1), src, "size table %s R_null_val two5" % k)
    put("size%sUpN" % K, f(rate(size[(k, "N50_null_val")][4]), 1), src, "size table %s N50_null_val up5" % k)
put("sizeAuditUpLo", f(cpi(size[("audit", "R_null_val")][4])[0], 1), src, "size table audit R_null_val up5 CP lo"); put("sizeAuditUpHi", f(cpi(size[("audit", "R_null_val")][4])[1], 1), src, "CP hi")
put("sizeHeckUpLo", f(cpi(size[("heck", "R_null_val")][4])[0], 1), src, "size table heck R_null_val up5 CP lo"); put("sizeHeckUpHi", f(cpi(size[("heck", "R_null_val")][4])[1], 1), src, "CP hi")
robust = [k for k in TESTS if cls[k][2] == "yes"]; valid = [k for k in TESTS if cls[k][1] == "yes"]
assert robust == ["rrate", "contr", "thr"], robust
assert valid == ["ipw", "audit", "rrate", "gap", "contr", "thr"], valid
put("nRobust", len(robust), src, "classification table: robust == yes"); put("nSizeValid", len(valid), src, "classification table: size-valid == yes"); put("nMethods", len(TESTS) - 1, src, "methods excluding the record-only reference")
dmin = min(rate(size[(k, c_)][j]) for k in robust for c_ in FAMS for j in (4, 5)); dmax = max(rate(size[(k, c_)][j]) for k in robust for c_ in FAMS for j in (4, 5))
put("robustMin", f(dmin, 1), src, "min up5/two5 over rrate, contr, thr and five null families"); put("robustMax", f(dmax, 1), src, "max of the same")
# calendar meaning of the alternatives
# CORRECTION 2026-11-23 (ERRATA.md): the calendar table in summary_a3.md was computed by analyze_a3.effect() as a secant over the first and the
# last HALF YEAR of the window (h = 0.5), not as the endpoint derivative, so it printed 304 -> 160 d for rr = 2 (ratio 1.90) and 473 -> 135 d
# for rr = 4 (ratio 3.50).  The simulated trajectories are exact (fdesign.Sim.true_L: start rate r_s = 2*rate/(1+rr), end rate rr*r_s).  The
# paper now uses the exact endpoint rates, computed here from the trajectory definition; the old table is reproduced and asserted first.
import math
RATE0 = V["params"]["rate_null"]; SPAN0 = R["span_years"]
LOGI = {"R_logi_dec": (0.35, 5.0), "R_logi_mid": (0.65, 6.0)}   # (um, ks) of design/grid_a2.py LOGI_DEC, LOGI_MID
_g2 = open(os.path.join(F, "design", "grid_a2.py")).read(); assert "LOGI_DEC = dict(truth='logi', um=0.35, ks=5.0); LOGI_MID = dict(truth='logi', um=0.65, ks=6.0)" in _g2
def true_L(nm, u):
    if nm.startswith("R_rr"):
        rr_ = float(nm[4:]); rs = RATE0 * 2.0 / (1.0 + rr_); return rs * u + 0.5 * (rr_ - 1.0) * rs / SPAN0 * u * u
    um, ks = LOGI[nm]; um *= SPAN0; k_ = ks / SPAN0; sg = lambda v: 1 / (1 + math.exp(-v))
    return RATE0 * SPAN0 * (sg(k_ * (u - um)) - sg(-k_ * um)) / (sg(k_ * (SPAN0 - um)) - sg(-k_ * um))
def ends(nm, h): return (true_L(nm, h) - true_L(nm, 0.0)) / h, (true_L(nm, SPAN0) - true_L(nm, SPAN0 - h)) / h
calx = {}
for a_ in cal:
    o0, o1 = ends(a_, 0.5); assert ("%.2f" % o0, "%.2f" % o1, "%.0f" % (365.25 / o0), "%.0f" % (365.25 / o1)) == tuple(cal[a_][1:5]), (a_, o0, o1, cal[a_])   # old half-year secants reproduced
    e0, e1 = ends(a_, 1e-6)
    if a_.startswith("R_rr"): rr_ = float(a_[4:]); assert abs(e0 - RATE0 * 2 / (1 + rr_)) < 1e-5 and abs(e1 / e0 - rr_) < 1e-5, (a_, e0, e1)   # endpoint ratio is exactly the label
    calx[a_] = ("%.2f" % e0, "%.2f" % e1, "%.0f" % (365.25 / e0), "%.0f" % (365.25 / e1))
csrc = "exact endpoint derivative of the alternative trajectory (design/fdesign.py Sim.true_L; rate_null, span_years); see ERRATA 2026-11-23"
for a_, K in (("R_rr1.25", "RrA"), ("R_rr1.5", "RrB"), ("R_rr2", "RrTwo"), ("R_rr3", "RrThree"), ("R_rr4", "RrFour")):
    put("dblStart" + K, calx[a_][2], csrc, a_ + " start doubling d"); put("dblEnd" + K, calx[a_][3], csrc, a_ + " end doubling d")
put("dblStartRrTwoOld", cal["R_rr2"][3], src, "superseded half-year secant, calendar table R_rr2"); put("dblEndRrTwoOld", cal["R_rr2"][4], src, "same, end")
put("dblStartRrFourOld", cal["R_rr4"][3], src, "superseded half-year secant, calendar table R_rr4"); put("dblEndRrFourOld", cal["R_rr4"][4], src, "same, end")
put("rrTwoOldRatio", "%.2f" % (float(cal["R_rr2"][3]) / float(cal["R_rr2"][4])), src, "ratio of the superseded secant doubling times, rr=2")
put("rrFourOldRatio", "%.2f" % (float(cal["R_rr4"][3]) / float(cal["R_rr4"][4])), src, "ratio of the superseded secant doubling times, rr=4")
write("table_cal.tex", ["%s & %s & %s & %s & %s \\\\" % (a_.replace("R_rr", "$rr=$").replace("R_logi_dec", "logistic, early").replace("R_logi_mid", "logistic, mid"), *calx[a_]) for a_ in cal])
# power
ALTS = ["R_rr1.25", "R_rr1.5", "R_rr2", "R_rr3", "R_rr4"]
write("table_power.tex", ["%s & %s & %s \\\\" % (SH[k], " & ".join(f(adj[(k, a_)][4], 1) for a_ in ALTS), f(rate(raw[(k, "R_rr2")][3]), 1)) for k in ["ccl", "mir", "audit", "heck", "sota", "ipw", "tcl", "rrate", "gap", "thr", "contr"]])
RALTS = ["R_rr0.5"] + ALTS + ["R_logi_dec", "R_logi_mid"]
def rawrows(ks): return ["%s & %s & %s & %s & %s \\\\" % (LBL[k] if a_ == "R_rr0.5" else "", a_.replace("R_rr", "$rr=$").replace("R_logi_dec", "logistic, early").replace("R_logi_mid", "logistic, mid"), *raw[(k, a_)][3:6]) for k in ks for a_ in RALTS]
write("table_rawpower_a.tex", rawrows(TESTS[:6])); write("table_rawpower_b.tex", rawrows(TESTS[6:]))
for k in ("audit", "heck", "sota", "rrate"): put("dec%s" % NAMES[k], f(rate(raw[(k, "R_logi_dec")][4]), 1), src, "raw power table %s R_logi_dec dn5" % k)
for k in TESTS:
    K = NAMES[k]
    put("pow%sTwo" % K, f(adj[(k, "R_rr2")][4], 1), src, "adjusted power table %s R_rr2" % k); put("pow%sThree" % K, f(adj[(k, "R_rr3")][4], 1), src, "adjusted power table %s R_rr3" % k)
    put("pow%sFour" % K, f(adj[(k, "R_rr4")][4], 1), src, "adjusted power table %s R_rr4" % k); put("rawpow%sTwo" % K, f(rate(raw[(k, "R_rr2")][3]), 1), src, "raw power table %s R_rr2 up5" % k)
mx2 = max(float(adj[(k, "R_rr2")][4]) for k in TESTS); mx3 = max(float(adj[(k, "R_rr3")][4]) for k in TESTS); mx4 = max(float(adj[(k, "R_rr4")][4]) for k in TESTS)
put("powMaxTwo", f(mx2, 1), src, "max adjusted power over 11 methods at R_rr2"); put("powMaxThree", f(mx3, 1), src, "same at R_rr3"); put("powMaxFour", f(mx4, 1), src, "same at R_rr4")
assert mx2 <= 28.0 and mx4 < 80
put("powCap", "28", src, "ceiling of max adjusted power at R_rr2 (%.1f), asserted <= 28" % mx2)
auc = re.search(r"AUC\(.*?\) = ([0-9.]+), bootstrap 95% \[([0-9.]+), ([0-9.]+)\]", A)
put("loroAuc", f(auc.group(1), 2), src, "D5 AUC"); put("loroAucLo", f(auc.group(2), 2), src, "D5 AUC lo"); put("loroAucHi", f(auc.group(3), 2), src, "D5 AUC hi")
CP = os.path.join(F, "design", "results_a3", "counts_a3.csv"); C = list(csv.DictReader(open(CP)))
tot = sum(int(x["completed"]) for x in C if x["test"] == "sota")
put("aThreeReps", commas(tot), rel(CP), "sum of completed over cells (rows of test sota)"); assert tot == 270000
put("aThreeCells", len({x["cell"] for x in C}), rel(CP), "distinct cells")
MF = json.load(open(os.path.join(F, "design", "results_a3", "manifest.json"))); put("preregAThree", "\\texttt{%s}" % MF["prereg_commit"], "design/results_a3/manifest.json", "prereg_commit")
_TRI = (18, 117, 33, 72)  # hand-classification counts (testable / needs new code / duplicate / vague) of the 240 candidates behind Amendment 3, see plans/04
_TS = "plans/04_amendment3_03dfe34.md (classification counts, constants in make_numbers.py)"
for K, v in zip(("triA", "triB", "triC", "triD"), _TRI): put(K, str(v), _TS, "counts")
put("triN", sum(_TRI), _TS, "sum of counts")

# ------------------------------------------------------------------ base design grid (exploratory)
BP = os.path.join(F, "design", "summary_base", "summary.json"); B = json.load(open(BP)); src = rel(BP)
def b(cell, test, key="rej2"): return 100 * B[cell]["tests"][test][key]
for tst, K in (("mb_sota", "MbSota"), ("mb_all", "MbAll"), ("pb_sota", "PbSota"), ("iid_all", "IidAll"), ("hb_all", "HbAll"), ("iid_sota", "IidSota"), ("hb_sota", "HbSota"), ("xb_all", "XbAll"), ("xb_sota", "XbSota")):
    put("base" + K, f(b("A_null_exp", tst), 1), src, "A_null_exp.tests.%s.rej2" % tst)
    put("base" + K + "Half", f(b("A_null_n0.5", tst), 1), src, "A_null_n0.5.tests.%s.rej2" % tst); put("base" + K + "Quarter", f(b("A_null_n0.25", tst), 1), src, "A_null_n0.25.tests.%s.rej2" % tst)
put("baseN", commas(B["A_null_exp"]["n"]), src, "A_null_exp.n"); put("baseMeanRecords", f(B["A_null_exp"]["mean_nS"], 1), src, "A_null_exp.mean_nS")
put("baseMbSotaEven", f(b("D_null_even", "mb_sota"), 1), src, "D_null_even.tests.mb_sota.rej2")
put("baseIidAllPowTwo", f(b("A_sup_rr2", "iid_all", "adj_power_2"), 0), src, "A_sup_rr2.tests.iid_all.adj_power_2"); put("baseIidAllRawTwo", f(b("A_sup_rr2", "iid_all"), 1), src, "A_sup_rr2.tests.iid_all.rej2")
put("baseNNoise", commas(B["A_null_n0.5"]["n"]), src, "A_null_n0.5.n"); assert B["A_null_n0.25"]["n"] == B["A_null_n0.5"]["n"]; put("baseNEven", commas(B["D_null_even"]["n"]), src, "D_null_even.n")
bt = ["mb_sota", "mb_all", "pb_sota", "iid_all", "iid_sota", "hb_all", "hb_sota", "xb_all", "xb_sota"]
bl = dict(mb_sota="model bootstrap, records", mb_all="model bootstrap, all models", pb_sota="parametric bootstrap, records", iid_all="OLS $F$ test, all models", iid_sota="OLS $F$ test, records",
          hb_all="task-hierarchical bootstrap, all", hb_sota="task-hierarchical bootstrap, records", xb_all="crossed bootstrap, all", xb_sota="crossed bootstrap, records")
write("table_base.tex", ["%s & %s [%s, %s] & %s & %s & %s \\\\" % (bl[k], f(b("A_null_exp", k), 1), f(100 * B["A_null_exp"]["tests"][k]["cp2"][0], 1), f(100 * B["A_null_exp"]["tests"][k]["cp2"][1], 1),
                                                                 f(b("A_null_n0.5", k), 1), f(b("A_null_n0.25", k), 1), f(b("D_null_even", k), 1)) for k in bt])

# ------------------------------------------------------------------ Gaussian illustration made for Fig. 1
IP = os.path.join(HERE, "bias_illustration.json"); I = json.load(open(IP)); src = rel(IP)
row = [x for x in I["rows"] if abs(x["sigma"] - V["params"]["sigma_m"]) < 1e-9][0]
put("illBias", f(row["mean_beta2_sota"], 3), src, "row sigma = sigma_m, mean_beta2_sota"); put("illRr", f(row["rr_eq_sota"], 2), src, "same row rr_eq_sota")
put("illRecords", f(row["mean_records"], 1), src, "same row mean_records"); put("illReps", commas(I["reps"]), src, "reps")

# ------------------------------------------------------------------ holdout (already seen; descriptive) and idea U (underpowered backtest)
HP = os.path.join(F, "results", "F_holdout.json"); H = json.load(open(HP)); src = rel(HP)
put("holdN", len(H["holdout"]), src, "len(holdout)"); put("holdInside", sum(1 for x in H["holdout"] if not x["above_upper_pi"] and not x["below_lower_pi"]), src, "holdout inside pi95")
put("holdAbove", sum(1 for x in H["holdout"] if x["observed_minus_linear"] > 0), src, "holdout observed above the linear forecast")
put("holdHbLo", sgn(H["hb_pre_cutoff_v1_1"]["lo"], 2), src, "hb_pre_cutoff_v1_1.lo"); put("holdHbHi", sgn(H["hb_pre_cutoff_v1_1"]["hi"], 2), src, "hb_pre_cutoff_v1_1.hi")
UP = os.path.join(U, "results", "U_summary.csv"); us = {(x["method"], x["level"], x["h"]): x for x in csv.DictReader(open(UP))}; src = rel(UP)
x = us[("M0", "0.95", "1.0")]; put("uInside", x["met_inside"], src, "M0 0.95 h=1.0 met_inside"); put("uN", x["n"], src, "n"); put("uCov", f(100 * float(x["cov"]), 1), src, "cov")
put("uCbLo", f(100 * float(x["cb90_lo"]), 0), src, "cb90_lo"); put("uCbHi", f(100 * float(x["cb90_hi"]), 0), src, "cb90_hi"); put("uSeries", x["n_series"], src, "n_series")
x = us[("M0", "0.8", "1.0")]; put("uInsideEighty", x["met_inside"], src, "M0 0.8 h=1.0 met_inside"); put("uCovEighty", f(100 * float(x["cov"]), 0), src, "cov")
UQ = os.path.join(U, "results", "U_per_series.csv"); up = {(x["series"], x["method"], x["level"], x["h"]): x for x in csv.DictReader(open(UQ))}
x = up[("metr", "M0", "0.95", "1.0")]; put("uMetrInside", x["inside"], rel(UQ), "metr M0 0.95 h=1.0 inside"); put("uMetrN", x["n"], rel(UQ), "n")

# post hoc sensitivity (NOT pre-registered): the same Holm family with the wild-bootstrap p in place of the HC3 t p
pw = dict(pu, hc3=g["wild_pup"]); o2 = sorted(fam, key=lambda k: pw[k]); run = 0.0
for i, k in enumerate(o2):
    run = max(run, min(1.0, (len(fam) - i) * pw[k]))
    if k == "hc3": put("holmWild", pv(run), rel(RP), "Holm step-down with reg.wild_pup replacing reg.hc3_pup (post hoc, computed here)")
UR = os.path.join(U, "RESULTS.md"); put("uGap", re.search(r"detects only a (\d+)-point gap", open(UR).read()).group(1), rel(UR), "pre-registered power statement")
put("auditDrawAbove", "above" if p["audit_c"] > a["q75"] else "below", rel(RP), "pb.audit_c compared with audit_draws.q75"); assert p["audit_c"] > a["q75"]
# ------------------------------------------------------------------ v2 additions, all EXPLORATORY and not pre-registered
TP = os.path.join(F, "design", "results_a3", "typem_exploratory.json"); TM = json.load(open(TP)); src = rel(TP)
assert abs(TM["rate"] - RATE0) < 1e-12 and abs(TM["span"] - SPAN0) < 1e-12
for nm, K in (("R_rr1.5", "B"), ("R_rr2", "Two"), ("R_rr3", "Three"), ("R_rr4", "Four")):
    c_ = TM["cells"][nm]; assert c_["n"] == 10000
    put("typeMAudit" + K, f(c_["tests"]["audit"]["exaggeration_own"], 1), src, "cells.%s.tests.audit.exaggeration_own" % nm)
    put("typeMAll" + K, f(c_["tests"]["audit"]["exaggeration_c_all"], 1), src, "cells.%s.tests.audit.exaggeration_c_all" % nm)
    put("typeMSota" + K, f(c_["tests"]["sota"]["exaggeration_own"], 1), src, "cells.%s.tests.sota.exaggeration_own" % nm)
    put("typeMHeck" + K, f(c_["tests"]["heck"]["exaggeration_own"], 1), src, "cells.%s.tests.heck.exaggeration_own" % nm)
c_ = TM["cells"]["R_rr2"]; put("trueBetaTwo", f(c_["true_beta2"], 3), src, "cells.R_rr2.true_beta2")
put("typeMAllGivenTwo", sgn(c_["tests"]["audit"]["mean_c_all_given_reject"], 3), src, "cells.R_rr2.tests.audit.mean_c_all_given_reject")
put("typeMAuditGivenTwo", sgn(c_["tests"]["audit"]["mean_est_given_reject"], 3), src, "cells.R_rr2.tests.audit.mean_est_given_reject")
c_ = TM["cells"]["R_null_val"]; put("typeMAllGivenNull", sgn(c_["tests"]["audit"]["mean_c_all_given_reject"], 3), src, "cells.R_null_val.tests.audit.mean_c_all_given_reject")
put("typeMAuditGivenNull", sgn(c_["tests"]["audit"]["mean_est_given_reject"], 3), src, "cells.R_null_val.tests.audit.mean_est_given_reject")
write("table_typem.tex", ["$rr=$%s & %.3f & %s & %s & %s & %s \\\\" % (nm[4:], TM["cells"][nm]["true_beta2"], *[f(TM["cells"][nm]["tests"][t_][k_], 1) for t_, k_ in (("audit", "exaggeration_own"), ("audit", "exaggeration_c_all"), ("heck", "exaggeration_own"), ("sota", "exaggeration_own"))])
                          for nm in ("R_rr1.25", "R_rr1.5", "R_rr2", "R_rr3", "R_rr4")])
SNP = os.path.join(HERE, "sensitivity_exploratory.json"); SN = json.load(open(SNP)); src = rel(SNP)
assert abs(SN["full"]["beta2"] - g["reg_c"]) < 1e-9 and abs(SN["full"]["hc3_pup"] - g["hc3_pup"]) < 1e-9
L_ = SN["loo_summary"]; put("looMin", sgn(L_["beta2_min"], 3), src, "loo_summary.beta2_min"); put("looMax", sgn(L_["beta2_max"], 3), src, "loo_summary.beta2_max")
put("looPmax", pv(L_["hc3_pup_max"]), src, "loo_summary.hc3_pup_max"); put("looNsig", L_["n_hc3_pup_below_05"], src, "loo_summary.n_hc3_pup_below_05")
lo = {r_["dropped"]: r_ for r_ in SN["leave_one_out"]}; assert L_["dropped_at_pmax"] == "davinci-002 (GPT-3)" and sorted(r_["dropped"] for r_ in SN["leave_one_out"] if r_["hc3_pup"] >= 0.05) == ["GPT-2", "davinci-002 (GPT-3)"]
put("looPGptTwo", pv(lo["GPT-2"]["hc3_pup"]), src, "leave_one_out[GPT-2].hc3_pup"); put("looBGptTwo", sgn(lo["GPT-2"]["beta2"], 3), src, "leave_one_out[GPT-2].beta2")
put("looPGptThree", pv(lo["davinci-002 (GPT-3)"]["hc3_pup"]), src, "leave_one_out[davinci-002 (GPT-3)].hc3_pup"); put("looBGptThree", sgn(lo["davinci-002 (GPT-3)"]["beta2"], 3), src, "leave_one_out[davinci-002 (GPT-3)].beta2")
assert SN["n_pre2023"] == 3 and SN["drops"]["first_two"]["dropped"] == ["GPT-2", "davinci-002 (GPT-3)"]
for key, K in (("pre2023", "PreTwentyThree"), ("first_two", "FirstTwo")):
    x_ = SN["drops"][key]; put("drop%sN" % K, x_["n"], src, "drops.%s.n" % key); put("drop%sBeta" % K, sgn(x_["beta2"], 3), src, "drops.%s.beta2" % key)
    put("drop%sP" % K, pv(x_["hc3_pup"]), src, "drops.%s.hc3_pup" % key); put("drop%sWild" % K, pv(x_["wild_pup"]), src, "drops.%s.wild_pup" % key)
am = SN["audit_many"]; put("auditManyN", commas(am["n"]), src, "audit_many.n"); put("auditManyMean", sgn(am["mean"], 3), src, "audit_many.mean"); put("auditManyMed", sgn(am["median"], 3), src, "audit_many.median")
put("auditManyQlo", f(am["q25"], 3), src, "audit_many.q25"); put("auditManyQhi", f(am["q75"], 3), src, "audit_many.q75"); put("auditManyShare", f(100 * am["share_below_registered"], 0), src, "100 * audit_many.share_below_registered")
SCP = os.path.join(HERE, "schedule_illustration.json"); SC = json.load(open(SCP)); src = rel(SCP)
assert abs(SC["rows"]["real"]["rr_eq_sota"] - row["rr_eq_sota"]) < 0.03   # agrees with the Fig. 2(a) illustration at the calibrated noise (different seed)
for key, K in (("real", "Real"), ("even", "Even"), ("reflected", "Refl")):
    put("sched%sRr" % K, f(SC["rows"][key]["rr_eq_sota"], 2), src, "rows.%s.rr_eq_sota" % key); put("sched%sBeta" % K, sgn(SC["rows"][key]["mean_beta2_sota"], 3), src, "rows.%s.mean_beta2_sota" % key)
put("pvMin", pv(min(g["ols_pup"], g["hc3_pup"], g["wild_pup"], g["perm_pup"])), rel(RP), "min of reg.{ols,hc3,wild,perm}_pup"); put("pvMax", pv(max(g["ols_pup"], g["hc3_pup"], g["wild_pup"], g["perm_pup"])), rel(RP), "max of the same")
# ------------------------------------------------------------------ v3: Design Amendment 2 (pre-registered exploratory, synthetic; complete)
A2P = os.path.join(F, "design", "results_a2", "summary_a2.md"); A2 = open(A2P).read(); src = rel(A2P)
M2 = json.load(open(os.path.join(F, "design", "results_a2", "manifest.json"))); assert M2["runs_sha_ok"] is True and M2["smoke"] is False
C2 = list(csv.DictReader(open(os.path.join(F, "design", "results_a2", "counts_a2.csv")))); assert all(x["planned"] == x["completed"] for x in C2)
put("preregATwo", "\\texttt{%s}" % M2["prereg_commit"], "design/results_a2/manifest.json", "prereg_commit")
def tab2(start):
    i = A2.index(start); rows = []
    for ln in A2[i:].split("\n")[1:]:
        if not ln.startswith("|"):
            if rows: break
            continue
        cells = [x.strip() for x in ln.strip().strip("|").split("|")]
        if set(cells[0]) <= set("-: "): continue
        rows.append(cells)
    return rows[0], rows[1:]
def sizetab(start):
    h, rows = tab2(start); return {(r[0], h[j]): re.sub(r" \(B.*", "", r[j]) for r in rows for j in range(2, len(h))}
s2 = dict(up=sizetab("## Null size, primary and validation cells: upward"), two=sizetab("## Null size, primary and validation cells: two-sided"), dn=sizetab("## Null size, primary and validation cells: downward"))
def verd(s): return s.split("] ")[1]
def cpi2(s): return s.split("[")[1].split("]")[0].split(",")
T2 = ["ols", "hc3", "wild", "perm", "mb_all", "mb_sota", "pb_sota"]
L2 = dict(ols="OLS $t$, all models", hc3="HC3 $t$, all models", wild="wild bootstrap, all models", perm="residual permutation, all models", mb_all="model bootstrap, all models", mb_sota="model bootstrap, records", pb_sota="parametric bootstrap, records")
N2 = dict(ols="Ols", hc3="Hc", wild="Wild", perm="Perm", mb_all="MbAll", mb_sota="MbSota", pb_sota="PbSota")
F2 = ["R", "E", "K0", "K2", "K4", "N50", "N25", "MF1", "MF2"]
for k in T2:
    for rule, RK in (("up", "Up"), ("two", "Two")):
        x = s2[rule][("R_null_val", k)]; put("aTwo%s%s" % (N2[k], RK), f(rate(x), 1), src, "size table (%s) R_null_val %s" % (rule, k))
for k in ("hc3", "wild"):
    x = s2["up"][("R_null_val", k)]; put("aTwo%sUpLo" % N2[k], f(cpi2(x)[0], 1), src, "CP lo"); put("aTwo%sUpHi" % N2[k], f(cpi2(x)[1], 1), src, "CP hi")
    for fm in ("E", "K4", "N50", "N25"):
        put("aTwo%sUp%s" % (N2[k], dict(E="E", K4="Kfour", N50="Nhalf", N25="Nquarter")[fm]), f(rate(s2["up"][(fm + "_null_val", k)]), 1), src, "size table (up) %s_null_val %s" % (fm, k))
        put("aTwo%sTwo%s" % (N2[k], dict(E="E", K4="Kfour", N50="Nhalf", N25="Nquarter")[fm]), f(rate(s2["two"][(fm + "_null_val", k)]), 1), src, "size table (two) %s_null_val %s" % (fm, k))
    put("aTwo%sDnKfour" % N2[k], f(rate(s2["dn"][("K4_null_val", k)]), 1), src, "size table (dn) K4_null_val %s" % k)
    okf = [fm for fm in F2 if verd(s2["up"][(fm + "_null_val", k)]) == "OK" and verd(s2["two"][(fm + "_null_val", k)]) == "OK"]
    outf = [fm for fm in F2 if verd(s2["up"][(fm + "_null_val", k)]) == "OUT" and verd(s2["two"][(fm + "_null_val", k)]) == "OUT"]
    assert okf == ["R", "K0", "K2", "MF1", "MF2"] and outf == ["E", "K4", "N50", "N25"], (k, okf, outf)   # the scope statement in the text
assert verd(s2["up"][("R_null_val", "ols")]) == "OUT" and verd(s2["two"][("R_null_val", "ols")]) == "OUT" and verd(s2["two"][("R_null_val", "perm")]) == "OUT" and verd(s2["up"][("R_null_val", "perm")]) == "inconclusive"
assert verd(s2["up"][("R_null_val", "mb_all")]) == "OK" and verd(s2["two"][("R_null_val", "mb_all")]) == "OK"
for rule, RK in (("up", "Up"), ("two", "Two"), ("dn", "Dn")):   # v5: two decimals, so that the tails of the record bootstrap are quoted exactly as in SM Table S7
    put("aTwoMbSota%sX" % RK, f(rate(s2[rule][("R_null_val", "mb_sota")]), 2), src, "size table (%s) R_null_val mb_sota, two decimals" % rule)
assert verd(s2["up"][("R_null_val", "mb_sota")]) == "OUT" and verd(s2["two"][("R_null_val", "mb_sota")]) == "OK"
def cell2(x, ci=False): return ("%s [%s, %s]%s" % (f(rate(x), 1), f(cpi2(x)[0], 1), f(cpi2(x)[1], 1), mark(verd(x)))) if ci else "%s%s" % (f(rate(x), 1), mark(verd(x)))
write("table_a2size.tex", ["%s & %s & %s & %s \\\\" % (L2[k].replace(", all models", ""), cell2(s2["up"][("R_null_val", k)], True), cell2(s2["two"][("R_null_val", k)]),
                                                     " & ".join(cell2(s2["up"][(fm + "_null_val", k)]) for fm in F2[1:])) for k in ("ols", "perm", "hc3", "wild", "mb_all")])
L2S = dict(ols="OLS $t$", hc3="HC3 $t$", wild="wild boot.", perm="permutation", mb_all="model boot., all", mb_sota="model boot., rec.", pb_sota="param. boot., rec.")
write("table_a2sizefull.tex", ["%s & %s & %s & %s & %s & %s \\\\" % (L2S[k] if fm == "R" else "", fm, r1_(s2["up"][(fm + "_null_val", k)].rsplit(" ", 1)[0]), r1_(nc_(s2["two"][(fm + "_null_val", k)].rsplit(" ", 1)[0])), r1_(nc_(s2["dn"][(fm + "_null_val", k)].rsplit(" ", 1)[0])),
                                                                          vc_(verd(s2["up"][(fm + "_null_val", k)]), verd(s2["two"][(fm + "_null_val", k)]))) for k in T2 for fm in F2] + ["\\hline\\hline"])
# power (P2)
h2, pr = tab2("### ACCELERATION power"); pw2 = {(r[0], h2[j]): r[j] for r in pr for j in range(2, len(h2))}
def padj(s): return float(s.split("/")[1].split("[")[0])
def praw(s): return float(s.split("/")[0])
for k in ("ols", "hc3", "wild", "perm", "mb_all"):
    for a_, K in (("R_rr1.25", "A"), ("R_rr1.5", "B"), ("R_rr2", "Two"), ("R_rr3", "Three"), ("R_rr4", "Four")):
        put("aTwoPow%s%s" % (N2[k], K), f(padj(pw2[(a_, k)]), 1), src, "acceleration power table %s %s adjusted" % (a_, k))
    put("aTwoRaw%sTwo" % N2[k], f(praw(pw2[("R_rr2", k)]), 1), src, "acceleration power table R_rr2 %s raw" % k)
x = pw2[("R_rr2", "hc3")]; put("aTwoPowHcTwoLo", f(cpi2(x)[0], 1), src, "R_rr2 hc3 adjusted interval lo"); put("aTwoPowHcTwoHi", f(cpi2(x)[1], 1), src, "hi")
x = pw2[("R_rr2", "wild")]; put("aTwoPowWildTwoLo", f(cpi2(x)[0], 1), src, "R_rr2 wild adjusted interval lo"); put("aTwoPowWildTwoHi", f(cpi2(x)[1], 1), src, "hi")
assert padj(pw2[("R_rr2", "hc3")]) == padj(pw2[("R_rr2", "wild")]) and padj(pw2[("R_rr2", "ols")]) == padj(pw2[("R_rr2", "perm")])   # same statistic, same adjusted power
assert all(padj(pw2[("R_rr2", k)]) < 80 for k in T2) and padj(pw2[("R_rr4", "hc3")]) < 80 and padj(pw2[("R_rr4", "ols")]) > 80 and padj(pw2[("R_rr3", "ols")]) < 80
put("aTwoPowHcTwoRound", f(padj(pw2[("R_rr2", "hc3")]), 0), src, "R_rr2 hc3 adjusted, rounded")
hv, vr = tab2("## Validation: achieved size"); val2 = {(r[0], r[1]): r for r in vr}
put("aTwoValHc", f(rate(val2[("R", "hc3")][4]), 1), src, "validation table R hc3 up5 achieved"); put("aTwoValOls", f(rate(val2[("R", "ols")][4]), 1), src, "validation table R ols up5 achieved")
hp, pp = tab2("## Paired Monte Carlo differences"); pd2 = {(r[0], r[1]): r[2] for r in pp}
put("aTwoPairWildHc", pd2[("R_rr2", "wild - hc3")].split()[0].replace("-", "$-$"), src, "paired table R_rr2 wild - hc3 (pp)")
with open(os.path.join(HERE, "table_power.tex"), "a") as fh:
    fh.write("\\hline\n\\multicolumn{7}{l}{\\emph{All-model regression (Amendment 2)}} \\\\\n" + "\n".join("%s & %s & %s \\\\" % (lb, " & ".join(f(padj(pw2[(a_, k)]), 1) for a_ in ALTS), f(praw(pw2[("R_rr2", k)]), 1))
              for k, lb in (("ols", "OLS $t$"), ("perm", "OLS, permutation $p$"), ("hc3", "HC3 $t$"), ("wild", "HC3, wild bootstrap $p$"), ("mb_all", "model boot., all"))) + "\n")
# ladder (P3)
hc_, cr = tab2("| cell | n | mean beta2 all (SE) |"); cur2 = {r[0]: r for r in cr}
lu = sizetab("## Ladder rungs (null): upward"); RUNGS = ["LAD0_gauss", "LAD1_estimation", "LAD2_censoring", "LAD3_taskdep", "LAD4_modfam"]
RL = dict(LAD0_gauss="0: Gaussian horizons", LAD1_estimation="1: + horizon estimation", LAD2_censoring="2: + suite ceiling", LAD3_taskdep="3: + shared task jitter", LAD4_modfam="4: + model-by-family")
def mse(s): m_ = re.fullmatch(r"([+-][0-9.]+) \(([0-9.]+)\)", s); return float(m_.group(1)), float(m_.group(2))
first = [r_ for r_ in RUNGS if abs(mse(cur2[r_][2])[0]) > 2 * mse(cur2[r_][2])[1]][0]; assert first == "LAD1_estimation" and re.search(r"First rung.*\*\*LAD1_estimation\*\*", open(os.path.join(F, "RESULTS_A2.md")).read())
for r_, K in (("LAD0_gauss", "Zero"), ("LAD1_estimation", "One")):
    put("lad%sAll" % K, sgn(mse(cur2[r_][2])[0], 4), src, "curvature table %s mean beta2 all" % r_); put("lad%sSe" % K, f(mse(cur2[r_][2])[1], 4), src, "same, SE")
    put("lad%sRecRr" % K, f(cur2[r_][5], 2), src, "curvature table %s rr_eq SOTA" % r_)
rrs = [float(cur2[r_][5]) for r_ in RUNGS]; put("ladRecRrMin", f(min(rrs), 2), src, "min rr_eq SOTA over ladder rungs"); put("ladRecRrMax", f(max(rrs), 2), src, "max of the same")
alls = [mse(cur2[r_][2])[0] for r_ in RUNGS]; put("ladAllMin", sgn(min(alls), 4), src, "min mean beta2 all over ladder rungs"); put("ladAllMax", sgn(max(alls), 4), src, "max of the same")
for k, K in (("hc3", "Hc"), ("ols", "Ols"), ("mb_sota", "MbSota")):
    v_ = [rate(lu[(r_, k)]) for r_ in RUNGS]; put("lad%sMin" % K, f(min(v_), 1), src, "ladder upward size %s min over rungs" % k); put("lad%sMax" % K, f(max(v_), 1), src, "max")
lt = sizetab("## Ladder rungs (null): two-sided")
assert [verd(lt[(r_, "ols")]) for r_ in RUNGS] == ["OK", "OK", "OK", "OUT", "OUT"] and all(verd(lu[(r_, "ols")]) == "OK" for r_ in RUNGS)
put("ladOlsTwoBefore", f(rate(lt[("LAD2_censoring", "ols")]), 1), src, "ladder two-sided size ols LAD2_censoring"); put("ladOlsTwoAfter", f(rate(lt[("LAD3_taskdep", "ols")]), 1), src, "ladder two-sided size ols LAD3_taskdep")
put("aTwoKfourAll", sgn(mse(cur2["K4_null_val"][2])[0], 3), src, "curvature table K4_null_val mean beta2 all"); put("aTwoKfourCeil", f(100 * float(cur2["K4_null_val"][7]), 0), src, "K4_null_val frac of models at ceiling, %")
put("aTwoRAll", sgn(mse(cur2["R_null_val"][2])[0], 4), src, "curvature table R_null_val mean beta2 all"); put("aTwoRAllSe", f(mse(cur2["R_null_val"][2])[1], 4), src, "same, SE")
write("table_ladder.tex", ["%s & %s & %s & %s & %s & %s & %s & %s \\\\" % (RL[r_], sgn(mse(cur2[r_][2])[0], 4), f(mse(cur2[r_][2])[1], 4), sgn(mse(cur2[r_][4])[0], 4), f(cur2[r_][5], 2),
                           cell2(lu[(r_, "ols")]), cell2(lu[(r_, "hc3")]), cell2(lu[(r_, "mb_sota")])) for r_ in RUNGS])
tot2 = sum(int(x["completed"]) for x in C2 if x["test"] == "ols"); put("aTwoReps", commas(tot2), "design/results_a2/counts_a2.csv", "sum of completed over cells (rows of test ols)")
# ------------------------------------------------------------------ v3: developer-clustered tests on the real series (Amendment CL1, pre-registered exploratory)
KP = os.path.join(F, "real_data", "out", "cluster_v10.json"); KL = json.load(open(KP)); src = rel(KP)
RSHA = __import__("hashlib").sha256(open(RP, "rb").read()).hexdigest(); assert KL["source_sha256"] == RSHA, "cluster test was not run on the stored real_v10.json"
kf, kd = KL["full"], KL["drop_gpt2_gpt3"]; assert abs(kf["beta2"] - g["reg_c"]) < 1e-9 and abs(kf["hc3_p_up_t(n-3)"] - g["hc3_pup"]) < 1e-9 and kf["n"] == R["M"]
assert abs(kd["beta2"] - SN["drops"]["first_two"]["beta2"]) < 1e-9 and abs(kd["hc3_p_up_t(n-3)"] - SN["drops"]["first_two"]["hc3_pup"]) < 1e-9
put("clG", kf["G"], src, "full.G"); put("clMax", max(kf["cluster_sizes"].values()), src, "max cluster size"); put("clSingles", sum(1 for v_ in kf["cluster_sizes"].values() if v_ == 1), src, "clusters of one model")
assert max(kf["cluster_sizes"], key=kf["cluster_sizes"].get) == "OpenAI" and kf["cluster_sizes"]["Anthropic"] == 9
def p3(x): return "%.3f" % float(x)
put("clSecond", kf["cluster_sizes"]["Anthropic"], src, "cluster_sizes.Anthropic")
for d_, K in ((kf, ""), (kd, "Drop")):
    put("clT" + K, f(d_["cr2_t"], 2), src, "cr2_t"); put("clDf" + K, f(d_["cr2_df"], 1), src, "cr2_df"); put("clP" + K, p3(d_["cr2_p_up"]), src, "cr2_p_up"); put("clPtwo" + K, p3(d_["cr2_p_two"]), src, "cr2_p_two")
    put("clWebb" + K, p3(d_["webb"]["p_up"]), src, "webb.p_up"); put("clWebbTwo" + K, p3(d_["webb"]["p_two"]), src, "webb.p_two"); put("clRad" + K, p3(d_["rademacher_exact"]["p_up"]), src, "rademacher_exact.p_up")
put("clWebbB", commas(kf["webb"]["B"]), src, "full.webb.B"); put("clRadN", kf["rademacher_exact"]["patterns"], src, "full.rademacher_exact.patterns"); put("clNullQ", f(kf["webb"]["null_t_q95"], 2), src, "full.webb.null_t_q95")
assert min(kf["cr2_p_up"], kf["webb"]["p_up"], kf["rademacher_exact"]["p_up"], kd["cr2_p_up"], kd["webb"]["p_up"], kd["rademacher_exact"]["p_up"]) > 0.05   # "does not survive clustering"
write("table_cluster.tex", ["%s & %s & %s & %s & %s & %s \\\\" % (lb, sgn(d_["beta2"], 3), pv(d_["hc3_p_up_t(n-3)"]), p3(d_["cr2_p_up"]), p3(d_["webb"]["p_up"]), p3(d_["rademacher_exact"]["p_up"]))
                            for lb, d_ in (("All %d" % kf["n"], kf), ("No GPT-2, GPT-3" , kd))])
# ------------------------------------------------------------------ v3: closed form for the schedule-induced curvature (Amendment CF1, confirmatory on simulated data; FAILED its bar)
FP = os.path.join(F, "design", "cf1_out.json"); CF = json.load(open(FP)); src = rel(FP)
assert CF["bar_met"] is False and CF["n_pass"] == 2 and CF["n_sign"] == 7 and len(CF["rows"]) == 8
put("cfPass", CF["n_pass"], src, "n_pass"); put("cfSign", CF["n_sign"], src, "n_sign"); put("cfN", len(CF["rows"]), src, "len(rows)"); put("cfReps", commas(CF["reps"]), src, "reps")
for key, K in (("real", "Real"), ("even", "Even"), ("reflected", "Refl")):
    x = CF["rows"][key]; assert x["sign_ok"]; put("cf%s" % K, sgn(x["cf"], 3), src, "rows.%s.cf" % key); put("cf%sSim" % K, sgn(x["sim"], 3), src, "rows.%s.sim" % key); put("cf%sErr" % K, f(100 * abs(x["rel_err"]), 0), src, "100*|rows.%s.rel_err|" % key)
assert CF["rows"]["real"]["cf"] > 0 > CF["rows"]["even"]["cf"] and CF["rows"]["reflected"]["cf"] < 0 and CF["rows"]["real"]["pass_"] and not CF["rows"]["bursty"]["sign_ok"] and CF["rows"]["bursty"]["pass_"]
assert all(CF["rows"][k_]["sim"] < 0 and abs(CF["rows"][k_]["cf"]) > abs(CF["rows"][k_]["sim"]) for k_ in CF["rows"] if k_ not in ("real", "bursty"))   # "overstates the negative curvature"
put("cfRecErr", f(100 * max(abs(x["cf_mean_records"] / x["sim_mean_records"] - 1) for x in CF["rows"].values()), 2), src, "max over schedules of 100*|cf_mean_records/sim_mean_records - 1|")
ne = [100 * abs(x["rel_err"]) for k_, x in CF["rows"].items() if k_ not in ("real", "bursty")]; put("cfErrMin", f(min(ne), 0), src, "min 100*|rel_err| over the six failing schedules"); put("cfErrMax", f(max(ne), 0), src, "max of the same")
cneg = [k_ for k_, x in CF["rows"].items() if x["sim"] < -2 * x["se"]]; cpos = [k_ for k_, x in CF["rows"].items() if x["sim"] > 2 * x["se"]]   # v5: sign count of the SIMULATED means (Table S13)
assert len(cneg) == 6 and cpos == ["real"] and set(CF["rows"]) - set(cneg) - set(cpos) == {"bursty"} and {"even", "reflected", "late_g0_5", "late_g0_75"} <= set(cneg)
_q = lambda b: (lambda q: (1 + q) / (1 - q))(b * SC["span_years"] / SC["rate"])   # same conversion as rr_eq_sota in make_schedule_illustration.py
for key, K in (("real", "Real"), ("even", "Even"), ("reflected", "Refl")): put("cf%sRr" % K, f(_q(CF["rows"][key]["sim"]), 2), src, "rr_eq of rows.%s.sim (Table S15 run, not the schedule illustration)" % key)
put("cfNeg", len(cneg), src, "schedules with simulated mean more than 2 SE below zero"); put("cfOther", len(CF["rows"]) - 1, src, "schedules other than the real one")
CL_ = dict(real="real dates", even="even", reflected="real, reflected", late_g0_5="smooth, late-dense ($u^{0.5}$)", late_g0_75="smooth, late-dense ($u^{0.75}$)", early_g1_5="smooth, early-dense ($u^{1.5}$)", early_g2="smooth, early-dense ($u^{2}$)", bursty="three bursts")
assert list(CF["rows"]) == list(CL_)
write("table_cf.tex", ["%s & %s & %s & %s & %s & %s & %s \\\\" % (CL_[k_], sgn(x["cf"], 4 if k_ != "bursty" else 6), sgn(x["sim"], 4), f(x["se"], 4), ("%+.0f\\%%" % (100 * x["rel_err"])).replace("-", "$-$") if k_ != "bursty" else "n/a", "yes" if x["pass_"] else "no", "yes" if x["sign_ok"] else "no")
                       for k_, x in CF["rows"].items()])
# ------------------------------------------------------------------ v4: size study of the developer-clustered tests (Amendment CS1, pre-registered exploratory, synthetic data)
SP = os.path.join(F, "real_data", "out", "cluster_size_v1.json"); CS = json.load(open(SP)); src = rel(SP)
assert CS["amendment"] == "CS1" and CS["cluster_sizes"] == kf["cluster_sizes"] and list(CS["cells"]) == ["R_null_val", "MF1_null_val", "N50_null_val", "LAD0_gauss", "DEV_rho0.3", "DEV_rho0.6"]
assert all(c_["n"] == CS["reps"] for c_ in CS["cells"].values())
csv_ = lambda t_: [c_["tests"][t_]["verdict"] for c_ in CS["cells"].values()]
csr_ = lambda t_: [100 * c_["tests"][t_]["rate_up"] for c_ in CS["cells"].values()]
assert all(v_ in ("VALID", "INCONCLUSIVE", "CONSERVATIVE") for t_ in ("cr2", "webb", "rad") for v_ in csv_(t_))   # "never anti-conservative"
assert csv_("webb").count("VALID") == 5 and csv_("webb")[3] == "INCONCLUSIVE" and csv_("cr2").count("VALID") == 1 and csv_("cr2").count("CONSERVATIVE") == 3 and csv_("rad").count("VALID") == 4
assert csv_("cr2")[4] == csv_("cr2")[5] == "CONSERVATIVE" and csv_("webb")[4] == csv_("webb")[5] == "VALID"
put("csReps", commas(CS["reps"]), src, "reps"); put("csWebbB", CS["B_webb"], src, "B_webb"); put("csCells", len(CS["cells"]), src, "len(cells)")
put("csWebbValid", csv_("webb").count("VALID"), src, "cells with webb verdict VALID"); put("csCrValid", csv_("cr2").count("VALID"), src, "cells with cr2 verdict VALID"); put("csCrCons", csv_("cr2").count("CONSERVATIVE"), src, "cells with cr2 verdict CONSERVATIVE"); put("csRadValid", csv_("rad").count("VALID"), src, "cells with rad verdict VALID")
put("csWebbMin", f(min(csr_("webb")), 1), src, "min over cells of 100*webb.rate_up"); put("csWebbMax", f(max(csr_("webb")), 1), src, "max of the same")
put("csCrMin", f(min(csr_("cr2")), 1), src, "min over cells of 100*cr2.rate_up"); put("csCrMax", f(max(csr_("cr2")), 1), src, "max of the same")
put("csCrLowMax", f(sorted(csr_("cr2"))[-2], 1), src, "second-largest 100*cr2.rate_up (largest of the five cells other than N50)"); assert max(csr_("cr2")) == csr_("cr2")[2]
gw = CS["cells"]["LAD0_gauss"]["tests"]["webb"]; put("csWebbGauss", f(100 * gw["rate_up"], 1), src, "LAD0_gauss.webb.rate_up"); put("csWebbGaussLo", f(100 * gw["cp_up"][0], 1), src, "LAD0_gauss.webb.cp_up[0]"); put("csWebbGaussHi", f(100 * gw["cp_up"][1], 1), src, "LAD0_gauss.webb.cp_up[1]")
put("csWebbDevA", f(csr_("webb")[4], 1), src, "DEV_rho0.3.webb.rate_up"); put("csWebbDevB", f(csr_("webb")[5], 1), src, "DEV_rho0.6.webb.rate_up"); put("csCrDevA", f(csr_("cr2")[4], 1), src, "DEV_rho0.3.cr2.rate_up"); put("csCrDevB", f(csr_("cr2")[5], 1), src, "DEV_rho0.6.cr2.rate_up")
assert abs(CS["cr2_df"] - kf["cr2_df"]) < 1e-9
CSM = {"VALID": "", "INCONCLUSIVE": "$^{\\dagger}$", "CONSERVATIVE": "$^{\\S}$"}
CSL = {"R_null_val": "real design (R)", "MF1_null_val": "model-by-family interaction (MF1)", "N50_null_val": "model-level noise halved (N50)", "LAD0_gauss": "Gaussian horizons (ladder rung 0)", "DEV_rho0.3": "developer level shift, $\\rho=0.3$", "DEV_rho0.6": "developer level shift, $\\rho=0.6$"}
def cscell(x): return "%s [%s, %s]%s" % (f(100 * x["rate_up"], 1), f(100 * x["cp_up"][0], 1), f(100 * x["cp_up"][1], 1), CSM[x["verdict"]])
write("table_cssize.tex", ["%s & %s & %s & %s \\\\" % (CSL[k_], cscell(c_["tests"]["cr2"]), cscell(c_["tests"]["webb"]), cscell(c_["tests"]["rad"])) for k_, c_ in CS["cells"].items()])
# ------------------------------------------------------------------ v4: multi-benchmark planted-trend audit (confirmatory bars on real scores with permuted dates; bar 1 met, bars 2 and 3 failed, falsifier triggered)
AD = os.path.join(F, "multibench_audit", "results"); AS = json.load(open(os.path.join(AD, "audit_summary.json"))); AP = json.load(open(os.path.join(AD, "audit_per_series.json"))); AE = json.load(open(os.path.join(AD, "audit_series.json")))
src = rel(os.path.join(AD, "audit_summary.json")); srcp = rel(os.path.join(AD, "audit_per_series.json"))
ser = [x for x in AP if not x["ref"]]; ref_ = [x for x in AP if x["ref"]]; assert len(ser) == AS["n_series"] == len(AE["eligible"]) == 22 and len(ref_) == 1 and [x["file"] for x in ser] == [e_["file"] for e_ in AE["eligible"]]
over_ = lambda x, t_, cs_: any(x["%s_%s_size" % (t_, c_)] > 0.10 and x["%s_%s_cp" % (t_, c_)][0] > 0.07 for c_ in cs_)
nb1 = sum(over_(x, "iid", ("N0",)) for x in ser); nov = sum(over_(x, "mb", ("N0", "P1")) for x in ser)
nb2 = sum(all(x["mb_%s_cp" % c_][0] <= 0.07 and x["mb_%s_cp" % c_][1] >= 0.03 for c_ in ("N0", "P1")) for x in ser)
assert AS["bar1"] == {"met": nb1, "of": 22, "pass_": True} and AS["bar2"] == {"met": nb2, "of": 22, "pass_": False} and AS["bar3"]["pass_"] is False and AS["falsifier"]["triggered"] is True
assert abs(AS["falsifier"]["oversized_mb_frac"] - nov / 22) < 1e-9 and AS["checks"]["i_pass"] and AS["checks"]["ii_zero_plant_equals_N0"] and AS["ref_pass"] and AS["unmeasured_mb"] == 0
put("mbN", AS["n_series"], src, "n_series"); put("mbBarOne", nb1, src, "bar1.met (recomputed from audit_per_series.json)"); put("mbBarTwo", nb2, src, "bar2.met (recomputed)"); put("mbOver", nov, srcp, "series with mb size >10% and CP lower >7% on N0 or P1")
put("mbOverPct", f(100 * AS["falsifier"]["oversized_mb_frac"], 0), src, "100*falsifier.oversized_mb_frac"); put("mbMid", 22 - nb2 - nov, srcp, "series neither meeting bar 2 nor oversized"); assert 22 - nb2 - nov >= 0
put("mbCovPlus", f(AS["bar3"]["cov_P2p"], 2), src, "bar3.cov_P2p"); put("mbCovMinus", f(AS["bar3"]["cov_P2m"], 2), src, "bar3.cov_P2m"); put("mbRelBias", f(AS["bar3"]["abs_relbias_pooled"], 1), src, "bar3.abs_relbias_pooled")
put("mbRefSize", f(100 * AS["ref_mb_N0_size"], 1), src, "100*ref_mb_N0_size"); put("mbCheckIid", f(100 * AS["checks"]["i_noselection_tiid_size"], 1), src, "100*checks.i_noselection_tiid_size"); put("mbClUnmeasured", AS["cl_unmeasured_series"], src, "cl_unmeasured_series")
put("mbIidMin", f(100 * min(x["iid_N0_size"] for x in ser), 1), srcp, "min iid_N0_size"); put("mbIidMax", f(100 * max(x["iid_N0_size"] for x in ser), 1), srcp, "max iid_N0_size")
put("mbMbMin", f(100 * min(x["mb_N0_size"] for x in ser), 1), srcp, "min mb_N0_size"); put("mbMbMax", f(100 * max(x["mb_N0_size"] for x in ser), 1), srcp, "max mb_N0_size")
ovs = [100 * max(x["mb_N0_size"], x["mb_P1_size"]) for x in ser if over_(x, "mb", ("N0", "P1"))]; put("mbOverMin", f(min(100 * x["mb_N0_size"] for x in ser if over_(x, "mb", ("N0", "P1"))), 0), srcp, "min mb_N0_size among the oversized series"); put("mbOverMax", f(max(ovs), 0), srcp, "max of mb_N0_size, mb_P1_size among the oversized series")
put("mbPowPlusMax", f(100 * max(x["mb_P2p_power"] for x in ser), 1), srcp, "max mb_P2p_power"); put("mbPowMinusMax", f(100 * max(x["mb_P2m_power"] for x in ser), 0), srcp, "max mb_P2m_power")
me_ = [x for x in ser if x["file"] == ref_[0]["file"]]; assert len(me_) == 1; put("mbMetrEpoch", f(100 * me_[0]["mb_N0_size"], 1), srcp, "mb_N0_size of the METR series as it appears in the Epoch list")
put("mbExcluded", AE["excluded"] if isinstance(AE["excluded"], int) else len(AE["excluded"]), rel(os.path.join(AD, "audit_series.json")), "number of excluded files")
sp_ = AS["exploratory_spearman_mb_N0_size"]; put("mbRhoM", f(sp_["M"][0], 2), src, "exploratory_spearman.M rho"); put("mbRhoMP", f(sp_["M"][1], 2), src, "same, p"); put("mbRhoRec", f(sp_["records"][0], 2), src, "exploratory_spearman.records rho"); put("mbRhoRecP", f(sp_["records"][1], 2), src, "same, p")
def mbc(x, k_): return "%s [%s, %s]" % (f(100 * x[k_ + "_size"], 1), f(100 * x[k_ + "_cp"][0], 1), f(100 * x[k_ + "_cp"][1], 1))
BN = {e_["file"]: e_["benchmark"] for e_ in AE["eligible"]}
MBS = {"FrontierMath-2025-02-28-Private": "FrontierMath", "FrontierMath-Tier-4-2025-07-01-Private": "FrontierMath Tier 4", "FrontierMath-Tiers-1-3-v2-Private": "FrontierMath Tiers 1--3 v2", "OTIS Mock AIME 2024-2025": "OTIS Mock AIME", "METR Time Horizons": "METR suite, average score"}
def mbname(x): n_ = BN[x["file"]]; assert "_" not in n_ and "&" not in n_; return MBS.get(n_, n_)
def mbrow(x, nm): return "%s & %d & %d & %s & %s & %s & %s & %s & %s \\\\" % (nm, x["M"], x["rec"], mbc(x, "iid_N0"), mbc(x, "mb_N0"), mbc(x, "mb_P1"), f(100 * x["mb_P2p_power"], 1), f(100 * x["mb_P2p_cov"], 0), f(100 * x["mb_P2m_cov"], 0))
write("table_mbaudit.tex", [mbrow(x, mbname(x) + ("$^{\\ddagger}$" if over_(x, "mb", ("N0", "P1")) else "")) for x in ser] + ["\\hline", mbrow(ref_[0], "METR v1.1 (reference)")])
nm_ = [x for x in ser if x["file"] != ref_[0]["file"]]; assert len(nm_) == 21 and over_(me_[0], "iid", ("N0",)) and not over_(me_[0], "mb", ("N0", "P1"))
put("mbNNoMetr", len(nm_), srcp, "series other than the METR suite's own"); put("mbBarOneNoMetr", sum(over_(x, "iid", ("N0",)) for x in nm_), srcp, "bar-1 count without the METR average-score series"); put("mbOverNoMetr", sum(over_(x, "mb", ("N0", "P1")) for x in nm_), srcp, "oversized-mb count without it")
put("mbBarTwoNoMetr", sum(all(x["mb_%s_cp" % c_][0] <= 0.07 and x["mb_%s_cp" % c_][1] >= 0.03 for c_ in ("N0", "P1")) for x in nm_), srcp, "bar-2 count without it")
put("mbBiasNeg", sum(x["P2p_relbias"] < 0 for x in ser), srcp, "series with P2p_relbias < 0"); put("mbBiasNegSign", sum(x["P2p_relbias"] < -1 for x in ser), srcp, "series with P2p_relbias < -1, i.e. the mean fitted coefficient is negative while the planted one is positive (audit_summarize.py: relbias = mean(coef - planted)/|planted| over the valid replicates)")
_man = {}
for _ln in open(os.path.join(AD, "audit_manifest.jsonl")):
    _o = json.loads(_ln)
    if _o["construction"] == "P2p":
        for _r in _o["rows"]:
            if _r.get("coef") is not None and _r["coef"] == _r["coef"]: _man.setdefault(_o["series"], []).append((_r["coef"], _r["c"]))
_ids = [x["index"] for x in ser]; assert all(i_ in _man for i_ in _ids)
_below = sorted(sum(c_ < v_[0][1] for c_, _ in v_) / len(v_) for v_ in (_man[i_] for i_ in _ids)); _neg = sorted(sum(c_ < 0 for c_, _ in v_) / len(v_) for v_ in (_man[i_] for i_ in _ids))
assert sum(sum(c_ for c_, _ in _man[i_]) / len(_man[i_]) < _man[i_][0][1] for i_ in _ids) == sum(x["P2p_relbias"] < 0 for x in ser)
put("mbRepBelowMed", f(100 * 100 * (_below[10] + _below[11]) / 2, 0), srcp, "median over the 22 series of the share of P2+ replicates whose fitted record-only coefficient is below the planted one (audit_manifest.jsonl)")
put("mbRepNegMed", f(100 * (_neg[10] + _neg[11]) / 2, 0), srcp, "median over the 22 series of the share of P2+ replicates whose fitted coefficient is negative")
assert me_[0]["P2p_relbias"] > 0 and ref_[0]["P2p_relbias"] > 0
clm = [x for x in ser if x["cl_N0_size"] is not None]; assert len(clm) == 22 - AS["cl_unmeasured_series"]; put("mbClN", len(clm), srcp, "series with T-cl measured"); put("mbClOver", sum(over_(x, "cl", ("N0", "P1")) for x in clm), srcp, "of those, cl size >10% and CP lower >7% on N0 or P1")
put("mbMmin", min(x["M"] for x in ser), srcp, "min M"); put("mbMmax", max(x["M"] for x in ser), srcp, "max M"); put("mbRecMin", min(x["rec"] for x in ser), srcp, "min rec"); put("mbRecMax", max(x["rec"] for x in ser), srcp, "max rec")
put("mbIidValidMin", min(x["iid_N0_n"] for x in ser), srcp, "min iid_N0_n"); put("mbMbValidMin", min(x["mb_N0_n"] for x in ser), srcp, "min mb_N0_n")
# ------------------------------------------------------------------ v5: one-sided (upward) re-score of the audit (corrective amendment 2 of multibench_audit/PLAN.md), valid-fit denominators,
# and the sensitivity in which an undefined fit counts as "no rejection".  Everything here is recomputed from the stored counts in audit_onesided_summary.json; nothing is simulated.
import math
def _bcdf(k, n, p): return sum(math.exp(math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1) + i * math.log(p) + (n - i) * math.log1p(-p)) for i in range(0, k + 1))
def cp95(k, n):   # exact Clopper-Pearson 95% interval by bisection (no SciPy in the build environment); asserted below against the stored SciPy intervals
    def bis(fn):
        lo, hi = 0.0, 1.0
        for _ in range(60):
            m = (lo + hi) / 2
            if fn(m): lo = m
            else: hi = m
        return (lo + hi) / 2
    return (0.0 if k == 0 else bis(lambda q: 1 - _bcdf(k - 1, n, q) < 0.025), 1.0 if k == n else bis(lambda q: _bcdf(k, n, q) > 0.025))
OSP = os.path.join(AD, "audit_onesided_summary.json"); OS = json.load(open(OSP)); srco = rel(OSP)
assert list(OS) == [str(i) for i in range(22)] + ["900"]
oser = [OS[str(i)] for i in range(22)]; oref = OS["900"]
assert [o["name"] for o in oser] == [x["file"].replace("_external.csv", "").replace(".csv", "") for x in ser]
for o, x in zip(oser + [oref], ser + ref_):   # the one-sided file reproduces the registered two-sided rates and intervals
    for t_ in ("iid", "mb"):
        d_ = o["N0"][t_]; assert d_["n"] == x["%s_N0_n" % t_] and abs(d_["two"] / d_["n"] - x["%s_N0_size" % t_]) < 1e-9
        c_ = cp95(d_["two"], d_["n"]); assert abs(c_[0] - x["%s_N0_cp" % t_][0]) < 1e-6 and abs(c_[1] - x["%s_N0_cp" % t_][1]) < 1e-6
def ov(k, n): return k / n > 0.10 and cp95(k, n)[0] > 0.07
def cons(k, n): c_ = cp95(k, n); return c_[0] <= 0.07 and c_[1] >= 0.03
def under(k, n): return cp95(k, n)[1] < 0.03
cnt = lambda fn, t_, side, att=False: sum(fn(o["N0"][t_][side], 1000 if att else o["N0"][t_]["n"]) for o in oser)
assert cnt(ov, "iid", "two") == nb1 == 18 and cnt(ov, "mb", "two") == 9
put("mbIidOneOver", cnt(ov, "iid", "one"), srco, "series with one-sided upward F-test N0 size >10% and CP lower >7% (valid fits)"); put("mbIidOneCons", cnt(cons, "iid", "one"), srco, "same, CP interval overlapping [3,7]%"); put("mbIidOneUnder", cnt(under, "iid", "one"), srco, "same, CP upper <3%")
put("mbMbOneOver", cnt(ov, "mb", "one"), srco, "series with one-sided upward model-bootstrap N0 size oversized"); put("mbMbOneCons", cnt(cons, "mb", "one"), srco, "same, consistent with [3,7]%"); put("mbMbOneUnder", cnt(under, "mb", "one"), srco, "same, CP upper <3%")
assert (cnt(ov, "iid", "one"), cnt(cons, "iid", "one"), cnt(under, "iid", "one")) == (3, 11, 8) and (cnt(ov, "mb", "one"), cnt(cons, "mb", "one"), cnt(under, "mb", "one")) == (1, 3, 18)   # REDTEAM_CHECKS_GEMINI.md
put("mbMbTwoOverNull", cnt(ov, "mb", "two"), srco, "series with two-sided model-bootstrap N0 size oversized (N0 only)")
put("mbIidTwoOverAtt", cnt(ov, "iid", "two", True), srco, "two-sided F test oversized when undefined fits count as non-rejections (denominator 1000)"); put("mbIidOneOverAtt", cnt(ov, "iid", "one", True), srco, "one-sided, same sensitivity")
put("mbMbTwoOverAtt", cnt(ov, "mb", "two", True), srco, "two-sided bootstrap, same sensitivity"); put("mbMbOneOverAtt", cnt(ov, "mb", "one", True), srco, "one-sided bootstrap, same sensitivity")
assert cnt(ov, "iid", "two", True) >= 11   # the registered half-of-series bar still clears under the sensitivity
put("mbIidValidMax", max(o["N0"]["iid"]["n"] for o in oser), srco, "max valid F-test fits under N0"); put("mbMbValidMax", max(o["N0"]["mb"]["n"] for o in oser), srco, "max valid bootstrap fits under N0")
assert min(o["N0"]["iid"]["n"] for o in oser) == 568 and min(o["N0"]["mb"]["n"] for o in oser) == 845
put("mbIidInvalidMaxPct", f(100 - min(o["N0"]["iid"]["n"] for o in oser) / 10, 0), srco, "largest share (%) of the 1000 permutations with an undefined F-test fit under N0")
io = [100 * o["N0"]["iid"]["one"] / o["N0"]["iid"]["n"] for o in oser]; mo = [100 * o["N0"]["mb"]["one"] / o["N0"]["mb"]["n"] for o in oser]
put("mbIidOneMin", f(min(io), 1), srco, "min one-sided F-test N0 rate"); put("mbIidOneMax", f(max(io), 1), srco, "max of the same"); put("mbMbOneMin", f(min(mo), 1), srco, "min one-sided bootstrap N0 rate"); put("mbMbOneMax", f(max(mo), 1), srco, "max of the same")
put("mbMbOneBelowOne", sum(z < 1.0 for z in mo), srco, "series with one-sided bootstrap N0 rate below 1%")
ovn = [mbname(x) for o, x in zip(oser, ser) if ov(o["N0"]["iid"]["one"], o["N0"]["iid"]["n"])]; assert ovn == ["METR suite, average score", "Mystery Game Puzzles", "OpenBookQA"], ovn
assert [mbname(x) for o, x in zip(oser, ser) if ov(o["N0"]["mb"]["one"], o["N0"]["mb"]["n"])] == ["Mystery Game Puzzles"]
rm_ = oref["N0"]["mb"]; rc_ = cp95(rm_["one"], rm_["n"]); put("mbRefOne", f(100 * rm_["one"] / rm_["n"], 1), srco, "METR reference, one-sided bootstrap N0 rate"); put("mbRefOneLo", f(100 * rc_[0], 1), srco, "CP lo"); put("mbRefOneHi", f(100 * rc_[1], 1), srco, "CP hi"); put("mbRefOneN", rm_["n"], srco, "valid fits")
assert cons(rm_["one"], rm_["n"]) and not ov(rm_["one"], rm_["n"])
ri_ = oref["N0"]["iid"]; put("mbRefIidOne", f(100 * ri_["one"] / ri_["n"], 1), srco, "METR reference, one-sided F-test N0 rate"); put("mbRefIidTwo", f(100 * ri_["two"] / ri_["n"], 1), srco, "same, two-sided"); put("mbRefIidN", ri_["n"], srco, "valid fits")
put("mbRefOnePone", f(100 * oref["P1"]["mb"]["one"] / oref["P1"]["mb"]["n"], 1), srco, "METR reference, one-sided bootstrap P1 rate")
def osc(d_, side): c_ = cp95(d_[side], d_["n"]); return "%s [%s, %s]" % (f(100 * d_[side] / d_["n"], 1), f(100 * c_[0], 1), f(100 * c_[1], 1))
def osrow(o, nm): a_, b_ = o["N0"]["iid"], o["N0"]["mb"]; return "%s & %d & %s & %s & %s & %s & %d & %s & %s \\\\" % (nm, a_["n"], osc(a_, "one"), f(100 * a_["two"] / a_["n"], 1), f(100 * a_["two"] / 1000, 1), f(100 * a_["one"] / 1000, 1), b_["n"], osc(b_, "one"), f(100 * b_["two"] / b_["n"], 1))
write("table_mbonesided.tex", [osrow(o, mbname(x)) for o, x in zip(oser, ser)] + ["\\hline", osrow(oref, "METR v1.1 (reference)")])

# v8: per-model refitted horizons (33 dated models) and per-series mean fitted record curvature as a multiple of the planted upward one (P2p; relbias = mean(coef - planted)/|planted|, so mean(coef)/planted = 1 + relbias)
_rows = sorted(R["model_horizons"], key=lambda r: (r[1], r[0])); _rec = set(R["sota_records"]); assert len(_rows) == R["M"]
def _tx(n_): return n_.replace("_", "\\_").replace("&", "\\&")
def _hr(r): return "%s%s & %s & %s" % (_tx(r[0]), "$^{*}$" if r[0] in _rec else "", r[1], f(r[2], 2))
_k = -(-len(_rows) // 2); _cols = [_rows[i * _k:(i + 1) * _k] for i in range(2)]
write("table_horizons.tex", [" & ".join(_hr(c[i]) if i < len(c) else " & & " for c in _cols) + " \\\\" for i in range(_k)])
def _pb(x): return "%s & %s" % (mbname(x), f(1 + x["P2p_relbias"], 2))
_h = -(-len(ser) // 2); _a, _b = ser[:_h], ser[_h:]
write("table_plant.tex", [" & ".join([_pb(_a[i]), _pb(_b[i]) if i < len(_b) else " & "]) + " \\\\" for i in range(_h)])
# v5: curvature at which rr_eq has its pole (q = 1), and the largest q among the r_eq values printed in the paper
put("rrEqPole", f(R["linear_slope_dbl_per_yr"] / SC["span_years"], 2), rel(RP), "linear_slope_dbl_per_yr / span: curvature at which q = 1 on the real series")
qmax = R["pb"]["c_all"] * SC["span_years"] / R["linear_slope_dbl_per_yr"]; put("rrEqMaxQ", f(-((-qmax * 100) // 1) / 100, 2), rel(RP), "q of the largest r_eq printed in main text and SM (the all-model fit, rr_eq_allmodel; every simulated r_eq printed is <= 1.8): pb.c_all * span / linear slope; rounded UP to two decimals (0.5316 -> 0.54) so that the printed bound really is an upper bound; corrected 2026-11-24 from the random-audit q (0.74, r_eq 6.7), a value no longer printed after the v6 cut"); put("rrEqMax", f((1 + qmax) / (1 - qmax), 1), rel(RP), "(1+q)/(1-q) for it")
assert f((1 + qmax) / (1 - qmax), 1) == f(R["rr_eq_allmodel"], 1) == "3.3" and qmax < 0.8 and max(float(l.split("&")[3]) for l in open(os.path.join(HERE, "table_bias.tex"))) < 3.3
# ------------------------------------------------------------------ checks after the final outside reviews (redteam_final/, pre-registered in PREREG_CHATGPT_FINAL_112426.md)
RF = os.path.join(F, "redteam_final"); AB = json.load(open(os.path.join(RF, "out_abcf.json"))); DD = json.load(open(os.path.join(RF, "out_d.json"))); srcf = rel(os.path.join(RF, "out_abcf.json")); srcd = rel(os.path.join(RF, "out_d.json"))
import statistics
def pq(p): return pv(p)
prox = [("Original dates", "S0 original"), ("Availability dates (Sep 2023)", "S1 availability (davinci 2023-08-22, instruct 2023-09-18, unverified)"), ("GPT-3.5 proxy dated 6 July 2023", "S1b availability, earliest documented (instruct 2023-07-06)"), ("Both proxies dropped", "S2 proxy anchors excluded")]
lines = []
for lb, k in prox:
    a_ = AB["A"][k]; lines.append("%s & %s & %s & %s & %s & %s \\\\" % (lb, sgn(a_["sim"]["beta2_rec"], 4), f(a_["sim"]["req_rec"], 2), sgn(a_["observed"]["beta2_all"], 3), pq(a_["observed"]["hc3_p_up"]), f(a_["observed"]["req_rec"], 2)))
bo = AB["B"]["without_imputed"]; lines.append("GPT-2 zeros dropped & -- & -- & %s & %s & %s \\\\" % (sgn(bo["beta2_all"], 3), pq(bo["hc3_p_up"]), f(bo["req_rec"], 2)))
write("table_proxy.tex", lines)
put("impN", AB["B"]["n_imputed"], srcf, "B.n_imputed"); put("impHcast", AB["B"]["by_source"]["HCAST"], srcf, "B.by_source.HCAST"); put("impRe", AB["B"]["by_source"]["RE-Bench"], srcf, "B.by_source.RE-Bench"); put("impSwaa", AB["B"]["gpt2_real_swaa"], srcf, "B.gpt2_real_swaa")
put("impP", pq(bo["hc3_p_up"]), srcf, "B.without_imputed.hc3_p_up"); put("impBeta", sgn(bo["beta2_all"], 3), srcf, "B.without_imputed.beta2_all"); put("impHWith", f(AB["B"]["gpt2_h_with"], 2), srcf, "B.gpt2_h_with"); put("impHWithout", f(AB["B"]["gpt2_h_without"], 2), srcf, "B.gpt2_h_without")
put("proxSimMin", f(min(AB["A"][k]["sim"]["req_rec"] for _, k in prox), 2), srcf, "min over A scenarios of simulated r_eq"); put("proxSimMax", f(max(AB["A"][k]["sim"]["req_rec"] for _, k in prox), 2), srcf, "max over A scenarios")
put("proxAllBeta", sgn(AB["A"][prox[1][1]]["observed"]["beta2_all"], 3), srcf, "A S1 observed all-model beta2"); put("proxDropP", pq(AB["A"][prox[3][1]]["observed"]["hc3_p_up"]), srcf, "A S2 observed HC3 p_up")
put("proxAvailP", pq(AB["A"][prox[1][1]]["observed"]["hc3_p_up"]), srcf, "A S1 HC3 p_up"); put("proxAvailPb", pq(AB["A"][prox[2][1]]["observed"]["hc3_p_up"]), srcf, "A S1b HC3 p_up")
put("tieNameN", AB["C"]["observed"]["name"]["n_rec"], srcf, "C observed records, frozen order"); put("tieRevN", AB["C"]["observed"]["rev"]["n_rec"], srcf, "C reverse order"); put("tieGroupN", AB["C"]["observed"]["group"]["n_rec"], srcf, "C group rule")
rc_ = AB["C"]["observed"]["random_within_day_nrec_counts"]; put("tieRandSeventeen", rc_["17"], srcf, "C 100 random within-day orders giving 17 records"); put("tieRandEighteen", rc_["18"], srcf, "C ... giving 18")
put("tieSimName", sgn(AB["C"]["sim"]["name"]["beta2_rec"], 4), srcf, "C sim name rule"); put("tieSimGroup", sgn(AB["C"]["sim"]["group"]["beta2_rec"], 4), srcf, "C sim group rule"); put("tieSimRev", sgn(AB["C"]["sim"]["rev"]["beta2_rec"], 4), srcf, "C sim reverse rule")
_q = lambda b: b * R["span_years"] / V["params"]["rate_null"]
put("tieRrName", f((1 + _q(AB["C"]["sim"]["name"]["beta2_rec"])) / (1 - _q(AB["C"]["sim"]["name"]["beta2_rec"])), 2), srcf, "rr_eq of C sim name-rule curvature at reference span and rate"); put("tieRrGroup", f((1 + _q(AB["C"]["sim"]["group"]["beta2_rec"])) / (1 - _q(AB["C"]["sim"]["group"]["beta2_rec"])), 2), srcf, "rr_eq of C sim group-rule (best model per day) curvature")
lv = AB["F"]["leverage"]; put("levOpenAI", f(100 * lv["by_developer"]["OpenAI"], 0), srcf, "F leverage OpenAI share %"); put("levGptTwo", f(100 * lv["by_model"]["GPT-2"], 0), srcf, "F leverage GPT-2 share %"); put("levAnthropic", f(100 * lv["by_developer"]["Anthropic"], 0), srcf, "F leverage Anthropic share %")
lo_ = AB["F"]["loo"]; put("looOpenAIP", pq(lo_["OpenAI"]["hc3_p_up"]), srcf, "F LOO OpenAI HC3 p_up"); put("looOpenAIBeta", sgn(lo_["OpenAI"]["beta2_all"], 3), srcf, "F LOO OpenAI beta2"); put("looAnthP", pq(lo_["Anthropic"]["hc3_p_up"]), srcf, "F LOO Anthropic HC3 p_up"); put("looOpenAIRec", sgn(lo_["OpenAI"]["beta2_rec"], 3), srcf, "F LOO OpenAI record beta2")
put("looOtherPMax", pq(max(v["hc3_p_up"] for k, v in lo_.items() if k not in ("OpenAI", "Anthropic")), ), srcf, "F LOO largest HC3 p_up among the five other developers")
lines = ["%s & %d & %s & %s & %s & %s \\\\" % (d, v["n_removed"], sgn(v["beta2_all"], 3), pq(v["hc3_p_up"]), sgn(v["beta2_rec"], 3), f(100 * lv["by_developer"][d], 0) + "\\%") for d, v in sorted(lo_.items(), key=lambda x: -x[1]["n_removed"])]
write("table_loo.tex", lines)
lines = []
for sat in ("0.80", "0.90", "0.95", "none"):
    cells = []
    for cons in ("N0", "P1", "PF"):
        rows = [(i, r[cons]) for i, r in DD[sat].items() if i != "900" and r[cons]]; v = [x["verdict_up"] for _, x in rows]
        assert len(v) == v.count("OVER") + v.count("in") + v.count("under") + v.count("mid") + v.count("nm"); cells.append("%d/%d/%d/%d/%d & %s" % (v.count("OVER"), v.count("in"), v.count("under"), v.count("mid"), v.count("nm"), f(100 * float(statistics.median([x["rate_up"] for _, x in rows])), 1)))
    lines.append("%s & %s \\\\" % ("none" if sat == "none" else sat.replace("0.", "."), " & ".join(cells)))
write("table_satcut.tex", lines)

ov_ = [sum(1 for i, r in DD[s_].items() if i != "900" and r[c_] and r[c_]["verdict_up"] == "OVER") for s_ in DD for c_ in ("N0", "P1", "PF")]
put("satOverMin", min(ov_), srcd, "min over 12 cut-off x construction cells of series OVER upward"); put("satOverMax", max(ov_), srcd, "max over the same")
put("satRefP", f(100 * DD["0.90"]["900"]["P1"]["rate_up"], 0), srcd, "METR v1.1 reference upward one-sided rate under P1 (PF: 25.0)"); put("satRefPF", f(100 * DD["0.90"]["900"]["PF"]["rate_up"], 0), srcd, "same under PF")
put("proxReps", commas(40000), srcf, "REPS in run_abcf.py")
# ------------------------------------------------------------------ v7: hinge vs quadratic (results/F_hinge.json, prereg design/PREREG_HINGE.md) and split-task replication (results/split_task/, prereg design/PREREG_SPLIT_TASK.md)
HGP = os.path.join(F, "results", "F_hinge.json"); HG = json.load(open(HGP)); srch = rel(HGP); hs, hr, ht = HG["sim"], HG["real_fit"], HG["real_tests"]
def pct(x): return f(100 * x, 1)
put("hgR", commas(hs["T_H"]["R"]), srch, "sim.T_H.R"); put("hgPost", HG["n_post_break_models"], srch, "n_post_break_models")
def _aiccv(m, k): n_ = 33; return n_ * math.log(hr[m]["RSS"] / n_) + 2 * k + 2 * k * (k + 1) / (n_ - k - 1)
assert abs(_aiccv("Q", 3) - hr["Q"]["AICc"]) < 1e-6 and abs(_aiccv("H", 4) - hr["H"]["AICc"]) < 1e-6  # stored AICc counts regression coefficients only (3 and 4)
put("hgAiccDiffV", f(_aiccv("H", 5) - _aiccv("Q", 4), 2), srch, "AICc with the residual variance counted as a parameter (k+1), H minus Q from real_fit RSS; positive: quadratic lower")
put("hgAiccDiff", f(hr["Q"]["AICc"] - hr["H"]["AICc"], 2), srch, "real_fit Q.AICc - H.AICc (positive: hinge lower)"); put("hgBicDiff", f(hr["H"]["BIC"] - hr["Q"]["BIC"], 1), srch, "real_fit H.BIC - Q.BIC (positive: quadratic lower)")
assert 0 < hr["Q"]["AICc"] - hr["H"]["AICc"] < 0.5 and hr["H"]["BIC"] > hr["Q"]["BIC"] and hr["H"]["LOMO_mse"] < hr["Q"]["LOMO_mse"]
put("hgCvQ", f(hr["Q"]["LOMO_mse"], 2), srch, "real_fit.Q.LOMO_mse"); put("hgCvH", f(hr["H"]["LOMO_mse"], 2), srch, "real_fit.H.LOMO_mse")
put("hgCQ", f(hr["Q"]["coef"][2], 3), srch, "real_fit.Q.coef[2]"); put("hgCQH", neg(hr["QH"]["coef"][2], 3), srch, "real_fit.QH.coef[2]: curvature with the hinge terms in the model")
assert abs(hr["Q"]["coef"][2] - R["pb"]["c_all"]) < 1e-6
put("hgCQHp", pv(ht["QH_c"]["p_two"]), srch, "real_tests.QH_c.p_two (Webb wild cluster)"); put("hgJointGivenC", pv(ht["QH_dg_joint"]["p"]), srch, "real_tests.QH_dg_joint.p")
put("hgD", sgn(hr["H"]["coef"][2], 2), srch, "real_fit.H.coef[2] level jump (log2 units)"); put("hgG", sgn(hr["H"]["coef"][3], 2), srch, "real_fit.H.coef[3] slope change (doublings/yr)")
put("hgDp", pv(ht["H_d"]["p_two"]), srch, "real_tests.H_d.p_two"); put("hgGp", pv(ht["H_g"]["p_two"]), srch, "real_tests.H_g.p_two"); put("hgJointP", pv(ht["H_dg_joint"]["p"]), srch, "real_tests.H_dg_joint.p")
# v18: Table S15 uses AICc with the residual variance counted (k = coefficients + 1), re-run on trench by code/hinge_aiccv.py (same seeds and draws)
HVD = os.path.join(F, "results", "hinge_aiccv"); HV = {k_: json.load(open(os.path.join(HVD, k_ + ".json"))) for k_ in ("T_L", "T_Q", "T_H", "PC_H", "PC_Q")}
for k_ in HV: assert all(abs(HV[k_]["select_AICc_coefonly_recomputed"][c_] - hs[k_]["select_AICc"][c_]) < 1e-12 for c_ in "LQH"), k_  # re-run reproduces stored coefficient-only rates exactly
assert all(abs(HV[k_]["real_AICc_kplus1"][m_] - _aiccv(m_, {"L": 3, "Q": 4, "H": 5}[m_])) < 1e-6 for k_ in HV for m_ in "QH")
hs = {k_: dict(R=HV[k_]["R"], select_AICc=HV[k_]["select_AICc_kplus1"]) for k_ in HV}; srch = rel(HVD)
for nm_, k_ in (("TL", "T_L"), ("TQ", "T_Q"), ("TH", "T_H"), ("PCH", "PC_H"), ("PCQ", "PC_Q")):
    for c_ in "LQH": put("hg%sSel%s" % (nm_, c_), pct(hs[k_]["select_AICc"][c_]), srch, "sim.%s.select_AICc.%s (%%)" % (k_, c_))
assert hs["PC_Q"]["select_AICc"]["Q"] < 0.90 <= hs["PC_H"]["select_AICc"]["H"] and hs["T_H"]["select_AICc"]["Q"] > hs["T_H"]["select_AICc"]["H"]
write("table_hinge.tex", ["%s & %s & %s & %s \\\\" % (lb_, pct(hs[k_]["select_AICc"]["L"]), pct(hs[k_]["select_AICc"]["Q"]), pct(hs[k_]["select_AICc"]["H"])) for lb_, k_ in (("Line", "T_L"), ("Fitted quadratic", "T_Q"), ("Fitted hinge", "T_H"), ("Control: slope $\\times4$ at the break", "PC_H"), ("Control: quadratic, $rr=4$", "PC_Q"))])
SPD = os.path.join(F, "results", "split_task"); SR = json.load(open(os.path.join(SPD, "real.json"))); SB = json.load(open(os.path.join(SPD, "boot.json"))); SCn = json.load(open(os.path.join(SPD, "controls.json"))); srcs = rel(SPD)
put("stModels", len(SR["invalid_frac"]), srcs, "real.json: models"); put("stSplits", SR["n_splits"], srcs, "real.json n_splits")
assert SR["exactness"] == 0.0 and SR["n_estimable_directions"] == SR["of"] and max(SR["invalid_frac"].values()) == 0.0
for k_ in ("D1", "D2"):
    nm_ = {"D1": "stDone", "D2": "stDtwo"}[k_]; put(nm_, sgn(SR["mean"][k_], 3), srcs, "real.json mean.%s" % k_); put(nm_ + "Lo", sgn(SB["family"][k_][0], 2), srcs, "boot.json family.%s lower" % k_); put(nm_ + "Hi", sgn(SB["family"][k_][1], 2), srcs, "boot.json family.%s upper" % k_)
    assert SB["family"][k_][0] < 0 < SB["family"][k_][1] and SB["two_way"][k_][0] < 0 < SB["two_way"][k_][1]
put("stDoneTwLo", sgn(SB["two_way"]["D1"][0], 2), srcs, "boot.json two_way.D1 lower"); put("stDoneTwHi", sgn(SB["two_way"]["D1"][1], 2), srcs, "upper"); put("stDtwoTwLo", sgn(SB["two_way"]["D2"][0], 2), srcs, "boot.json two_way.D2 lower"); put("stDtwoTwHi", sgn(SB["two_way"]["D2"][1], 2), srcs, "upper")
put("stCone", sgn(SCn["C1"]["D1"]["mean"], 3), srcs, "controls.json C1.D1.mean (selection on run noise alone)"); put("stConeSe", f(SCn["C1"]["D1"]["se"], 3), srcs, "controls.json C1.D1.se")
put("stCsel", f(SR["mean"]["CXs"], 2), srcs, "real.json mean.CXs"); put("stCrep", f(SR["mean"]["CYs"], 2), srcs, "real.json mean.CYs"); put("stCall", f(SR["mean"]["CYa"], 2), srcs, "real.json mean.CYa"); put("stR", f(SR["mean"]["r"], 2), srcs, "real.json mean.r")
lod = SR["lodo"]; put("stLodoDtwoMin", sgn(min(v["D2"] for v in lod.values()), 2), srcs, "real.json lodo min D2"); put("stLodoDtwoMax", sgn(max(v["D2"] for v in lod.values()), 2), srcs, "lodo max D2")
# ---- merged main-text size-and-power table (v2): parsed from the generated full tables
def _rows(fn): return [[c.strip() for c in ln.rstrip().rstrip("\\").split("&")] for ln in open(os.path.join(HERE, fn)).read().split("\n") if "&" in ln and not ln.startswith("\\multicolumn")]
SZ = {r[0]: r for r in _rows("table_size.tex")}; PW = {r[0]: r for r in _rows("table_power.tex")}; A2 = {r[0]: r for r in _rows("table_a2size.tex")}
def _cpstrip(c): return re.sub(r" \{\[\}.*?\{\]\}", "", c)
spec = [("record-only fit, parametric bootstrap", "record-only fit", SZ, "record-only fit", "record-only fit"), ("censored likelihood", "censored-crossing likelihood", SZ, "censored likelihood", "censored-crossing likelihood"),
        ("inverse-Mills", "inverse-Mills correction", SZ, "inverse-Mills", "inverse-Mills correction"), ("random audit", "random audit (25\\%)", SZ, "random audit", "random audit (25\\%)"),
        ("record timing", "record timing", SZ, "record timing", "record timing")]
ML = []
for lab, szk, _, pwk, _ in spec:
    z = SZ[szk]; p = PW[pwk]; ML.append("%s & %s & %s & %s & %s & %s & %s & %s \\\\" % (lab, _cpstrip(z[1]), z[2], z[7], z[8], p[3], p[5], p[6]))
for lab, a2k, pwk in (("HC3 $t$, all models", "HC3 $t$", "HC3 $t$"), ("wild bootstrap, all models", "wild bootstrap", "HC3, wild bootstrap $p$")):
    a = A2[a2k]; p = PW[pwk]; up = float(re.match(r"[\d.]+", a[1]).group()); two = float(re.match(r"[\d.]+", a[2]).group()); assert 3.5 <= up <= 6.5 and 3.5 <= two <= 6.5, a
    ML.append("%s & %s & %s & yes & no & %s & %s & %s \\\\" % (lab, _cpstrip(a[1]), a[2], p[3], p[5], p[6]))
write("table_main.tex", ML)
write("numbers.tex", ["% generated by make_numbers.py; do not edit"] + TEX); write("numbers_manifest.txt", MAN)
print("wrote %d macros" % len(TEX))

"""Figures for paper F, drawn from the same result files as numbers.tex (imports make_numbers, which re-reads them).
Run: /usr/local/bin/python3 make_figs.py   (needs matplotlib)"""
import os, sys, json, datetime as dt, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_numbers as mn
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE = mn.HERE; FIG = os.path.join(HERE, "figs"); os.makedirs(FIG, exist_ok=True)
plt.rcParams.update({"font.size": 7.5, "axes.spines.top": False, "axes.spines.right": False, "font.family": "DejaVu Sans", "axes.linewidth": 0.6,
                     "xtick.major.width": 0.6, "ytick.major.width": 0.6, "legend.frameon": False, "pdf.fonttype": 42})
BLUE, ORANGE, GREEN, VERM, PURP, GREY, INK = "#0072B2", "#E69F00", "#009E73", "#D55E00", "#CC79A7", "#8a8a8a", "#222222"

# ---------------------------------------------------------------- Fig. 1: the selection bias
I = mn.I; s = np.array([r["sigma"] for r in I["rows"]]); rr = np.array([r["rr_eq_sota"] for r in I["rows"]])
qa = np.array([r["mean_beta2_all"] for r in I["rows"]]) * I["span_years"] / I["rate"]; rra = (1 + qa) / (1 - qa)
fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.7), gridspec_kw=dict(width_ratios=[1.15, 1], wspace=0.55))
a = ax[0]; sm = mn.V["params"]["sigma_m"]
a.axhline(1, color=GREY, lw=0.6, ls=":"); a.axvline(sm, color=GREY, lw=0.6, ls=":")
a.plot(s, rr, "-o", color=VERM, ms=3, lw=1.4); a.plot(s, rra, "-o", color=BLUE, ms=3, lw=1.4)
a.plot([sm], [float(mn.bias["sota"][4])], marker="D", color=INK, ms=5, ls="none", zorder=5)
a.annotate("calibrated simulator,\nrecord-only fit: %.2f" % float(mn.bias["sota"][4]), (sm, float(mn.bias["sota"][4])), (0.08, 2.05), fontsize=7.5, arrowprops=dict(arrowstyle="-", lw=0.5, color=INK))
a.text(1.62, 2.05, "fit through\nrecords only", color=VERM, fontsize=7.5, ha="left"); a.text(1.95, 1.07, "fit through all models", color=BLUE, fontsize=7.5, ha="right")
a.text(sm - 0.03, 3.0, "calibrated\nmodel noise", color=GREY, fontsize=8, va="top", ha="right")
a.set_xlabel("model-level noise SD (doublings, i.e. log$_2$ units)"); a.set_ylabel("apparent acceleration under a\ntruly exponential trend ($rr_{\\rm eq}$)")
a.set_ylim(0.9, 3.1); a.set_xlim(0, 2.05); a.set_title("(a) Gaussian illustration", loc="left", fontsize=8)
b = ax[1]; ks = ["sota", "ipw", "mir", "heck", "audit", "all"]; lab = ["record-only fit", "naive IPW", "mirror envelope", "inverse-Mills", "random audit (25%)", "all-model fit"]
v = [float(mn.bias[k][4]) for k in ks]; col = [VERM, GREY, GREY, GREEN, GREEN, BLUE]; y = np.arange(len(ks))[::-1]
b.barh(y, [x - 1 for x in v], left=1, color=col, height=0.62); b.axvline(1, color=INK, lw=0.6)
b.axvspan(0.9, 1.1, color=GREEN, alpha=0.08, lw=0)
for yy, x in zip(y, v): b.text(x + 0.015, yy, "%.2f" % x, va="center", fontsize=7.5)
b.set_yticks(y); b.set_yticklabels(lab); b.set_xlim(0.9, 1.95); b.set_xlabel("mean $rr_{\\rm eq}$ under the null")
b.set_title("(b) calibrated simulator", loc="left", fontsize=8); b.tick_params(axis="y", length=0)
fig.savefig(os.path.join(FIG, "fig_bias.pdf"), bbox_inches="tight"); plt.close(fig)

# ---------------------------------------------------------------- Fig. 2: size-adjusted power
alts = ["R_rr1.25", "R_rr1.5", "R_rr2", "R_rr3", "R_rr4"]; x = np.array([1, 1.25, 1.5, 2, 3, 4])
def curve(k):
    v0 = float(mn.adj[(k, "R_rr2")][1].split()[0])
    p = [v0] + [float(mn.adj[(k, a_)][4]) for a_ in alts]
    ci = [[v0, v0]] + [[float(z) for z in mn.adj[(k, a_)][5].strip("[]").split(",")] for a_ in alts]
    return np.array(p), np.array(ci)
fig, a = plt.subplots(figsize=(3.4, 3.0))
a.axhline(80, color=GREY, lw=0.6, ls=":"); a.text(1.02, 81.5, "80% power", color=GREY, fontsize=8)
a.axhline(5, color=GREY, lw=0.6, ls=":"); a.axvline(2, color=GREY, lw=0.6, ls=":")
sty = [("ccl", GREY, "--", "censored-crossing lik.*"), ("mir", GREY, "-.", "mirror envelope*"), ("audit", GREEN, "-", "random audit"), ("heck", PURP, "-", "inverse-Mills"),
       ("sota", VERM, "-", "record-only fit"), ("rrate", BLUE, "-", "record timing"), ("contr", ORANGE, "-", "record-minus-all")]
yo = dict(ccl=2.5, mir=-2.5, audit=0, heck=0, sota=-0.5, rrate=0, contr=0)
for k, c, ls, lb in sty:
    p, ci = curve(k); a.plot(x, p, ls, color=c, lw=1.3, marker="o", ms=2.5); a.fill_between(x, ci[:, 0], ci[:, 1], color=c, alpha=0.15, lw=0)
    a.text(4.08, p[-1] + yo[k], lb, color=c if c != GREY else "#555555", fontsize=8, va="center")
a.set_xscale("log"); a.set_xticks(x); a.set_xticklabels(["1\n(null)", "1.25", "1.5", "2", "3", "4"]); a.minorticks_off()
a.set_xlim(0.95, 4.05); a.set_ylim(0, 100); a.set_xlabel("true acceleration $rr$ (end rate / start rate)"); a.set_ylabel("size-adjusted power, upward 5% (%)")
a.text(2.03, 93, "pre-specified\nmeaningful effect", fontsize=8, color=GREY, va="top")
fig.savefig(os.path.join(FIG, "fig_power.pdf"), bbox_inches="tight"); plt.close(fig)

# ---------------------------------------------------------------- Fig. 3: the real series
R = mn.R; rows = sorted(R["model_horizons"], key=lambda r: (r[1], r[0])); d = [dt.date.fromisoformat(r[1]) for r in rows]; yv = np.array([r[2] for r in rows])
t = np.array([(z - d[0]).days for z in d], float) / 365.25; names = [r[0] for r in rows]
rec = np.array([n in set(R["sota_records"]) for n in names]); pm = np.concatenate([[-np.inf], np.maximum.accumulate(yv)[:-1]])
assert (rec == (yv > pm)).all() and rec.sum() == R["n_records"]
X2 = np.stack([np.ones_like(t), t - t.mean(), (t - t.mean()) ** 2], 1); cq = np.linalg.lstsq(X2, yv, rcond=None)[0]; cl = np.linalg.lstsq(X2[:, :2], yv, rcond=None)[0]
assert abs(cq[2] - R["reg"]["reg_c"]) < 1e-6 and abs(cl[1] - R["linear_slope_dbl_per_yr"]) < 1e-6, (cq, cl)
cs = np.linalg.lstsq(X2[rec], yv[rec], rcond=None)[0]; assert abs(cs[2] - R["pb"]["sota_c"]) < 1e-6
yr0 = d[0].year + (d[0] - dt.date(d[0].year, 1, 1)).days / 365.25; T = yr0 + t; g = np.linspace(t[0], t[-1], 200); G = np.stack([np.ones_like(g), g - t.mean(), (g - t.mean()) ** 2], 1)
fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.0), gridspec_kw=dict(width_ratios=[1, 1.25], wspace=0.28))
for j, a in enumerate(ax):
    a.plot(yr0 + g, G[:, :2] @ cl, "--", color=GREY, lw=1.0, label="exponential, all models"); a.plot(yr0 + g, G @ cq, "-", color=BLUE, lw=1.3, label="quadratic, all models")
    a.plot(yr0 + g, G @ cs, "-", color=VERM, lw=1.0, alpha=0.8, label="quadratic, records only")
    a.step(np.concatenate([T[rec], [T[-1]]]), np.concatenate([yv[rec], [yv[rec][-1]]]), where="post", color=VERM, lw=0.6, alpha=0.5)
    a.plot(T[~rec], yv[~rec], "o", mfc="white", mec=INK, ms=4, mew=0.7, ls="none", label="other models (%d)" % (~rec).sum())
    a.plot(T[rec], yv[rec], "o", color=VERM, ms=4, ls="none", label="records (%d)" % rec.sum())
    tk = [np.log2(2 / 60), 0, 3, np.log2(60), np.log2(480)]; a.set_yticks(tk); a.set_yticklabels(["2 s", "1 min", "8 min", "1 h", "8 h"])
    if j == 1: tk = [0, 2, np.log2(15), np.log2(60), np.log2(240)]; a.set_yticks(tk); a.set_yticklabels(["1 min", "4 min", "15 min", "1 h", "4 h"]); a.set_xticks([2023, 2024, 2025, 2026])
    a.set_xlabel("release date")
ax[0].set_ylabel("50% time horizon (refit)"); ax[0].set_title("full window", loc="left", fontsize=8); ax[0].legend(fontsize=7, loc="upper left", handlelength=1.2, labelspacing=0.3, borderaxespad=0.1)
ax[0].set_ylim(-5.5, 15); ax[1].set_xlim(2023.0, 2026.05); ax[1].set_ylim(-3.6, 8.6); ax[1].set_title("(b) 2023 onwards", loc="left", fontsize=8)
for n in ("GPT-2", "davinci-002 (GPT-3)", "gpt-3.5-turbo-instruct", "GPT-4 0314"):
    i = names.index(n); ax[0].annotate(n.replace("davinci-002 (GPT-3)", "GPT-3 (proxy)").replace("gpt-3.5-turbo-instruct", "GPT-3.5 (proxy)").replace(" 0314", ""), (T[i], yv[i]), {"GPT-4 0314": (-24, 7), "GPT-2": (6, -5), "davinci-002 (GPT-3)": (-30, 7), "gpt-3.5-turbo-instruct": (-48, 5)}.get(n, (4, -9)), textcoords="offset points", fontsize=7)
for n, off in (("Claude Opus 4.5", (-70, 3)), ("GPT-5", (6, -12)), ("o3", (-14, 5)), ("Qwen2-72B", (5, -3)), ("GPT-4o", (-28, 6))):
    i = names.index(n); ax[1].annotate(n, (T[i], yv[i]), off, textcoords="offset points", fontsize=8)
# the two backdated proxy models: marked as diamonds at the dates METR gives them; crosses at their 2023 availability dates
PX = {"davinci-002 (GPT-3)": dt.date(2023, 8, 22), "gpt-3.5-turbo-instruct": dt.date(2023, 9, 18)}
for j, a in enumerate(ax):
    for n, av in PX.items():
        i = names.index(n); ya = av.year + (av - dt.date(av.year, 1, 1)).days / 365.25
        if j == 0:
            a.plot([T[i]], [yv[i]], "D", mfc="none", mec=GREEN, ms=7, mew=1.1, ls="none", label="backdated proxies (METR dates)" if n.startswith("davinci") else None)
            a.annotate("", (ya, yv[i]), (T[i], yv[i]), arrowprops=dict(arrowstyle="->", color=GREEN, lw=0.6, ls=":"))
        a.plot([ya], [yv[i]], "x", color=GREEN, ms=5, mew=1.1, ls="none", label="same, 2023 availability dates" if (n.startswith("davinci") and j == 0) else None)
ax[0].legend(fontsize=6, loc="upper left", handlelength=1.2, labelspacing=0.25, borderaxespad=0.1)
fig.canvas.draw(); rend = fig.canvas.get_renderer(); inv = fig.dpi_scale_trans.inverted()
fig.savefig(os.path.join(FIG, "fig_real.pdf"), bbox_inches=ax[0].get_tightbbox(rend).transformed(inv).expanded(1.06, 1.06))
fig.savefig(os.path.join(FIG, "fig_real_b.pdf"), bbox_inches=ax[1].get_tightbbox(rend).transformed(inv).expanded(1.02, 1.02)); plt.close(fig)

# ---------------------------------------------------------------- Opening figure (v5): the schedule reversal, paired null distributions
# EXPLORATORY illustration made for the paper (v5, after the outside red-team reviews of v4 asked for the schedule reversal to be Figure 1).  It REDRAWS the
# Gaussian schedule illustration (make_schedule_illustration.py: exactly exponential trend at the simulator's null rate, independent normal model errors with the
# calibrated model-level SD, 33 models, same span) with a new seed and with the SAME noise draws used for the three calendars (paired).  The redraw is asserted to
# reproduce the stored means of schedule_illustration.json, which remain the reported values; no number in the text is taken from this redraw.
SC = mn.SC; span = SC["span_years"]; rate = SC["rate"]; sg = SC["sigma"]; NB = 20000; n = len(t); assert abs(t[-1] - span) < 1e-9
CAL = [("real", "real METR v1.0 dates", t, VERM), ("even", "evenly spaced", np.linspace(0, span, n), BLUE), ("reflected", "real dates reflected", np.sort(span - t), GREEN)]
Z = np.random.default_rng(np.random.SeedSequence([4715, 1])).normal(0, sg, (NB, n)); dist = {}
for key, lab, tt, col in CAL:
    Xc = np.stack([np.ones_like(tt), tt - tt.mean(), (tt - tt.mean()) ** 2], 1); ys = rate * tt + Z
    pmx = np.full_like(ys, -np.inf); pmx[:, 1:] = np.maximum.accumulate(ys, axis=1)[:, :-1]; recs = ys > pmx; c = np.full(NB, np.nan)
    for i in range(NB):
        m = recs[i]
        if m.sum() >= 4: c[i] = np.linalg.lstsq(Xc[m], ys[i, m], rcond=None)[0][2]
    dist[key] = c; st = SC["rows"][key]["mean_beta2_sota"]; assert abs(np.nanmean(c) - st) < 0.003, (key, np.nanmean(c), st)
obs = R["pb"]["sota_c"]; ok3 = ~np.isnan(dist["real"]) & ~np.isnan(dist["even"]) & ~np.isnan(dist["reflected"])
fig, ax = plt.subplots(1, 2, figsize=(7.0, 1.7), gridspec_kw=dict(width_ratios=[0.6, 1], wspace=0.1))
a = ax[0]
for k, (key, lab, tt, col) in enumerate(CAL):
    yy = 2 - k; a.hlines(yy, 0, span, color="#d0d0d0", lw=0.6); a.vlines(tt, yy - 0.22, yy + 0.22, color=col, lw=0.9)
    a.text(0, yy + 0.30, lab, color=col, fontsize=7.5, ha="left", va="bottom")
a.set_ylim(-0.45, 2.75); a.set_yticks([]); a.spines["left"].set_visible(False); a.set_xlim(-0.15, span + 0.15); a.set_xlabel("years since the first release")
a.set_title("(a) three calendars, %d models" % n, loc="left", fontsize=8)
b = ax[1]; bins = np.linspace(-0.40, 0.50, 73)
for key, lab, tt, col in CAL:
    v = dist[key][~np.isnan(dist[key])]; b.hist(v, bins=bins, density=True, histtype="stepfilled", color=col, alpha=0.16, lw=0); b.hist(v, bins=bins, density=True, histtype="step", color=col, lw=1.1)
top = b.get_ylim()[1]; b.set_ylim(0, top * 1.38); b.axvline(0, color=GREY, lw=0.6, ls=":"); b.plot([obs, obs], [0, top * 1.04], color=INK, lw=1.3)
for key, lab, tt, col in CAL: b.plot([SC["rows"][key]["mean_beta2_sota"]] * 2, [0, top * 1.04], color=col, lw=1.0, ls="--")
b.text(0.0, top * 1.27, "real dates: mean %+.3f" % SC["rows"]["real"]["mean_beta2_sota"], color=VERM, fontsize=7, ha="left", va="center")
b.text(-0.035, top * 1.27, "evenly spaced: mean %+.3f" % SC["rows"]["even"]["mean_beta2_sota"], color=BLUE, fontsize=8, ha="right", va="center")
b.text(-0.035, top * 1.13, "reflected: mean %+.3f" % SC["rows"]["reflected"]["mean_beta2_sota"], color=GREEN, fontsize=8, ha="right", va="center")
b.text(obs + 0.085, top * 0.70, "observed METR\nrecord-only\ncurvature %+.3f" % obs, color=INK, fontsize=8, ha="left", va="center")
b.annotate("", (obs, top * 0.70), (obs + 0.08, top * 0.70), arrowprops=dict(arrowstyle="-", lw=0.5, color=INK))
b.set_xlim(-0.40, 0.50); b.set_yticks([]); b.spines["left"].set_visible(False); b.set_xlabel("record-only fitted curvature (doublings per year$^2$)")
b.set_title("(b) steady growth, same noise draws on each calendar", loc="left", fontsize=8)
fig.savefig(os.path.join(FIG, "fig_open.pdf"), bbox_inches="tight"); plt.close(fig)
print("opening figure (paired redraw, seed [4715,1]): means real %+.4f even %+.4f reflected %+.4f (stored %+.4f %+.4f %+.4f); share of draws with real > even %.3f, real > reflected %.3f; upper-tail share of the observed %+.3f at the real dates in this Gaussian null %.3f (registered fitted-null p_up %.2f)" % (
    np.nanmean(dist["real"]), np.nanmean(dist["even"]), np.nanmean(dist["reflected"]), SC["rows"]["real"]["mean_beta2_sota"], SC["rows"]["even"]["mean_beta2_sota"], SC["rows"]["reflected"]["mean_beta2_sota"],
    (dist["real"][ok3] > dist["even"][ok3]).mean(), (dist["real"][ok3] > dist["reflected"][ok3]).mean(), obs, np.nanmean(dist["real"][~np.isnan(dist["real"])] >= obs), R["pb"]["sota_pup"]))
print("figures written")

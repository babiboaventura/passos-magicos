"""
Análise exploratória e estatística (perguntas 1-8, 10 e 11 do Datathon).

Entrada : data/processed/painel_alunos.csv e pares_modelo.csv (gerados por src/limpeza.py)
Saída   : reports/figuras/*.png, reports/tabelas/*.csv, reports/metricas_chave.json

Convenções
  * "Em defasagem" = fase do aluno < fase ideal (IAN = 5 ou 2,5).
  * Comparações ao longo do tempo usam DUAS lentes: (a) foto anual da população; (b) os MESMOS alunos
    acompanhados entre anos (painel). A diferença entre as duas é uma das descobertas do estudo.
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

RAIZ = Path(__file__).resolve().parents[1]
FIG = RAIZ / "reports/figuras"
TAB = RAIZ / "reports/tabelas"
FIG.mkdir(parents=True, exist_ok=True)
TAB.mkdir(parents=True, exist_ok=True)

NAVY, TEAL, AMBER, CORAL, GRAY, LIGHT = "#0B1F3A", "#0E7C86", "#F2A900", "#D1495B", "#8A94A6", "#E9EEF5"
COR_PEDRA = {"Quartzo": "#E39BB0", "Ágata": "#7DB0B8", "Ametista": "#8E5BB5", "Topázio": "#F2A900"}
COR_NIVEL = {"Adequado (≥ 0)": TEAL, "Moderada (-1 a -2)": AMBER, "Severa (≤ -3)": CORAL}
ORDEM_PEDRA = ["Quartzo", "Ágata", "Ametista", "Topázio"]

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11, "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": GRAY, "axes.labelcolor": NAVY, "xtick.color": NAVY, "ytick.color": NAVY,
    "axes.titleweight": "bold", "axes.titlesize": 13, "axes.titlecolor": NAVY, "figure.dpi": 100,
    "savefig.dpi": 200, "savefig.bbox": "tight", "axes.grid": True, "grid.color": "#DDE3EC", "grid.linewidth": .7,
    "axes.axisbelow": True,
})

M = {}  # métricas-chave, exportadas em JSON


def br(x, n=1):
    """Número no formato brasileiro (vírgula decimal)."""
    return f"{x:.{n}f}".replace(".", ",")


def salva(fig, nome):
    fig.savefig(FIG / f"{nome}.png", facecolor="white")
    plt.close(fig)


def carrega():
    p = pd.read_csv(RAIZ / "data/processed/painel_alunos.csv")
    pares = pd.read_csv(RAIZ / "data/processed/pares_modelo.csv")
    v = p[~p.formado].copy()                              # sem formados
    a = v[~v.sem_indicadores].copy()                      # alunos avaliados
    return p, v, a, pares


# ------------------------------------------------------------------ Q1 · IAN
def q1(v):
    n = v.groupby("ano").size()
    dist = pd.crosstab(v.ano, v.nivel_defasagem, normalize="index") * 100
    dist = dist[["Adequado (≥ 0)", "Moderada (-1 a -2)", "Severa (≤ -3)"]]
    dist.round(1).to_csv(TAB / "q1_nivel_defasagem_por_ano.csv")
    cont = pd.crosstab(v.ano, v.nivel_defasagem)[dist.columns]
    cont.to_csv(TAB / "q1_nivel_defasagem_contagem.csv")
    M["q1"] = {"n": n.to_dict(), "pct": dist.round(1).to_dict("index"), "contagem": cont.to_dict("index")}

    w = v.pivot(index="ra", columns="ano", values="defasagem")
    c3 = w.dropna()
    M["q1"]["coorte3_n"] = len(c3)
    M["q1"]["coorte3_defas_media"] = c3.mean().round(2).to_dict()
    M["q1"]["coorte3_pct_defasado"] = (c3 < 0).mean().mul(100).round(1).to_dict()
    for a, b in [(2022, 2023), (2023, 2024)]:
        t = w[[a, b]].dropna()
        M["q1"][f"trans_{a}_{b}"] = {"n": len(t), "melhorou": round((t[b] > t[a]).mean() * 100, 1),
                                     "igual": round((t[b] == t[a]).mean() * 100, 1),
                                     "piorou": round((t[b] < t[a]).mean() * 100, 1)}
    por_fase = (v.pivot_table(index="fase", columns="ano", values="em_defasagem", aggfunc="mean") * 100).round(1)
    por_fase.to_csv(TAB / "q1_pct_defasado_por_fase.csv")
    M["q1"]["pct_defasado_fase"] = por_fase.to_dict()

    # figura: barras empilhadas + coorte
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.3), gridspec_kw={"width_ratios": [1.15, 1]})
    b = np.zeros(len(dist))
    for col in dist.columns:
        ax[0].bar(dist.index.astype(str), dist[col], bottom=b, color=COR_NIVEL[col], label=col, width=.6)
        for i, val in enumerate(dist[col]):
            if val > 4:
                ax[0].text(i, b[i] + val / 2, f"{br(val, 0)}%", ha="center", va="center", color="white", fontweight="bold")
        b += dist[col].values
    ax[0].set_ylabel("% dos alunos"); ax[0].set_title("Perfil de defasagem (IAN) por ano")
    ax[0].legend(frameon=False, fontsize=9, loc="upper center", bbox_to_anchor=(.5, -.1), ncol=3)
    ax[0].grid(axis="x", visible=False)
    ax[1].plot(["2022", "2023", "2024"], c3.mean().values, marker="o", color=TEAL, lw=3, label="Mesmos 468 alunos")
    ax[1].plot(["2022", "2023", "2024"], [v[v.ano == y].defasagem.mean() for y in (2022, 2023, 2024)],
               marker="o", color=GRAY, lw=2, ls="--", label="Todos os alunos do ano")
    ax[1].axhline(0, color=NAVY, lw=1)
    for i, val in enumerate(c3.mean().values):
        ax[1].text(i, val + .05, br(val, 2), ha="center", color=TEAL, fontweight="bold")
    ax[1].set_ylabel("Defasagem média (fases)"); ax[1].set_title("Defasagem média: menos negativa = melhor")
    ax[1].legend(frameon=False, fontsize=9, loc="lower right")
    fig.tight_layout(); salva(fig, "q1_defasagem")


# ------------------------------------------------------------------ Q2 · IDA
def q2(a):
    r = a.groupby("ano").ida.agg(["count", "mean", "median", "std"]).round(2)
    r["ic95"] = (1.96 * r["std"] / np.sqrt(r["count"])).round(2)
    r.to_csv(TAB / "q2_ida_por_ano.csv")
    M["q2"] = {"media": r["mean"].to_dict(), "ic95": r["ic95"].to_dict()}
    w = a.pivot(index="ra", columns="ano", values="ida")
    for x, y in [(2022, 2023), (2023, 2024)]:
        t = w[[x, y]].dropna(); d = t[y] - t[x]
        M["q2"][f"delta_{x}_{y}"] = {"n": len(t), "media": round(d.mean(), 2), "p": float(stats.ttest_rel(t[y], t[x]).pvalue),
                                     "pct_caiu": round((d < -.5).mean() * 100, 1), "pct_subiu": round((d > .5).mean() * 100, 1)}
    # promovidos x não promovidos (2023 -> 2024)
    x = a.pivot(index="ra", columns="ano", values=["ida", "fase"])
    t = pd.DataFrame({"i23": x[("ida", 2023)], "i24": x[("ida", 2024)], "f23": x[("fase", 2023)], "f24": x[("fase", 2024)]}).dropna()
    t["d"] = t.i24 - t.i23; t["promovido"] = t.f24 > t.f23
    g = t.groupby("promovido").d.agg(["count", "mean"]).round(2)
    M["q2"]["promovido"] = {"n": int(g.loc[True, "count"]), "delta": float(g.loc[True, "mean"])}
    M["q2"]["nao_promovido"] = {"n": int(g.loc[False, "count"]), "delta": float(g.loc[False, "mean"])}
    pf = a.pivot_table(index="fase", columns="ano", values="ida", aggfunc="mean").round(2)
    pf.to_csv(TAB / "q2_ida_por_fase_ano.csv")

    fig, ax = plt.subplots(1, 3, figsize=(13, 4.1), gridspec_kw={"width_ratios": [.8, 1.5, .8]})
    ax[0].bar(r.index.astype(str), r["mean"], yerr=r["ic95"], color=[GRAY, TEAL, GRAY], width=.55, capsize=4, error_kw={"ecolor": NAVY})
    for i, val in enumerate(r["mean"]):
        ax[0].text(i, val / 2, br(val, 2), ha="center", color="white", fontweight="bold")
    ax[0].set_ylim(0, 8); ax[0].set_title("IDA médio (IC 95%)"); ax[0].grid(axis="x", visible=False)
    pal = {2022: GRAY, 2023: AMBER, 2024: TEAL}
    for y in (2022, 2023, 2024):
        ax[1].plot(pf.index, pf[y], marker="o", color=pal[y], lw=2.2, label=str(y))
    ax[1].set_xlabel("Fase (0 = Alfa)"); ax[1].set_title("IDA médio por fase"); ax[1].legend(frameon=False, ncol=3, loc="lower center")
    vals = [g.loc[True, "mean"], g.loc[False, "mean"]]
    ax[2].bar(["Promovidos\nde fase", "Mantidos\nna fase"], vals, color=[CORAL, TEAL], width=.55)
    ax[2].set_ylim(min(vals + [0]) - .18, max(vals + [0]) + .18)
    for i, val in enumerate(vals):
        va = "bottom" if val >= 0 else "top"
        ax[2].text(i, val + (.035 if val >= 0 else -.035), f"{'+' if val > 0 else ''}{br(val, 2)}", ha="center", va=va, fontweight="bold", color=NAVY)
    ax[2].axhline(0, color=NAVY, lw=1); ax[2].set_title("Δ IDA 2023→2024"); ax[2].grid(axis="x", visible=False)
    fig.tight_layout(); salva(fig, "q2_ida")


# ------------------------------------------------------------------ Q3 · IEG
def q3(a):
    cor = {}
    for y in (2022, 2023, 2024):
        d = a[a.ano == y]
        cor[y] = {"ieg_ida": round(d.ieg.corr(d.ida, method="spearman"), 2), "ieg_ipv": round(d.ieg.corr(d.ipv, method="spearman"), 2)}
    M["q3"] = {"spearman": cor}
    a = a.copy()
    a["faixa_ieg"] = pd.cut(a.ieg, [-.1, 6, 7.5, 8.5, 9.5, 10.1], labels=["< 6", "6–7,5", "7,5–8,5", "8,5–9,5", "≥ 9,5"])
    t = a.groupby("faixa_ieg", observed=True).agg(n=("ra", "count"), ida=("ida", "mean"), ipv=("ipv", "mean"), inde=("inde", "mean"),
                                                  pct_defasado=("em_defasagem", "mean")).round(2)
    t.to_csv(TAB / "q3_ieg_faixas.csv")
    M["q3"]["faixas"] = t.to_dict("index")
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.1))
    x = np.arange(len(t)); wd = .38
    ax[0].bar(x - wd / 2, t.ida, wd, color=TEAL, label="IDA"); ax[0].bar(x + wd / 2, t.ipv, wd, color=AMBER, label="IPV")
    for i, (u, w_) in enumerate(zip(t.ida, t.ipv)):
        ax[0].text(i - wd / 2, u + .1, br(u), ha="center", fontsize=9); ax[0].text(i + wd / 2, w_ + .1, br(w_), ha="center", fontsize=9)
    ax[0].set_xticks(x); ax[0].set_xticklabels(t.index); ax[0].set_xlabel("Faixa de IEG"); ax[0].set_ylim(0, 10)
    ax[0].set_title("Quanto maior o engajamento, maior IDA e IPV"); ax[0].legend(frameon=False, ncol=2); ax[0].grid(axis="x", visible=False)
    anos = [2022, 2023, 2024]
    ax[1].plot(anos, [cor[y]["ieg_ida"] for y in anos], marker="o", color=TEAL, lw=2.5, label="IEG × IDA")
    ax[1].plot(anos, [cor[y]["ieg_ipv"] for y in anos], marker="o", color=AMBER, lw=2.5, label="IEG × IPV")
    ax[1].set_ylim(0, .8); ax[1].set_xticks(anos); ax[1].set_ylabel("Correlação de Spearman"); ax[1].legend(frameon=False)
    ax[1].set_title("Relação estável nos três anos")
    fig.tight_layout(); salva(fig, "q3_engajamento")


# ------------------------------------------------------------------ Q4 · IAA
def q4(a):
    a = a.copy()
    a["gap"] = a.iaa - a.ida
    g = a.groupby("ano").agg(iaa=("iaa", "mean"), ida=("ida", "mean"), ieg=("ieg", "mean"), gap=("gap", "mean"),
                             superestima=("gap", lambda s: (s > 2).mean() * 100), subestima=("gap", lambda s: (s < -2).mean() * 100)).round(2)
    g.to_csv(TAB / "q4_autoavaliacao_por_ano.csv")
    cor = {y: {"iaa_ida": round(d.iaa.corr(d.ida, method="spearman"), 2), "iaa_ieg": round(d.iaa.corr(d.ieg, method="spearman"), 2)}
           for y, d in a.groupby("ano")}
    a["faixa_ida"] = pd.cut(a.ida, [-.1, 4, 6, 8, 10.1], labels=["< 4", "4–6", "6–8", "> 8"])
    f = a.groupby("faixa_ida", observed=True).agg(n=("ra", "count"), iaa=("iaa", "mean"), ida=("ida", "mean"),
                                                  iaa_alto=("iaa", lambda s: (s >= 8).mean() * 100)).round(2)
    f.to_csv(TAB / "q4_iaa_por_faixa_ida.csv")
    M["q4"] = {"por_ano": g.to_dict("index"), "spearman": cor, "faixa_ida": f.to_dict("index")}
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.1))
    x = np.arange(len(f)); wd = .38
    ax[0].bar(x - wd / 2, f.ida, wd, color=TEAL, label="IDA (real)"); ax[0].bar(x + wd / 2, f.iaa, wd, color=AMBER, label="IAA (autoavaliação)")
    for i, (u, w_) in enumerate(zip(f.ida, f.iaa)):
        ax[0].text(i - wd / 2, u + .1, br(u), ha="center", fontsize=9); ax[0].text(i + wd / 2, w_ + .1, br(w_), ha="center", fontsize=9)
    ax[0].set_xticks(x); ax[0].set_xticklabels(f.index); ax[0].set_xlabel("Faixa de IDA"); ax[0].set_ylim(0, 10.5)
    ax[0].set_title("Quem vai mal se avalia bem"); ax[0].legend(frameon=False, ncol=2, loc="upper left"); ax[0].grid(axis="x", visible=False)
    anos = [2022, 2023, 2024]
    ax[1].bar([str(y) for y in anos], g.gap, color=[TEAL, GRAY, TEAL], width=.5)
    for i, val in enumerate(g.gap):
        ax[1].text(i, val + .05, br(val, 2), ha="center", fontweight="bold")
    ax[1].set_title("Excesso de autoconfiança (IAA − IDA)"); ax[1].set_ylabel("pontos"); ax[1].grid(axis="x", visible=False)
    fig.tight_layout(); salva(fig, "q4_autoavaliacao")


# ------------------------------------------------------------------ Q5 · IPS
def q5(a, pares):
    a = a.copy()
    pr = pares.copy()
    pr["d_ida"] = pr.ida_prox - pr.ida
    pr["d_ieg"] = pr.ieg_prox - pr.ieg
    pr["queda_ida"] = (pr.d_ida < -1).astype(int)
    pr["queda_ieg"] = (pr.d_ieg < -1).astype(int)
    pr["faixa_ips"] = pd.cut(pr.ips, [-.1, 5, 7.45, 10.1], labels=["≤ 5", "5–7,4", "≥ 7,5"])
    t = pr.groupby(["ano_base", "faixa_ips"], observed=True).agg(n=("ra", "count"), queda_ida=("queda_ida", "mean"), queda_ieg=("queda_ieg", "mean")).mul([1, 100, 100]).round(1)
    t.to_csv(TAB / "q5_queda_por_faixa_ips.csv")
    rho = {int(y): {"ips_dida": round(d.ips.corr(d.d_ida, method="spearman"), 3), "ips_dieg": round(d.ips.corr(d.d_ieg, method="spearman"), 3)}
           for y, d in pr.groupby("ano_base")}
    # o que antecede as quedas? Spearman de cada indicador em t com a variação em t+1
    feat = ["ida", "ieg", "iaa", "ips", "ipv", "idade", "fase", "defasagem"]
    ant = pd.DataFrame({"queda_ida": [pr[c].corr(pr.d_ida, method="spearman") for c in feat],
                        "queda_ieg": [pr[c].corr(pr.d_ieg, method="spearman") for c in feat]}, index=feat).round(2)
    ant.to_csv(TAB / "q5_antecedentes_variacao.csv")
    from scipy.stats import chi2_contingency
    pq = {int(y): {"queda_ida": round(float(chi2_contingency(pd.crosstab(d.faixa_ips, d.queda_ida))[1]), 2),
                   "queda_ieg": round(float(chi2_contingency(pd.crosstab(d.faixa_ips, d.queda_ieg))[1]), 2)} for y, d in pr.groupby("ano_base")}
    ips = a.groupby("ano").ips.agg(mean="mean", pct_75=lambda s: (s.round(1) == 7.5).mean() * 100, pct_baixo=lambda s: (s < 2.6).mean() * 100).round(1)
    M["q5"] = {"p_qui2_faixa_ips": pq, "spearman_ips_variacao": rho, "antecedentes": ant.to_dict("index"), "ips_dist": ips.to_dict("index"),
               "queda_ida_pct": pr.groupby("ano_base").queda_ida.mean().mul(100).round(1).to_dict(),
               "queda_ieg_pct": pr.groupby("ano_base").queda_ieg.mean().mul(100).round(1).to_dict()}
    # queda de IPS entre anos x queda subsequente (2023→2024)
    w = a.pivot(index="ra", columns="ano", values=["ips", "ida", "ieg"])
    for x, y in [(2022, 2023), (2023, 2024)]:
        d = pd.DataFrame({"dips": w[("ips", y)] - w[("ips", x)], "dida": w[("ida", y)] - w[("ida", x)], "dieg": w[("ieg", y)] - w[("ieg", x)]}).dropna()
        M["q5"][f"dips_{x}_{y}"] = {"n": len(d), "rho_dida": round(d.dips.corr(d.dida, method="spearman"), 2), "rho_dieg": round(d.dips.corr(d.dieg, method="spearman"), 2)}

    fig, ax = plt.subplots(1, 3, figsize=(13.5, 4.1), gridspec_kw={"width_ratios": [1.1, 1.2, 1]})
    for y, c in [(2022, GRAY), (2023, AMBER), (2024, TEAL)]:
        d = a[a.ano == y].ips
        ax[0].hist(d, bins=np.arange(2.25, 10.5, .5), color=c, alpha=.6, label=str(y), density=True)
    ax[0].set_title("Distribuição do IPS por ano"); ax[0].set_xlabel("IPS"); ax[0].legend(frameon=False); ax[0].set_yticks([])
    tt = t.reset_index()
    for y, c in [(2022, GRAY), (2023, AMBER)]:
        s = tt[tt.ano_base == y]
        ax[1].plot(s.faixa_ips.astype(str), s.queda_ida, marker="o", color=c, lw=2.4, label=f"Base {y} → {y + 1}")
    ax[1].set_ylim(0, 60); ax[1].set_ylabel("% com queda de IDA > 1 ponto"); ax[1].set_xlabel("IPS no ano-base")
    ax[1].set_title("Queda de IDA por faixa de IPS: sem padrão"); ax[1].legend(frameon=False)
    ant2 = ant.loc[["ida", "idade", "fase", "ips", "ipv", "ieg"]]
    yy = np.arange(len(ant2)); ax[2].barh(yy - .2, ant2.queda_ida, .38, color=TEAL, label="Δ IDA"); ax[2].barh(yy + .2, ant2.queda_ieg, .38, color=AMBER, label="Δ IEG")
    ax[2].set_yticks(yy); ax[2].set_yticklabels([s.upper() if s not in ("idade", "fase") else s.capitalize() for s in ant2.index]); ax[2].axvline(0, color=NAVY, lw=1)
    ax[2].set_title("Correlação do indicador atual\ncom a variação no ano seguinte"); ax[2].legend(frameon=False, fontsize=9)
    ax[2].invert_yaxis(); ax[2].grid(axis="y", visible=False)
    fig.tight_layout(); salva(fig, "q5_ips")


# ------------------------------------------------------------------ Q6 · IPP x IAN
def q6(a):
    d = a[a.ipp.notna()].copy()
    t = d.groupby("nivel_defasagem", observed=True).agg(n=("ra", "count"), ipp=("ipp", "mean"), ida=("ida", "mean")).round(2)
    t.to_csv(TAB / "q6_ipp_por_nivel_defasagem.csv")
    alto = d.groupby("em_defasagem").apply(lambda x: pd.Series({"n": len(x), "ipp_medio": x.ipp.mean(), "pct_ipp_alto": (x.ipp >= 7.5).mean() * 100, "pct_ipp_baixo": (x.ipp < 6.5).mean() * 100}), include_groups=False).round(1)
    cor = {int(y): {"ipp_defasagem": round(x.ipp.corr(x.defasagem, method="spearman"), 2), "ipp_ida": round(x.ipp.corr(x.ida, method="spearman"), 2),
                    "ipp_ieg": round(x.ipp.corr(x.ieg, method="spearman"), 2), "ipp_ipv": round(x.ipp.corr(x.ipv, method="spearman"), 2)} for y, x in d.groupby("ano")}
    M["q6"] = {"por_nivel": t.to_dict("index"), "alto_baixo": alto.to_dict("index"), "spearman": cor}
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.1))
    ax[0].bar([s.split(" (")[0] for s in t.index], t.ipp, color=[COR_NIVEL[i] for i in t.index], width=.55)
    for i, val in enumerate(t.ipp):
        ax[0].text(i, val + .1, br(val, 2), ha="center", fontweight="bold")
    ax[0].set_ylim(0, 9); ax[0].set_title("IPP médio por nível de defasagem (IAN)"); ax[0].grid(axis="x", visible=False)
    for i, n_ in enumerate(t.n):
        ax[0].text(i, .4, f"n = {n_}", ha="center", color="white", fontsize=9)
    lab = ["Adequados\n(sem defasagem)", "Defasados"]
    x = np.arange(2); wd = .38
    ax[1].bar(x - wd / 2, [alto.loc[0.0, "pct_ipp_alto"], alto.loc[1.0, "pct_ipp_alto"]], wd, color=TEAL, label="IPP alto (≥ 7,5)")
    ax[1].bar(x + wd / 2, [alto.loc[0.0, "pct_ipp_baixo"], alto.loc[1.0, "pct_ipp_baixo"]], wd, color=CORAL, label="IPP baixo (< 6,5)")
    for i, (u, w_) in enumerate(zip([alto.loc[0.0, "pct_ipp_alto"], alto.loc[1.0, "pct_ipp_alto"]], [alto.loc[0.0, "pct_ipp_baixo"], alto.loc[1.0, "pct_ipp_baixo"]])):
        ax[1].text(i - wd / 2, u + 1, f"{br(u, 0)}%", ha="center", fontweight="bold"); ax[1].text(i + wd / 2, w_ + 1, f"{br(w_, 0)}%", ha="center", fontweight="bold")
    ax[1].set_xticks(x); ax[1].set_xticklabels(lab); ax[1].set_ylim(0, 90); ax[1].set_ylabel("% dos alunos"); ax[1].legend(frameon=False, fontsize=9)
    ax[1].set_title("60% dos defasados têm IPP alto"); ax[1].grid(axis="x", visible=False)
    fig.tight_layout(); salva(fig, "q6_ipp_ian")


# ------------------------------------------------------------------ Q7 · IPV
def q7(a):
    def z(s):
        return (s - s.mean()) / s.std()
    res = {}
    for y, feat in [(2022, ["ida", "ieg", "iaa", "ips"]), (2023, ["ida", "ieg", "iaa", "ips", "ipp"]), (2024, ["ida", "ieg", "iaa", "ips", "ipp"])]:
        d = a[a.ano == y].dropna(subset=feat + ["ipv"])
        X = np.column_stack([np.ones(len(d))] + [z(d[c]) for c in feat]); yv = z(d.ipv).values
        b = np.linalg.lstsq(X, yv, rcond=None)[0]
        r2 = 1 - ((yv - X @ b) ** 2).sum() / ((yv - yv.mean()) ** 2).sum()
        res[y] = {"beta": dict(zip(feat, b[1:].round(2))), "r2": round(r2, 2), "n": len(d)}
    w = a.pivot(index="ra", columns="ano", values=["ipv", "ida", "ieg", "iaa", "ips", "ipp"])
    dl = {}
    for x, y in [(2022, 2023), (2023, 2024)]:
        cols = ["ida", "ieg", "iaa", "ips"] + (["ipp"] if y == 2024 else [])
        d = pd.DataFrame({f"d_{c}": w[(c, y)] - w[(c, x)] for c in ["ipv"] + cols}).dropna()
        dl[f"{x}_{y}"] = {"n": len(d), **{k: round(d[k].corr(d.d_ipv, method="spearman"), 2) for k in d.columns if k != "d_ipv"}}
    x22 = a[a.ano == 2022]
    pv = x22.groupby("atingiu_pv").agg(n=("ra", "count"), ipv=("ipv", "mean"), ieg=("ieg", "mean"), ida=("ida", "mean")).round(2)
    M["q7"] = {"regressao_padronizada": res, "delta_spearman": dl, "atingiu_pv_2022": pv.to_dict("index")}
    pd.DataFrame({y: pd.Series(r["beta"]) for y, r in res.items()}).to_csv(TAB / "q7_betas_ipv.csv")
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.1), gridspec_kw={"width_ratios": [1.4, 1]})
    ind = ["ipp", "ida", "ieg", "ips", "iaa"]; x = np.arange(len(ind)); wd = .27
    for i, (y, c) in enumerate([(2022, GRAY), (2023, AMBER), (2024, TEAL)]):
        vals = [res[y]["beta"].get(k, np.nan) for k in ind]
        ax[0].bar(x + (i - 1) * wd, vals, wd, color=c, label=f"{y} (R² = {br(res[y]['r2'], 2)})")
    ax[0].set_xticks(x); ax[0].set_xticklabels([k.upper() for k in ind]); ax[0].axhline(0, color=NAVY, lw=1)
    ax[0].set_ylabel("Coeficiente padronizado"); ax[0].set_title("O que explica o IPV (regressão padronizada)"); ax[0].legend(frameon=False, fontsize=9)
    ax[0].grid(axis="x", visible=False); ax[0].text(0 - wd, .02, "sem IPP\nem 2022", ha="center", fontsize=8, color=GRAY)
    ax[1].bar(["Não atingiram\nponto de virada", "Atingiram\nponto de virada"], [pv.loc["Não", "ida"], pv.loc["Sim", "ida"]], color=[GRAY, TEAL], width=.5, label="IDA")
    ax[1].set_title("2022: quem virou tinha IDA maior"); ax[1].set_ylim(0, 10)
    for i, (idx, col) in enumerate([("Não", GRAY), ("Sim", TEAL)]):
        ax[1].text(i, pv.loc[idx, "ida"] / 2, f"IDA {br(pv.loc[idx, 'ida'])}\nIEG {br(pv.loc[idx, 'ieg'])}", ha="center", color="white", fontweight="bold")
    ax[1].grid(axis="x", visible=False)
    fig.tight_layout(); salva(fig, "q7_ipv")


# ------------------------------------------------------------------ Q8 · INDE
def q8(a):
    w = a[(a.ano >= 2023) & a.inde.notna()].copy()
    pesos = {"ian": .1, "ida": .2, "ieg": .2, "iaa": .1, "ips": .1, "ipp": .1, "ipv": .2}
    top = w[w.pedra == "Topázio"][list(pesos)].mean(); low = w[w.pedra.isin(["Quartzo", "Ágata"])][list(pesos)].mean()
    contrib = pd.DataFrame({"topazio": top, "quartzo_agata": low, "diferenca": top - low, "peso": pd.Series(pesos)})
    contrib["contribuicao_inde"] = contrib.diferenca * contrib.peso
    contrib.round(2).to_csv(TAB / "q8_contribuicao_topazio_vs_quartzo_agata.csv")
    w["n_fortes"] = (w[["ida", "ieg", "ipv", "ipp"]] >= 8).sum(axis=1)
    nf = w.groupby("n_fortes").agg(n=("ra", "count"), inde=("inde", "mean"), pct_topazio=("pedra", lambda s: (s == "Topázio").mean() * 100)).round(1)
    nf.to_csv(TAB / "q8_indicadores_fortes.csv")
    import itertools
    linhas = []
    for k in (1, 2, 3):
        for comb in itertools.combinations(["ida", "ieg", "ipv", "ipp"], k):
            resto = [c for c in ["ida", "ieg", "ipv", "ipp"] if c not in comb]
            m = (w[list(comb)] >= 8).all(axis=1) & (w[resto] < 8).all(axis=1)
            linhas.append({"combinacao": " + ".join(c.upper() for c in comb), "n": int(m.sum()), "inde": w[m].inde.mean(), "pct_topazio": (w[m].pedra == "Topázio").mean() * 100})
    cb = pd.DataFrame(linhas).sort_values("inde", ascending=False).round(2)
    cb.to_csv(TAB / "q8_combinacoes.csv", index=False)
    M["q8"] = {"formula": pesos, "contribuicao": contrib.round(2).to_dict("index"), "n_fortes": nf.to_dict("index"),
               "combos_top": cb[cb.n >= 40].head(4).to_dict("records"), "ieg_sozinho": cb[cb.combinacao == "IEG"].iloc[0].to_dict()}
    fig, ax = plt.subplots(1, 2, figsize=(11.5, 4.2), gridspec_kw={"width_ratios": [1, 1.1]})
    c = contrib.sort_values("contribuicao_inde")
    ax[0].barh([s.upper() for s in c.index], c.contribuicao_inde, color=[AMBER if s in ("ida", "ieg", "ipv") else GRAY for s in c.index])
    for i, val in enumerate(c.contribuicao_inde):
        ax[0].text(val + .01, i, br(val, 2), va="center", fontsize=9)
    ax[0].set_title("Quanto cada indicador explica da\ndistância Topázio × (Quartzo+Ágata)"); ax[0].set_xlabel("pontos de INDE"); ax[0].grid(axis="y", visible=False)
    ax[1].bar(nf.index.astype(str), nf.inde, color=TEAL, width=.6)
    ax2 = ax[1].twinx(); ax2.plot(nf.index.astype(str), nf.pct_topazio, color=AMBER, marker="o", lw=3); ax2.set_ylim(0, 100); ax2.spines["right"].set_visible(True); ax2.grid(False)
    ax2.set_ylabel("% Topázio", color=AMBER)
    for i, (u, w_) in enumerate(zip(nf.inde, nf.pct_topazio)):
        ax[1].text(i, u / 2, br(u), ha="center", color="white", fontweight="bold"); ax2.text(i, w_ + 4, f"{br(w_, 0)}%", ha="center", color=AMBER, fontweight="bold", fontsize=9)
    ax[1].set_ylim(0, 10); ax[1].set_xlabel("Nº de indicadores ≥ 8 entre IDA, IEG, IPV e IPP"); ax[1].set_ylabel("INDE médio")
    ax[1].set_title("Indicadores fortes se somam"); ax[1].grid(axis="x", visible=False)
    fig.tight_layout(); salva(fig, "q8_inde")


# ------------------------------------------------------------------ Q10 · Efetividade
def q10(v, a):
    ord_ = {"Quartzo": 1, "Ágata": 2, "Ametista": 3, "Topázio": 4}
    dist = (pd.crosstab(a[a.inde.notna()].ano, a[a.inde.notna()].pedra, normalize="index") * 100)[ORDEM_PEDRA].round(1)
    dist.to_csv(TAB / "q10_pedra_por_ano.csv")
    inde_ano = a.groupby("ano").inde.mean().round(2)
    pi = a.pivot(index="ra", columns="ano", values="inde")
    coorte = {}
    for x, y in [(2022, 2023), (2023, 2024), (2022, 2024)]:
        t = pi[[x, y]].dropna()
        coorte[f"{x}_{y}"] = {"n": len(t), "inde_ini": round(t[x].mean(), 2), "inde_fim": round(t[y].mean(), 2), "pct_subiu": round((t[y] > t[x]).mean() * 100, 1)}
    pp = a[a.pedra.notna()].pivot(index="ra", columns="ano", values="pedra").map(lambda s: ord_.get(s, np.nan))
    trans = {}
    for x, y in [(2022, 2023), (2023, 2024)]:
        t = pp[[x, y]].dropna(); d = t[y] - t[x]
        trans[f"{x}_{y}"] = {"n": len(t), "sobe": round((d > 0).mean() * 100, 1), "igual": round((d == 0).mean() * 100, 1), "desce": round((d < 0).mean() * 100, 1)}
    t = pp[[2023, 2024]].dropna().astype(int)
    inv = {v_: k for k, v_ in ord_.items()}
    mat = (pd.crosstab(t[2023].map(inv), t[2024].map(inv), normalize="index") * 100).reindex(index=ORDEM_PEDRA, columns=ORDEM_PEDRA).round(0)
    mat.to_csv(TAB / "q10_transicao_pedra_2023_2024.csv")
    # variação do INDE por pedra inicial (regressão à média)
    t2 = a.pivot(index="ra", columns="ano", values=["inde", "pedra"])
    tt = pd.DataFrame({"i0": t2[("inde", 2023)], "i1": t2[("inde", 2024)], "p0": t2[("pedra", 2023)]}).dropna()
    tt["d"] = tt.i1 - tt.i0
    dp = tt.groupby("p0").d.agg(["count", "mean"]).reindex(ORDEM_PEDRA).round(2)
    dp.to_csv(TAB / "q10_delta_inde_por_pedra_inicial.csv")
    # por fase (mesmos alunos)
    tf = a.pivot(index="ra", columns="ano", values=["inde", "fase", "defasagem"])
    fase_t = pd.DataFrame({"fase": tf[("fase", 2023)], "d_inde": tf[("inde", 2024)] - tf[("inde", 2023)], "d_defas": tf[("defasagem", 2024)] - tf[("defasagem", 2023)]}).dropna()
    df = fase_t.groupby("fase").agg(n=("d_inde", "count"), d_inde=("d_inde", "mean"), d_defas=("d_defas", "mean")).round(2)
    df.to_csv(TAB / "q10_delta_por_fase_2023_2024.csv")
    # ganho em defasagem x INDE
    wd = v.pivot(index="ra", columns="ano", values="defasagem")
    ganho_def = {f"{x}_{y}": round((wd[y] - wd[x]).dropna().mean(), 2) for x, y in [(2022, 2023), (2023, 2024)]}
    M["q10"] = {"pedra_pct": dist.to_dict("index"), "inde_medio": inde_ano.to_dict(), "coorte": coorte, "transicao": trans,
                "delta_por_pedra_inicial": dp.to_dict("index"), "delta_por_fase": df.to_dict("index"), "ganho_defasagem_medio": ganho_def}
    fig, ax = plt.subplots(1, 3, figsize=(14, 4.2), gridspec_kw={"width_ratios": [1, 1, 1]})
    b = np.zeros(len(dist))
    for pdr in ORDEM_PEDRA:
        ax[0].bar(dist.index.astype(str), dist[pdr], bottom=b, color=COR_PEDRA[pdr], label=pdr, width=.6)
        for i, val in enumerate(dist[pdr]):
            ax[0].text(i, b[i] + val / 2, f"{br(val, 0)}%", ha="center", va="center", color="white" if pdr in ("Ametista", "Ágata") else NAVY, fontsize=9, fontweight="bold")
        b += dist[pdr].values
    ax[0].set_title("Pedras da população, por ano"); ax[0].legend(frameon=False, fontsize=8, ncol=4, loc="upper center", bbox_to_anchor=(.5, -.08)); ax[0].grid(axis="x", visible=False)
    ax[1].plot(["2022", "2023", "2024"], inde_ano.values, marker="o", color=GRAY, lw=2.4, ls="--", label="População do ano")
    ic = [pi[2022].dropna().pipe(lambda s: s.mean())]
    c22_23 = coorte["2022_2023"]; c23_24 = coorte["2023_2024"]
    ax[1].plot(["2022", "2023"], [c22_23["inde_ini"], c22_23["inde_fim"]], marker="o", color=AMBER, lw=3, label="Mesmos alunos 22→23")
    ax[1].plot(["2023", "2024"], [c23_24["inde_ini"], c23_24["inde_fim"]], marker="o", color=TEAL, lw=3, label="Mesmos alunos 23→24")
    ax[1].set_ylim(6.8, 7.7); ax[1].set_title("INDE: população cresce,\nmesmos alunos ficam estáveis"); ax[1].set_ylabel("INDE médio"); ax[1].legend(frameon=False, fontsize=8, loc="upper left")
    im = ax[2].imshow(mat.values, cmap="YlGnBu", vmin=0, vmax=80)
    ax[2].set_xticks(range(4)); ax[2].set_xticklabels(ORDEM_PEDRA, fontsize=9); ax[2].set_yticks(range(4)); ax[2].set_yticklabels(ORDEM_PEDRA, fontsize=9)
    for i in range(4):
        for j in range(4):
            ax[2].text(j, i, f"{br(mat.values[i, j], 0)}%", ha="center", va="center", color="white" if mat.values[i, j] > 45 else NAVY, fontweight="bold")
    ax[2].set_xlabel("Pedra 2024"); ax[2].set_ylabel("Pedra 2023"); ax[2].set_title("Para onde vão os alunos (23→24)"); ax[2].grid(False)
    fig.tight_layout(); salva(fig, "q10_efetividade")


# ------------------------------------------------------------------ Q11 · Extras
def q11(p, v, a):
    ret = {}
    for x, y in [(2022, 2023), (2023, 2024)]:
        d = v[v.ano == x].copy(); d["ficou"] = d.ra.isin(set(v[v.ano == y].ra)).astype(int)
        d["faixa_ieg"] = pd.cut(d.ieg, [-.1, 7, 8.5, 10.1], labels=["IEG < 7", "IEG 7–8,5", "IEG > 8,5"])
        ret[f"{x}_{y}"] = {"retencao": round(d.ficou.mean() * 100, 1), "n": len(d),
                           "por_ieg": d.groupby("faixa_ieg", observed=True).ficou.mean().mul(100).round(1).to_dict(),
                           "por_instituicao": d.groupby("instituicao").ficou.mean().mul(100).round(1).to_dict()}
    inst = v.groupby(["ano", "instituicao"]).agg(n=("ra", "count"), pct_defasado=("em_defasagem", "mean"), inde=("inde", "mean")).round(2)
    inst["pct_defasado"] *= 100
    inst.to_csv(TAB / "q11_instituicao.csv")
    esc = pd.read_excel(RAIZ / "data/raw/BASE_DE_DADOS_PEDE_2024_-_DATATHON.xlsx", sheet_name="PEDE2024")[["RA", "Escola"]]
    e = v[v.ano == 2024].merge(esc, left_on="ra", right_on="RA").groupby("Escola").agg(n=("ra", "count"), pct_defasado=("em_defasagem", "mean"), inde=("inde", "mean"), ida=("ida", "mean")).round(2)
    e["pct_defasado"] = (e.pct_defasado * 100).round(1)
    e = e[e.n >= 25].sort_values("pct_defasado"); e.to_csv(TAB / "q11_escolas_2024.csv")
    idade = v.assign(idade_rel=v.idade - (v.fase + 7)).groupby("ano").apply(lambda d: d.idade_rel.corr(d.defasagem), include_groups=False).round(2)
    gen = v.groupby(["ano", "genero"]).em_defasagem.mean().mul(100).round(1).unstack()
    M["q11"] = {"retencao": ret, "instituicao": inst.reset_index().to_dict("records"), "escolas_min": e.head(1).reset_index().to_dict("records"),
                "escolas_max": e.tail(1).reset_index().to_dict("records"), "corr_idade_relativa_defasagem": idade.to_dict(), "genero_pct_defasado": gen.to_dict("index"),
                "qualidade": {"formados_sem_avaliacao_2024": int(p.formado.sum()), "sem_indicadores": p[~p.formado].groupby("ano").sem_indicadores.sum().astype(int).to_dict(),
                              "idade_2023_corrompida": 399}}
    fig, ax = plt.subplots(1, 3, figsize=(14, 4.1), gridspec_kw={"width_ratios": [1.1, 1.1, 1.2]})
    r = pd.DataFrame(ret["2023_2024"]["por_ieg"], index=["ret"]).T["ret"]; r0 = pd.DataFrame(ret["2022_2023"]["por_ieg"], index=["ret"]).T["ret"]
    x = np.arange(3); wd = .38
    ax[0].bar(x - wd / 2, r0.values, wd, color=GRAY, label="2022→2023"); ax[0].bar(x + wd / 2, r.values, wd, color=TEAL, label="2023→2024")
    for i, (u, w_) in enumerate(zip(r0.values, r.values)):
        ax[0].text(i - wd / 2, u + 1, f"{br(u, 0)}%", ha="center", fontsize=9); ax[0].text(i + wd / 2, w_ + 1, f"{br(w_, 0)}%", ha="center", fontsize=9)
    ax[0].set_xticks(x); ax[0].set_xticklabels(r.index); ax[0].set_ylim(0, 100); ax[0].set_ylabel("% que reaparece no ano seguinte")
    ax[0].set_title("Engajamento baixo antecede saída"); ax[0].legend(frameon=False, fontsize=9, loc="lower right"); ax[0].grid(axis="x", visible=False)
    ii = inst.reset_index(); ii = ii[ii.instituicao.isin(["Pública", "Privada / bolsa"])]
    for nome, c in [("Pública", GRAY), ("Privada / bolsa", TEAL)]:
        s = ii[ii.instituicao == nome]; ax[1].plot(s.ano.astype(str), s.pct_defasado, marker="o", color=c, lw=3, label=nome)
        for _, row in s.iterrows():
            ax[1].text(str(int(row.ano)), row.pct_defasado + 3, f"{br(row.pct_defasado, 0)}%", ha="center", color=c, fontweight="bold", fontsize=9)
    ax[1].set_ylim(0, 90); ax[1].set_ylabel("% em defasagem"); ax[1].set_title("Defasagem: escola pública × privada/bolsa"); ax[1].legend(frameon=False)
    ee = e.copy(); ee = ee[ee.inde.notna()]
    ax[2].scatter(ee.pct_defasado, ee.ida, s=ee.n * 3, color=TEAL, alpha=.75, edgecolor="white")
    ax[2].set_xlabel("% de alunos em defasagem (2024)"); ax[2].set_ylabel("IDA médio")
    ax[2].set_title("Escolas de origem (2024, n ≥ 25)")
    for nm, row in ee.iterrows():
        if row.pct_defasado < 30 or row.ida < 5.0:
            ax[2].annotate(nm.replace("Colégio ", "").replace("EE ", "")[:22], (row.pct_defasado, row.ida), fontsize=8, xytext=(6, 4), textcoords="offset points")
    fig.tight_layout(); salva(fig, "q11_extras")


def main():
    p, v, a, pares = carrega()
    q1(v); q2(a); q3(a); q4(a); q5(a, pares); q6(a); q7(a); q8(a); q10(v, a); q11(p, v, a)
    meta = RAIZ / "models/metadata.json"
    if meta.exists():
        M["q9"] = json.loads(meta.read_text())
    (RAIZ / "reports/metricas_chave.json").write_text(json.dumps(M, ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    print("ok: figuras em", FIG)


if __name__ == "__main__":
    main()

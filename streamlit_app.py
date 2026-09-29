"""
App Streamlit · Radar de Risco de Defasagem (Passos Mágicos)

Estima a probabilidade de um aluno estar EM DEFASAGEM no ano seguinte a partir dos indicadores
do ano corrente. Ferramenta de apoio à priorização; não substitui a avaliação da equipe.

Execução local:  streamlit run app/streamlit_app.py
"""
import io
import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from src.features import FEATURES, faixa_risco, prepara_features  # noqa: E402

st.set_page_config(page_title="Radar de Risco · Passos Mágicos", page_icon="🧭", layout="wide")

COR = {"Baixo": "#0E7C86", "Médio": "#F2A900", "Alto": "#D1495B"}
ACAO = {
    "Alto": "Priorizar no acompanhamento: revisar o plano individual, alinhar com o responsável e conectar psicopedagogia e reforço nas disciplinas com menor nota.",
    "Médio": "Monitorar de perto: acompanhar IDA e IEG a cada bimestre e antecipar o reforço se algum indicador cair.",
    "Baixo": "Manter a rotina atual e continuar acompanhando os indicadores no ciclo seguinte.",
}
FASES = {0: "Alfa", 1: "Fase 1", 2: "Fase 2", 3: "Fase 3", 4: "Fase 4", 5: "Fase 5", 6: "Fase 6", 7: "Fase 7", 8: "Fase 8 (universitários)"}


# --------------------------------------------------------------------------- modelo
@st.cache_resource(show_spinner="Carregando modelo…")
def carrega_modelo():
    meta = json.loads((RAIZ / "models/metadata.json").read_text())
    try:
        return joblib.load(RAIZ / "models/modelo_risco.joblib"), meta
    except Exception:  # versão do scikit-learn diferente da usada no treino: re-treina em segundos
        from src.treino import treina_modelo
        pares = pd.read_csv(RAIZ / "data/processed/pares_modelo.csv")
        return treina_modelo(pares, meta["hiperparametros"]), meta


modelo, meta = carrega_modelo()


def prevê(df: pd.DataFrame) -> np.ndarray:
    return modelo.predict_proba(prepara_features(df))[:, 1]


def badge(faixa: str, p: float) -> str:
    return (f"<div style='background:{COR[faixa]};color:white;padding:18px 22px;border-radius:14px'>"
            f"<div style='font-size:14px;opacity:.9'>Probabilidade de defasagem no próximo ano</div>"
            f"<div style='font-size:44px;font-weight:800;line-height:1.1'>{p:.0%}</div>"
            f"<div style='font-size:18px;font-weight:600'>Risco {faixa.upper()}</div></div>")


def parse_fase(v):
    s = str(v).strip().upper()
    if s.startswith("ALFA"):
        return 0
    digs = [c for c in s if c.isdigit()]
    return int(digs[0]) if digs else np.nan


# --------------------------------------------------------------------------- layout
st.title("🧭 Radar de Risco de Defasagem")
st.caption("Associação Passos Mágicos · estima a chance de o aluno estar defasado no **próximo ano** para priorizar o acompanhamento.")

with st.sidebar:
    st.header("Sobre a ferramenta")
    m = meta["metricas_teste"]
    st.metric("AUC no teste", f"{m['auc']:.2f}")
    st.metric("AUC em validação temporal", f"{meta['validacao_temporal_auc']:.2f}")
    st.caption(f"Treinado com {meta['n_pares']:,} pares aluno-ano (2022→2023 e 2023→2024) de {meta['n_alunos']} alunos.".replace(",", "."))
    st.info("Apoio à decisão. O modelo indica **associações** nos dados históricos, não causas, e não deve ser usado para excluir ou rotular alunos.")

tab1, tab2, tab3 = st.tabs(["👤 Aluno individual", "📄 Vários alunos (planilha)", "📊 Sobre o modelo"])

# --------------------------------------------------------------------------- aba 1
with tab1:
    c1, c2 = st.columns([1.1, 1])
    with c1:
        st.subheader("Dados do aluno no ano atual")
        a, b, c = st.columns(3)
        fase = a.selectbox("Fase atual", list(FASES), format_func=FASES.get, index=3)
        idade = b.number_input("Idade", 6, 30, 13)
        defas = c.slider("Defasagem atual", -5, 3, 0, help="Fase do aluno menos a fase ideal para sua série. 0 = adequado; −1 = uma fase atrás.")
        st.markdown("**Indicadores (0 a 10)**")
        d, e, f = st.columns(3)
        ida = d.slider("IDA · desempenho acadêmico", 0.0, 10.0, 6.5, .1)
        ieg = e.slider("IEG · engajamento", 0.0, 10.0, 8.0, .1)
        ipv = f.slider("IPV · ponto de virada", 0.0, 10.0, 7.5, .1)
        g, h, i = st.columns(3)
        iaa = g.slider("IAA · autoavaliação", 0.0, 10.0, 8.0, .1)
        ips = h.slider("IPS · psicossocial", 0.0, 10.0, 7.5, .1)
        tem_ipp = i.checkbox("Tenho o IPP", value=True, help="Sem o IPP o modelo continua funcionando, com precisão ligeiramente menor.")
        ipp = i.slider("IPP · psicopedagógico", 0.0, 10.0, 7.5, .1, disabled=not tem_ipp)

    aluno = pd.DataFrame([{"ida": ida, "ieg": ieg, "iaa": iaa, "ips": ips, "ipv": ipv, "ipp": ipp if tem_ipp else np.nan,
                           "defasagem": defas, "fase": fase, "idade": idade}])
    p = float(prevê(aluno)[0])
    faixa = faixa_risco(p)

    with c2:
        st.subheader("Resultado")
        st.markdown(badge(faixa, p), unsafe_allow_html=True)
        st.progress(min(p, 1.0))
        st.write(ACAO[faixa])
        obs = meta["faixas_risco"][faixa]["taxa_real_defasagem"]
        st.caption(f"Nos dados de teste, {obs:.0%} dos alunos classificados em risco **{faixa.lower()}** estavam de fato defasados no ano seguinte.")
        idade_rel = idade - (fase + 7)
        if idade_rel >= 2:
            st.warning(f"Aluno {idade_rel} ano(s) mais velho que o esperado para a fase: fator que pesa fortemente no risco.")

        st.markdown("**E se um indicador melhorasse 1 ponto?** (simulação, mantendo o resto igual)")
        linhas = []
        for k, nome in [("ida", "IDA"), ("ieg", "IEG"), ("ipv", "IPV"), ("ips", "IPS"), ("iaa", "IAA"), ("ipp", "IPP")]:
            if k == "ipp" and not tem_ipp:
                continue
            alt = aluno.copy(); alt[k] = min(float(alt[k].iloc[0]) + 1, 10.0)
            linhas.append({"Indicador": nome, "Variação da probabilidade (pontos percentuais)": (float(prevê(alt)[0]) - p) * 100})
        sim = pd.DataFrame(linhas).set_index("Indicador")
        st.bar_chart(sim, color="#0E7C86", height=220)
        st.caption("Simulação associativa: mostra como o modelo reage, não promete que a intervenção terá esse efeito.")

# --------------------------------------------------------------------------- aba 2
with tab2:
    st.subheader("Classificar uma turma ou lista de alunos")
    st.write("Envie um CSV ou Excel com as colunas abaixo (uma linha por aluno, dados do ano atual). O IPP pode ficar vazio.")
    modelo_csv = pd.DataFrame({"ra": ["RA-1", "RA-2"], "fase": [3, 5], "idade": [13, 16], "defasagem": [0, -2], "ida": [6.5, 4.2], "ieg": [8.1, 6.0],
                               "iaa": [8.0, 8.5], "ips": [7.5, 6.3], "ipv": [7.4, 6.1], "ipp": [7.6, None]})
    st.download_button("⬇️ Baixar planilha modelo", modelo_csv.to_csv(index=False).encode("utf-8"), "modelo_alunos.csv", "text/csv")
    up = st.file_uploader("Planilha de alunos", type=["csv", "xlsx"])
    if up is not None:
        try:
            df = pd.read_csv(up) if up.name.lower().endswith(".csv") else pd.read_excel(up)
        except Exception as ex:
            st.error(f"Não consegui ler o arquivo: {ex}"); st.stop()
        df.columns = [str(c).strip().lower() for c in df.columns]
        obrig = ["fase", "idade", "defasagem", "ida", "ieg", "iaa", "ips", "ipv"]
        falta = [c for c in obrig if c not in df.columns]
        if falta:
            st.error(f"Faltam colunas: {', '.join(falta)}. Use a planilha modelo.")
        else:
            work = df.copy()
            work["fase"] = work["fase"].map(parse_fase)
            for c in obrig[1:] + ["ipp"]:
                work[c] = pd.to_numeric(work.get(c, np.nan), errors="coerce")
            valido = work[obrig].notna().all(axis=1)
            res = df.copy()
            res["prob_defasagem"] = np.nan; res["faixa_risco"] = "dados insuficientes"
            if valido.any():
                pr = prevê(work[valido])
                res.loc[valido, "prob_defasagem"] = pr
                res.loc[valido, "faixa_risco"] = [faixa_risco(x) for x in pr]
            res = res.sort_values("prob_defasagem", ascending=False, na_position="last")
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Alunos", len(res))
            for kk, fx in zip((k2, k3, k4), ("Alto", "Médio", "Baixo")):
                kk.metric(f"Risco {fx.lower()}", int((res.faixa_risco == fx).sum()))
            if (~valido).any():
                st.warning(f"{int((~valido).sum())} linha(s) sem todos os campos obrigatórios foram marcadas como 'dados insuficientes'.")
            st.dataframe(res.style.format({"prob_defasagem": "{:.0%}"}, na_rep="—"), use_container_width=True, hide_index=True)
            buf = io.BytesIO(); res.to_excel(buf, index=False)
            st.download_button("⬇️ Baixar resultado (Excel)", buf.getvalue(), "risco_alunos.xlsx",
                               "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# --------------------------------------------------------------------------- aba 3
with tab3:
    st.subheader("Como o modelo foi construído")
    st.markdown(f"""
- **Pergunta:** o aluno estará em defasagem (fase abaixo da ideal) no ano seguinte?
- **Dados:** {meta['n_pares']:,} pares aluno-ano (2022→2023 e 2023→2024) — {meta['n_alunos']} alunos.
- **Modelo:** gradient boosting com probabilidades calibradas; separação treino/teste **por aluno** para evitar vazamento.
- **Variáveis:** IDA, IEG, IAA, IPS, IPV, IPP, defasagem atual, fase, idade, idade relativa à fase e excesso de autoconfiança (IAA − IDA).
""".replace(",", "."))
    m = meta["metricas_teste"]; b = meta["baseline_persistencia"]
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("AUC (teste)", f"{m['auc']:.2f}", f"+{m['auc'] - b['auc']:.2f} vs. regra 'continua defasado'")
    k2.metric("AUC temporal (treina 22→23, testa 23→24)", f"{meta['validacao_temporal_auc']:.2f}")
    k3.metric("Precisão (limiar 50%)", f"{m['precisao_limiar_050']:.0%}")
    k4.metric("Recall (limiar 50%)", f"{m['recall_limiar_050']:.0%}")
    st.markdown("**As faixas de risco são confiáveis?** Taxa de alunos realmente defasados, por faixa (dados de teste):")
    fx = pd.DataFrame(meta["faixas_risco"]).T.rename(columns={"alunos": "Alunos", "prob_media_prevista": "Prob. média prevista", "taxa_real_defasagem": "Taxa real"})
    st.dataframe(fx.style.format({"Alunos": "{:.0f}", "Prob. média prevista": "{:.0%}", "Taxa real": "{:.0%}"}), use_container_width=True)
    ad = meta["adequados_hoje"]
    st.success(f"Entre alunos **hoje adequados**, {ad['taxa_entram_defasagem']:.0%} entram em defasagem no ano seguinte. Acompanhando os 30% de maior risco, "
               f"a equipe alcança **{ad['captura_top30']:.0%}** desses casos.")
    st.markdown("**O que mais pesa (importância por permutação)**")
    imp = pd.Series(meta["importancia_permutacao"]).sort_values(ascending=False).clip(lower=0)
    st.bar_chart(imp, color="#F2A900", height=260)
    st.markdown("""
**Limitações**
- Fase, idade e defasagem atual explicam boa parte do risco (defasagem é persistente); os indicadores acrescentam poder além disso.
- Só há dois pares de anos e alunos que saíram do programa não aparecem no ano seguinte.
- O IPS de 2023 tem comportamento atípico (28% dos alunos com valor mínimo), o que pode afetar o aprendizado sobre esse indicador.
- Use como **priorização**, junto com o conhecimento da equipe sobre cada aluno.
""")

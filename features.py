"""
Feature engineering do modelo de risco de defasagem.

Único ponto de verdade: o notebook, o script de treino e o app Streamlit importam daqui,
o que evita divergência entre o que foi treinado e o que é servido.

Unidade de análise: um aluno em um ano t (indicadores conhecidos em t).
Alvo: o aluno estará EM DEFASAGEM (fase < fase ideal, IAN < 10) no ano t+1.
"""
import numpy as np
import pandas as pd

# indicadores e atributos do aluno no ano-base
BASE = ["ida", "ieg", "iaa", "ips", "ipv", "ipp", "defasagem", "fase", "idade"]
# variáveis construídas
ENGENHARIA = ["idade_relativa", "gap_autoaval"]
FEATURES = BASE + ENGENHARIA

ALVO = "em_defasagem_prox"
FAIXAS_RISCO = {"Baixo": (0.0, 0.35), "Médio": (0.35, 0.65), "Alto": (0.65, 1.01)}


def prepara_features(df: pd.DataFrame) -> pd.DataFrame:
    """Recebe colunas BASE (IPP pode faltar/NaN) e devolve a matriz de features do modelo."""
    x = pd.DataFrame(index=df.index)
    for c in BASE:
        x[c] = pd.to_numeric(df[c], errors="coerce") if c in df else np.nan
    # idade em relação à esperada para a fase (Alfa ≈ 7 anos; +1 ano por fase):
    # positivo = mais velho que o esperado, o que já é sinal de atraso escolar
    x["idade_relativa"] = x["idade"] - (x["fase"] + 7)
    # excesso de autoconfiança: quanto o aluno se avalia acima do desempenho real (IAA − IDA)
    x["gap_autoaval"] = x["iaa"] - x["ida"]
    return x[FEATURES]


def faixa_risco(p: float) -> str:
    for nome, (lo, hi) in FAIXAS_RISCO.items():
        if lo <= p < hi:
            return nome
    return "Alto"

"""
Treino do modelo final de risco de defasagem (mesma receita do notebook, seção 8).

Uso:  python treino.py
Também é chamado pelo app Streamlit como plano B, caso o .joblib salvo seja incompatível
com a versão do scikit-learn do ambiente de deploy.
"""
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import StratifiedGroupKFold

from features import ALVO, prepara_features

RAIZ = Path(__file__).resolve().parent
SEED = 42


def treina_modelo(pares: pd.DataFrame, params: dict):
    X, y, g = prepara_features(pares), pares[ALVO].astype(int), pares.ra
    splits = list(StratifiedGroupKFold(5, shuffle=True, random_state=21).split(X, y, g))
    base = HistGradientBoostingClassifier(random_state=SEED, **params)
    return CalibratedClassifierCV(base, method="sigmoid", cv=splits).fit(X, y)


if __name__ == "__main__":
    meta = json.loads((RAIZ / "metadata.json").read_text())
    pares = pd.read_csv(RAIZ / "pares_modelo.csv")
    joblib.dump(treina_modelo(pares, meta["hiperparametros"]), RAIZ / "modelo_risco.joblib")
    print("modelo salvo em modelo_risco.joblib")

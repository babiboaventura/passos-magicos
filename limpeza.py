"""
Limpeza e harmonização da base PEDE (Passos Mágicos) 2022-2024.

Entrada : data/raw/BASE_DE_DADOS_PEDE_2024_-_DATATHON.xlsx (abas PEDE2022, PEDE2023, PEDE2024)
Saída   : data/processed/painel_alunos.csv  (1 linha por aluno-ano, esquema único)
          data/processed/pares_modelo.csv    (aluno em t -> situação em t+1, usado no modelo)

Problemas tratados (ver README):
  * Nomes de colunas diferentes entre as abas (Defas x Defasagem, Matem x Mat, ...).
  * 2022 traz Fase como número, 2023 como 'FASE 3' e 2024 traz a TURMA ('3A') na coluna Fase.
  * 2023: Idade corrompida (datas 1900-01-xx = serial do Excel) em 399 linhas.
  * Pedra escrita 'Agata' / 'Ágata'; 2024 traz placeholders 'INCLUIR' (38 formados sem avaliação).
  * Instituição de ensino com categorias diferentes por ano -> tipo padronizado.
  * IPP não existe em 2022; Indicado / Atingiu PV só existem em 2022.
"""
import datetime as dt
import re
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
ARQ = RAIZ / "data/raw/BASE_DE_DADOS_PEDE_2024_-_DATATHON.xlsx"
SAIDA = RAIZ / "data/processed"
SAIDA.mkdir(parents=True, exist_ok=True)

INDICADORES = ["ian", "ida", "ieg", "iaa", "ips", "ipp", "ipv"]
# Fórmula do INDE (verificada por regressão: R² = 1,0 em 2023 e 2024)
PESOS_INDE = {"ian": .1, "ida": .2, "ieg": .2, "iaa": .1, "ips": .1, "ipp": .1, "ipv": .2}


def num_fase_ideal(txt):
    txt = str(txt).upper()
    if "ALFA" in txt:
        return 0
    m = re.search(r"FASE\s*(\d)", txt)
    return int(m.group(1)) if m else np.nan


def tipo_instituicao(txt):
    t = str(txt).lower()
    if t in ("nan", "none"):
        return np.nan
    if "pública" in t or "publica" in t:
        return "Pública"
    if "concluiu" in t or "formado" in t or "nenhuma" in t:
        return "Concluiu / outro"
    return "Privada / bolsa"  # Privada, apadrinhamento, bolsa 100%, empresa parceira


def pedra(s):
    return s.astype(str).str.strip().replace(
        {"Agata": "Ágata", "nan": np.nan, "INCLUIR": np.nan, "": np.nan})


def serial_excel_para_idade(v):
    """Idade veio como data (ex.: 1900-01-08 = 8 anos): o Excel leu o número como serial de data."""
    if isinstance(v, (pd.Timestamp, dt.datetime)):
        return (pd.Timestamp(v) - pd.Timestamp("1899-12-31")).days
    return pd.to_numeric(v, errors="coerce")


def limpa_2022(d):
    return pd.DataFrame({
        "ano": 2022, "ra": d["RA"],
        "fase": d["Fase"].astype(int),
        "fase_ideal": d["Fase ideal"].map(num_fase_ideal),
        "defasagem": d["Defas"],
        "idade": d["Idade 22"],
        "genero": d["Gênero"].map({"Menina": "Feminino", "Menino": "Masculino"}),
        "ano_ingresso": d["Ano ingresso"],
        "instituicao": d["Instituição de ensino"].map(
            lambda t: "Pública" if "Pública" in t else "Privada / bolsa"),
        "pedra": pedra(d["Pedra 22"]),
        "inde": d["INDE 22"],
        "ian": d["IAN"], "ida": d["IDA"], "ieg": d["IEG"], "iaa": d["IAA"], "ips": d["IPS"],
        "ipp": np.nan,  # não existe em 2022
        "ipv": d["IPV"],
        "mat": d["Matem"], "port": d["Portug"], "ing": d["Inglês"],
        "rec_psicologia": d["Rec Psicologia"],
        "indicado_bolsa": d["Indicado"], "atingiu_pv": d["Atingiu PV"],
        "pedra_ant": pedra(d["Pedra 21"]), "formado": False,
    })


def limpa_2023(d):
    return pd.DataFrame({
        "ano": 2023, "ra": d["RA"],
        "fase": d["Fase"].map(lambda s: 0 if str(s).upper() == "ALFA" else int(str(s)[-1])),
        "fase_ideal": d["Fase Ideal"].map(num_fase_ideal),
        "defasagem": d["Defasagem"],
        "idade": d["Idade"].map(serial_excel_para_idade),
        "genero": d["Gênero"],
        "ano_ingresso": d["Ano ingresso"],
        "instituicao": d["Instituição de ensino"].map(tipo_instituicao),
        "pedra": pedra(d["Pedra 2023"]),
        "inde": pd.to_numeric(d["INDE 2023"], errors="coerce"),
        "ian": d["IAN"], "ida": d["IDA"], "ieg": d["IEG"], "iaa": d["IAA"], "ips": d["IPS"],
        "ipp": d["IPP"], "ipv": d["IPV"],
        "mat": d["Mat"], "port": d["Por"], "ing": d["Ing"],
        "rec_psicologia": np.nan, "indicado_bolsa": np.nan, "atingiu_pv": np.nan,
        "pedra_ant": pedra(d["Pedra 22"]), "formado": False,
    })


def limpa_2024(d):
    fase_txt = d["Fase"].astype(str).str.strip()      # aqui a coluna Fase traz a turma ('3A')
    formado = fase_txt.eq("9")                        # 38 formados, sem avaliação ('INCLUIR')
    fase = fase_txt.map(lambda s: 0 if s.upper() == "ALFA" else (int(s[0]) if s[0].isdigit() else np.nan))
    return pd.DataFrame({
        "ano": 2024, "ra": d["RA"],
        "fase": fase.where(~formado),
        "fase_ideal": d["Fase Ideal"].map(num_fase_ideal),
        "defasagem": d["Defasagem"],
        "idade": d["Idade"],
        "genero": d["Gênero"],
        "ano_ingresso": d["Ano ingresso"],
        "instituicao": d["Instituição de ensino"].map(tipo_instituicao),
        "pedra": pedra(d["Pedra 2024"]),
        "inde": pd.to_numeric(d["INDE 2024"], errors="coerce"),
        "ian": d["IAN"], "ida": d["IDA"], "ieg": d["IEG"], "iaa": d["IAA"], "ips": d["IPS"],
        "ipp": d["IPP"], "ipv": d["IPV"],
        "mat": d["Mat"], "port": d["Por"], "ing": d["Ing"],
        "rec_psicologia": np.nan, "indicado_bolsa": np.nan, "atingiu_pv": np.nan,
        "pedra_ant": pedra(d["Pedra 23"]), "formado": formado,
    })


def main():
    x = pd.read_excel(ARQ, sheet_name=None)
    p = pd.concat([limpa_2022(x["PEDE2022"]), limpa_2023(x["PEDE2023"]), limpa_2024(x["PEDE2024"])],
                  ignore_index=True)
    # defasagem = fase - fase ideal (2 linhas de 2024 divergiam do valor original)
    p["defasagem"] = (p["fase"] - p["fase_ideal"]).where(p["fase"].notna(), p["defasagem"])
    # IAN oficial: 10 = adequado (>= 0), 5 = moderada (-1 a -2), 2,5 = severa (<= -3)
    p["ian"] = np.select([p.defasagem >= 0, p.defasagem >= -2], [10.0, 5.0], 2.5)
    # formados de 2024 vêm com placeholders (IEG = 0, INDE = 'INCLUIR'): anula indicadores
    p.loc[p.formado, ["ian", "defasagem", "ieg", "ida", "iaa", "ips", "ipp", "ipv", "inde"]] = np.nan
    p["nivel_defasagem"] = pd.cut(p.defasagem, [-99, -3, -1, 99],
                                  labels=["Severa (≤ -3)", "Moderada (-1 a -2)", "Adequado (≥ 0)"])
    p["tempo_programa"] = p["ano"] - p["ano_ingresso"]
    p["em_defasagem"] = (p["defasagem"] < 0).astype(float).where(p.defasagem.notna())
    # 2024: 64 universitários (fase 8) trazem IEG = 0 como placeholder e nenhum outro indicador
    p["sem_indicadores"] = p[["ida", "iaa", "ips", "ipv"]].isna().all(axis=1)
    p.loc[p.sem_indicadores, "ieg"] = np.nan
    p.to_csv(SAIDA / "painel_alunos.csv", index=False)

    # ---- pares aluno em t -> t+1 (base do modelo) ----
    a = p[~p.formado & ~p.sem_indicadores]
    pares = []
    for t in (2022, 2023):
        prox = p[(p.ano == t + 1) & ~p.formado & p.defasagem.notna()][
            ["ra", "fase", "defasagem", "em_defasagem", "inde", "ida", "ieg", "ipv"]]
        prox = prox.rename(columns={c: c + "_prox" for c in prox.columns if c != "ra"})
        m = a[a.ano == t].merge(prox, on="ra", how="inner")
        m["ano_base"] = t
        pares.append(m)
    pares = pd.concat(pares, ignore_index=True)
    pares.to_csv(SAIDA / "pares_modelo.csv", index=False)

    print("painel:", p.shape, "| por ano:", p.groupby("ano").size().to_dict())
    print("formados excluídos de 2024:", int(p.formado.sum()),
          "| sem indicadores:", p.groupby("ano").sem_indicadores.sum().to_dict())
    print("pares t->t+1:", pares.groupby("ano_base").size().to_dict())
    return p, pares


if __name__ == "__main__":
    main()

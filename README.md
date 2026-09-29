# Datathon Passos Mágicos — Fase 5 PosTech

Análise de dados (2022–2024), storytelling e modelo preditivo de risco de defasagem escolar
para a Associação Passos Mágicos.

## Estrutura

```
data/raw/        base original (BASE_DE_DADOS_PEDE_2024_-_DATATHON.xlsx, abas PEDE2022/23/24)
data/processed/  painel_alunos.csv (base limpa e harmonizada) e pares_modelo.csv (base do modelo)
src/limpeza.py   limpeza e harmonização das 3 abas em um esquema único
src/analise.py   responde as perguntas 1–8, 10 e 11; gera reports/figuras e reports/tabelas
src/features.py  feature engineering do modelo (usado pelo notebook e pelo app)
src/treino.py    treino do modelo final (usado pelo notebook e como fallback do app)
notebooks/modelo_risco_defasagem.ipynb   modelo preditivo (pergunta 9) — feature eng., treino/teste, avaliação
app/streamlit_app.py   aplicação que serve o modelo (aluno individual ou planilha)
models/          modelo treinado (.joblib) e metadata.json com as métricas
reports/         figuras (.png) e tabelas (.csv) usadas na apresentação
```

## Como reproduzir

```bash
pip install -r requirements.txt
python src/limpeza.py                 # gera data/processed/*.csv
python src/analise.py                 # gera reports/figuras e reports/tabelas
jupyter nbconvert --to notebook --execute --inplace notebooks/modelo_risco_defasagem.ipynb
streamlit run app/streamlit_app.py    # abre o app localmente
```

## Principais decisões de limpeza (ver docstring de `src/limpeza.py`)

- As 3 abas têm nomes de colunas diferentes (`Defas` × `Defasagem`, `Matem` × `Mat`) — harmonizadas em um schema único.
- Em 2024 a coluna `Fase` traz a **turma** (ex. `"3A"`), não a fase — extraída da primeira letra/dígito.
- 38 alunos formados em 2024 vêm com indicadores placeholder (`INCLUIR`, IEG = 0) — excluídos das análises de indicadores.
- Em 2023, 399 idades vieram corrompidas (datas seriais do Excel, ex. `1900-01-08` = 8 anos) — corrigidas.
- Defasagem recalculada como `fase − fase ideal` (2 linhas de 2024 divergiam do valor original da planilha).
- Fórmula do INDE confirmada por regressão (R² = 1,0 em 2023/2024): 10% IAN + 20% IDA + 20% IEG + 10% IAA + 10% IPS + 10% IPP + 20% IPV.

## Modelo preditivo (pergunta 9)

- **Alvo:** aluno em defasagem (fase < fase ideal) no ano seguinte.
- **Dados:** 1.306 pares aluno-ano (2022→2023 e 2023→2024), separação treino/teste **agrupada por aluno**.
- **Modelo:** Gradient Boosting calibrado. AUC = 0,90 no teste (0,88 em validação temporal), contra 0,70 de uma regra de
  persistência simples ("quem está defasado hoje continua defasado").
- Detalhes completos, comparação de modelos e interpretação: ver o notebook.

## Deploy no Streamlit Community Cloud

1. Suba este repositório no GitHub (inclua `data/processed/`, `models/` e `requirements.txt`).
2. Em [share.streamlit.io](https://share.streamlit.io), aponte para `app/streamlit_app.py` como arquivo principal.
3. Não é necessário configurar segredos — o app é 100% local ao repositório.

## Entregáveis do Datathon

| Item | Onde está |
|---|---|
| Link do GitHub | *a publicar* |
| Apresentação (storytelling) | `reports/apresentacao.pptx` (a gerar) |
| Notebook do modelo preditivo | `notebooks/modelo_risco_defasagem.ipynb` |
| App Streamlit + deploy | `app/streamlit_app.py` |
| Vídeo (até 5 min) | *a gravar pelo grupo* |

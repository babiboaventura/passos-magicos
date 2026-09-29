# Datathon Passos Mágicos

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

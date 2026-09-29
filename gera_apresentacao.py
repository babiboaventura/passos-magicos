"""
Gera reports/apresentacao.pdf a partir de um deck HTML (16:9, 1 <section> por slide),
renderizado com Playwright (Chromium) em páginas de 1280x720.
"""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
FIG = RAIZ / "reports/figuras"
mc = json.loads((RAIZ / "reports/metricas_chave.json").read_text())
meta = json.loads((RAIZ / "models/metadata.json").read_text())

NAVY, INK, TEAL, AMBER, CORAL, GRAY, LINE, PAPER = \
    "#0B1F3A", "#111827", "#0E7C86", "#C9860A", "#B94152", "#5B6472", "#E4E8EF", "#FBFBF9"


def img(name, alt=""):
    return f'<img src="{FIG / (name + ".png")}" alt="{alt}">'


def n(v, casas=1):
    return f"{v:.{casas}f}".replace(".", ",")


def milhar(v):
    return f"{v:,}".replace(",", ".")


def slide(cls, body, kicker=None, num=None):
    k = f'<div class="kicker">{kicker}</div>' if kicker else ""
    pg = f'<div class="pageno">{num:02d}</div>' if num else ""
    return f'<section class="slide {cls}">{k}{body}{pg}</section>'


SLIDES = []

# ---------------------------------------------------------------- 01 · Capa
SLIDES.append(slide("cover", f"""
  <div class="cover-grid">
    <div class="cover-left">
      <div class="cover-eyebrow">Datathon PosTech FIAP · Fase 5</div>
      <h1>O que os dados da Passos Mágicos contam sobre a jornada de cada aluno</h1>
      <p class="cover-sub">Análise de três anos de indicadores educacionais (2022–2024) e um modelo preditivo
      para antecipar risco de defasagem escolar.</p>
      <div class="cover-meta">Associação Passos Mágicos · Base PEDE 2022–2024 · {mc['q1']['n']['2022'] + mc['q1']['n']['2023'] + mc['q1']['n']['2024']:,} registros de aluno-ano</div>
    </div>
    <div class="cover-right">
      <div class="cover-stat"><div class="v">{mc['q1']['pct']['2024']['Adequado (≥ 0)']:.0f}%</div><div class="l">dos alunos estavam com a fase adequada em 2024,<br>contra {mc['q1']['pct']['2022']['Adequado (≥ 0)']:.0f}% em 2022</div></div>
      <div class="cover-stat"><div class="v">{n(meta['metricas_teste']['auc'],2)}</div><div class="l">AUC do modelo que estima o risco de defasagem<br>do aluno no ano seguinte</div></div>
    </div>
  </div>
""".replace(f"{mc['q1']['n']['2022'] + mc['q1']['n']['2023'] + mc['q1']['n']['2024']:,}", f"{mc['q1']['n']['2022'] + mc['q1']['n']['2023'] + mc['q1']['n']['2024']:,}".replace(",", "."))))

# ---------------------------------------------------------------- 02 · Contexto
SLIDES.append(slide("text-only", f"""
  <h2>Uma fórmula que já muda vidas há 35 anos</h2>
  <div class="two-col">
    <div>
      <p>A Passos Mágicos leva educação de qualidade, apoio psicológico e ampliação de horizontes a crianças e
      jovens em vulnerabilidade social. Só em 2024, os alunos da base vieram de 56 escolas de origem diferentes.</p>
      <p>Todo aluno é acompanhado por sete indicadores complementares, que juntos formam o <b>INDE</b>, a nota
      geral usada para classificar cada aluno em uma "pedra" (Quartzo, Ágata, Ametista ou Topázio):</p>
    </div>
    <div class="indicadores-lista">
      <div><b>IAN</b> — Adequação de nível (defasagem)</div>
      <div><b>IDA</b> — Desempenho acadêmico</div>
      <div><b>IEG</b> — Engajamento</div>
      <div><b>IAA</b> — Autoavaliação</div>
      <div><b>IPS</b> — Psicossocial</div>
      <div><b>IPP</b> — Psicopedagógico <span class="tag">desde 2023</span></div>
      <div><b>IPV</b> — Ponto de virada</div>
    </div>
  </div>
  <p class="lead">Esta análise cruza os três ciclos da pesquisa PEDE para responder: <b>o programa está funcionando,
  e conseguimos prever — a tempo de agir — quem vai precisar de mais apoio?</b></p>
  <div class="stat-row">
    <div><div class="v">{milhar(mc['q1']['n']['2022'])}</div><div class="l">alunos avaliados em 2022</div></div>
    <div><div class="v">{milhar(mc['q1']['n']['2023'])}</div><div class="l">alunos avaliados em 2023</div></div>
    <div><div class="v">{milhar(mc['q1']['n']['2024'])}</div><div class="l">alunos avaliados em 2024</div></div>
    <div><div class="v">{milhar(mc['q1']['coorte3_n'])}</div><div class="l">alunos acompanhados nos 3 anos seguidos</div></div>
  </div>
""", kicker="O desafio", num=2))

# ---------------------------------------------------------------- 03 · Dados e metodologia
SLIDES.append(slide("text-only", f"""
  <h2>A base exigiu garimpo antes de contar qualquer história</h2>
  <div class="three-col">
    <div class="card">
      <div class="card-h">3 planilhas, 3 esquemas</div>
      <p>Colunas com nomes diferentes a cada ano (<i>Defas</i> × <i>Defasagem</i>), e em 2024 a coluna "Fase"
      trazia a <b>turma</b> ("3A"), não a fase — corrigido via a fase ideal declarada.</p>
    </div>
    <div class="card">
      <div class="card-h">Registros incompletos</div>
      <p>399 idades de 2023 vieram corrompidas (datas seriais do Excel) e 38 universitários formados em 2024
      têm indicadores placeholder — ambos tratados e excluídos onde cabia.</p>
    </div>
    <div class="card">
      <div class="card-h">Duas lentes de leitura</div>
      <p>Sempre que possível comparamos a <b>foto anual</b> da população com os <b>mesmos alunos</b> seguidos
      entre anos — são leituras diferentes, e a diferença entre elas é uma das descobertas do estudo.</p>
    </div>
  </div>
  <div class="footnote-box">
    Fórmula do INDE confirmada por regressão sobre os dados (R² = 1,0): 10% IAN + 20% IDA + 20% IEG + 10% IAA + 10% IPS + 10% IPP + 20% IPV.
  </div>
  <div class="stat-row alt">
    <div><div class="v">{mc['q11']['qualidade']['idade_2023_corrompida']}</div><div class="l">idades corrigidas em 2023</div></div>
    <div><div class="v">{mc['q11']['qualidade']['formados_sem_avaliacao_2024']}</div><div class="l">formados sem indicadores, excluídos em 2024</div></div>
    <div><div class="v">3</div><div class="l">esquemas de coluna diferentes, harmonizados em 1</div></div>
  </div>
""", kicker="Como chegamos aqui", num=3))

# ---------------------------------------------------------------- 04 · Q1 IAN
SLIDES.append(slide("chart", f"""
  <h2>A defasagem está caindo, e mais rápido para quem o programa consegue acompanhar de perto</h2>
  <div class="figure-wrap">{img('q1_defasagem')}</div>
  <div class="insight-bar">
    <span class="pill teal">468 alunos nos 3 anos</span> defasagem média foi de <b>−0,85</b> para <b>−0,23</b> fase —
    melhor que a leitura por foto anual, sinal de que o programa retém melhor quem já está evoluindo.
  </div>
""", kicker="Q1 · Adequação de nível (IAN)", num=4))

# ---------------------------------------------------------------- 05 · Q2 IDA
SLIDES.append(slide("chart", f"""
  <h2>Desempenho acadêmico estagnou — e cai justamente quando o aluno é promovido de fase</h2>
  <div class="figure-wrap">{img('q2_ida')}</div>
  <div class="insight-bar">
    <span class="pill amber">2023 → 2024</span> IDA médio caiu de {n(mc['q2']['media']['2023'])} para {n(mc['q2']['media']['2024'])}
    (p < 0,001). Alunos promovidos de fase perderam {n(abs(mc['q2']['promovido']['delta']))} pontos de IDA em média —
    o salto de conteúdo da nova fase pesa mais do que o ganho da promoção.
  </div>
""", kicker="Q2 · Desempenho acadêmico (IDA)", num=5))

# ---------------------------------------------------------------- 06 · Q3 IEG
SLIDES.append(slide("chart", f"""
  <h2>Engajamento é o sinal mais consistente de desempenho e de virada</h2>
  <div class="figure-wrap">{img('q3_engajamento')}</div>
  <div class="insight-bar">
    Correlação IEG×IDA e IEG×IPV fica estável em torno de <b>0,5</b> nos três anos — o único vínculo que não oscila.
    Quem está no quartil de maior engajamento tem IDA {n(mc['q3']['faixas']['≥ 9,5']['ida'] - mc['q3']['faixas']['< 6']['ida'])} pontos acima de quem está no menor.
  </div>
""", kicker="Q3 · Engajamento nas atividades (IEG)", num=6))

# ---------------------------------------------------------------- 07 · Q4 IAA
SLIDES.append(slide("chart", f"""
  <h2>Quem mais precisa de ajuda é quem menos percebe que precisa</h2>
  <div class="figure-wrap">{img('q4_autoavaliacao')}</div>
  <div class="insight-bar">
    Entre alunos com IDA abaixo de 4, a autoavaliação (IAA) já é {n(mc['q4']['faixa_ida']['< 4']['iaa'])} — quase o mesmo patamar
    de quem vai bem. A correlação IAA×IDA é fraca (ρ ≈ 0,13–0,18): <b>a autoavaliação sozinha não serve como alerta de risco.</b>
  </div>
""", kicker="Q4 · Autoavaliação (IAA)", num=7))

# ---------------------------------------------------------------- 08 · Q5 IPS
SLIDES.append(slide("chart", f"""
  <h2>O IPS de hoje não avisa a queda de amanhã</h2>
  <div class="figure-wrap">{img('q5_ips')}</div>
  <div class="insight-bar">
    Nenhuma faixa de IPS se destaca na taxa de queda de IDA/IEG no ano seguinte (χ² sem significância, p > 0,3 em todos os casos).
    O que antecipa queda é outro sinal: <b>IDA e IPV já baixos hoje</b> — não o aspecto psicossocial isoladamente.
  </div>
""", kicker="Q5 · Aspectos psicossociais (IPS)", num=8))

# ---------------------------------------------------------------- 09 · Q6 IPP
SLIDES.append(slide("chart", f"""
  <h2>O psicopedagógico frequentemente diverge do que o IAN aponta</h2>
  <div class="figure-wrap">{img('q6_ipp_ian')}</div>
  <div class="insight-bar">
    <span class="pill coral">61% dos defasados</span> têm IPP alto (≥ 7,5) — a avaliação psicopedagógica não enxerga o mesmo
    atraso que a fase escolar indica. A defasagem parece refletir mais o <b>percurso formal</b> do aluno do que sua capacidade
    percebida em sala.
  </div>
""", kicker="Q6 · Aspectos psicopedagógicos (IPP)", num=9))

# ---------------------------------------------------------------- 10 · Q7 IPV
SLIDES.append(slide("chart", f"""
  <h2>O ponto de virada nasce do desempenho — e, desde 2023, também do olhar psicopedagógico</h2>
  <div class="figure-wrap">{img('q7_ipv')}</div>
  <div class="insight-bar">
    Em 2022, IDA e IEG explicavam a maior parte do IPV (R² = 0,48). Em 2024, o IPP passa a ser o maior peso (β = 0,61,
    R² = 0,65) — sinal de que a leitura psicopedagógica amadureceu como termômetro do avanço do aluno.
  </div>
""", kicker="Q7 · Ponto de virada (IPV)", num=10))

# ---------------------------------------------------------------- 11 · Q8 INDE
SLIDES.append(slide("chart", f"""
  <h2>Indicadores fortes se somam: nenhum sozinho garante a pedra Topázio</h2>
  <div class="figure-wrap">{img('q8_inde')}</div>
  <div class="insight-bar">
    IDA é quem mais separa Topázio de Quartzo/Ágata (+0,67 pt de INDE), seguido por IEG (+0,46) e IPV (+0,32).
    Com os 4 indicadores fortes (≥ 8) simultaneamente, {n(mc['q8']['n_fortes']['4']['pct_topazio'], 0)}% dos alunos chegam a Topázio —
    com nenhum, apenas {n(mc['q8']['n_fortes']['0']['pct_topazio'], 0)}%.
  </div>
""", kicker="Q8 · Multidimensionalidade dos indicadores", num=11))

# ---------------------------------------------------------------- 12 · Q10 Efetividade
SLIDES.append(slide("chart", f"""
  <h2>A "foto" da população melhora mais rápido do que a "filme" de cada aluno</h2>
  <div class="figure-wrap">{img('q10_efetividade')}</div>
  <div class="insight-bar">
    O INDE médio da população sobe ({n(mc['q10']['inde_medio']['2022'])} → {n(mc['q10']['inde_medio']['2024'])}), mas o dos mesmos alunos
    acompanhados fica praticamente estável (~7,4 nos três anos). O ganho populacional reflete a <b>composição de quem entra e sai</b>
    do programa, não uma trajetória ascendente garantida por aluno.
  </div>
""", kicker="Q10 · Efetividade do programa", num=12))

# ---------------------------------------------------------------- 13 · Q11 insights
SLIDES.append(slide("chart", f"""
  <h2>Engajamento prediz quem permanece, e a rede de origem concentra o risco</h2>
  <div class="figure-wrap">{img('q11_extras')}</div>
  <div class="insight-bar">
    Alunos com IEG > 8,5 têm até <b>84% de chance</b> de reaparecer no programa no ano seguinte, contra 42–44% com IEG < 7.
    Em 2024 a defasagem na rede pública chegou a {n(mc["q11"]["instituicao"][7]["pct_defasado"],0)}% contra {n(mc["q11"]["instituicao"][6]["pct_defasado"],0)}%
    na rede privada/bolsa — cerca de 5 vezes mais —, e escolas de origem específicas concentram os piores indicadores: pontos de
    partida naturais para ação direcionada.
  </div>
""", kicker="Q11 · Outros achados", num=13))

# ---------------------------------------------------------------- 14 · Q9 Modelo
SLIDES.append(slide("chart", f"""
  <h2>O modelo antecipa risco com 1 ano de antecedência — e vale mais que uma regra simples</h2>
  <div class="figure-wrap model">{img('q9_modelo_avaliacao')}</div>
  <div class="model-metrics">
    <div><div class="v">{n(meta['metricas_teste']['auc'],2)}</div><div class="l">AUC no teste<br><span class="muted">vs. {n(meta['baseline_persistencia']['auc'],2)} da regra "continua defasado"</span></div></div>
    <div><div class="v">{n(meta['validacao_temporal_auc'],2)}</div><div class="l">AUC treinando em 22→23<br>e testando em 23→24</div></div>
    <div><div class="v">{meta['adequados_hoje']['captura_top30']:.0%}</div><div class="l">dos que vão cair em defasagem<br>estão nos 30% de maior risco hoje</div></div>
  </div>
""", kicker="Q9 · Previsão de risco (Machine Learning)", num=14))

# ---------------------------------------------------------------- 15 · Recomendações
SLIDES.append(slide("text-only", f"""
  <h2>Da análise à ação: três frentes para o próximo ciclo</h2>
  <div class="three-col">
    <div class="card num"><div class="card-n">1</div>
      <div class="card-h">Priorizar pela virada, não só pela nota</div>
      <p>IEG e IPV concentram o maior poder preditivo. Ações de engajamento (participação, vínculo com a turma)
      tendem a mover mais indicadores do que reforço isolado de conteúdo.</p>
    </div>
    <div class="card num"><div class="card-n">2</div>
      <div class="card-h">Rever a leitura de autoavaliação e IPS</div>
      <p>IAA não distingue risco e IPS não antecipa queda — hoje funcionam como retrato de bem-estar, não como
      alerta precoce. Vale redesenhar o que se espera desses indicadores.</p>
    </div>
    <div class="card num"><div class="card-n">3</div>
      <div class="card-h">Usar o radar de risco no planejamento anual</div>
      <p>Aplicar o modelo (app Streamlit) logo após o fechamento de cada ciclo, focando o acompanhamento nos
      alunos hoje adequados mas classificados como alto risco — é onde a prevenção tem mais retorno.</p>
    </div>
  </div>
""", kicker="Recomendações", num=15))

# ---------------------------------------------------------------- 16 · Fechamento
SLIDES.append(slide("cover", f"""
  <div class="closing">
    <div class="cover-eyebrow">Obrigado</div>
    <h1>Os dados confirmam o que a Passos Mágicos já pratica: transformação é acompanhamento constante</h1>
    <p class="cover-sub">Repositório completo — limpeza, notebook do modelo e app Streamlit —
    disponível para a equipe técnica da associação.</p>
  </div>
""", num=16))


CSS = f"""
@page {{ size: 1280px 720px; margin: 0; }}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; padding: 0; }}
body {{ font-family: 'Source Sans 3', 'Segoe UI', Arial, sans-serif; color: {INK}; background: {PAPER}; }}
h1, h2 {{ font-family: 'Fraunces', Georgia, serif; color: {NAVY}; margin: 0; }}
.slide {{
  width: 1280px; height: 720px; position: relative; overflow: hidden;
  page-break-after: always; break-after: page;
  padding: 56px 72px 48px; background: {PAPER};
}}
.kicker {{ font-size: 16px; letter-spacing: .02em; color: {TEAL}; font-weight: 700; margin-bottom: 10px; }}
.pageno {{ position: absolute; bottom: 26px; right: 40px; font-size: 12px; color: {GRAY}; }}
h2 {{ font-size: 34px; line-height: 1.22; font-weight: 600; max-width: 1000px; margin-bottom: 22px; }}

/* ---- capa ---- */
.cover {{ background: {NAVY}; padding: 0; }}
.cover-grid {{ display: grid; grid-template-columns: 1.35fr 1fr; height: 100%; }}
.cover-left {{ padding: 74px 64px 74px 76px; display: flex; flex-direction: column; justify-content: center; }}
.cover-eyebrow {{ color: {AMBER}; font-weight: 700; font-size: 16px; letter-spacing: .02em; margin-bottom: 22px; }}
.cover h1 {{ color: #fff; font-size: 44px; line-height: 1.18; font-weight: 600; max-width: 640px; }}
.cover-sub {{ color: #C7D1DE; font-size: 19px; line-height: 1.5; max-width: 560px; margin-top: 22px; }}
.cover-meta {{ color: #7E90A8; font-size: 14px; margin-top: 40px; border-top: 1px solid #24374F; padding-top: 18px; max-width: 560px; }}
.cover-right {{ background: #0E2A4A; display: flex; flex-direction: column; justify-content: center; gap: 40px; padding: 0 52px; }}
.cover-right .cover-stat .v {{ color: {AMBER}; font-family: 'Fraunces', serif; font-size: 58px; font-weight: 600; line-height: 1; }}
.cover-right .cover-stat .l {{ color: #C7D1DE; font-size: 15px; margin-top: 10px; line-height: 1.4; }}
.closing {{ height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: flex-start; padding: 0 40px; max-width: 980px; }}
.closing h1 {{ color: #fff; font-size: 38px; line-height: 1.25; font-weight: 600; }}
.closing .cover-sub {{ margin-top: 22px; }}

/* ---- texto ---- */
.text-only p {{ font-size: 17px; line-height: 1.55; color: #333B47; }}
.two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 48px; align-items: start; margin-top: 8px; }}
.indicadores-lista {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px 22px; align-content: start; margin-top: 6px; }}
.indicadores-lista div {{ font-size: 15px; padding: 10px 14px; background: #fff; border: 1px solid {LINE}; border-radius: 3px; }}
.indicadores-lista b {{ color: {TEAL}; }}
.tag {{ float: right; font-size: 11px; color: {AMBER}; font-weight: 700; }}
.lead {{ font-size: 19px; color: {NAVY}; border-left: 3px solid {AMBER}; padding-left: 18px; margin-top: 30px; max-width: 980px; }}

.three-col {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; margin-top: 12px; }}
.card {{ background: #fff; border: 1px solid {LINE}; border-radius: 4px; padding: 24px; position: relative; }}
.card-h {{ font-weight: 700; color: {NAVY}; font-size: 17px; margin-bottom: 10px; }}
.card p {{ font-size: 14.5px; line-height: 1.5; color: #444C58; margin: 0; }}
.card.num .card-n {{ position: absolute; top: -14px; left: 20px; background: {NAVY}; color: {AMBER}; font-family: 'Fraunces', serif;
  font-weight: 600; font-size: 18px; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }}
.footnote-box {{ margin-top: 34px; font-size: 13.5px; color: {GRAY}; border-top: 1px solid {LINE}; padding-top: 16px; }}

.stat-row {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-top: 46px; padding-top: 28px; border-top: 1px solid {LINE}; }}
.stat-row .v {{ font-family: 'Fraunces', serif; font-weight: 600; font-size: 34px; color: {TEAL}; }}
.stat-row .l {{ font-size: 13px; color: {GRAY}; margin-top: 4px; line-height: 1.35; max-width: 190px; }}
.stat-row.alt {{ margin-top: 40px; }}
.stat-row.alt .v {{ color: {NAVY}; }}

/* ---- slides de gráfico ---- */
.figure-wrap {{ display: flex; justify-content: center; align-items: center; }}
.figure-wrap img {{ width: 100%; max-height: 470px; object-fit: contain; }}
.figure-wrap.model img {{ max-height: 420px; }}
.insight-bar {{ margin-top: 22px; background: #fff; border: 1px solid {LINE}; border-left: 4px solid {TEAL};
  border-radius: 3px; padding: 16px 22px; font-size: 15.5px; line-height: 1.5; color: #333B47; }}
.pill {{ display: inline-block; font-size: 12px; font-weight: 700; color: #fff; padding: 3px 10px; border-radius: 3px; margin-right: 8px; }}
.pill.teal {{ background: {TEAL}; }}
.pill.amber {{ background: {AMBER}; }}
.pill.coral {{ background: {CORAL}; }}

.model-metrics {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; margin-top: 26px; }}
.model-metrics .v {{ font-family: 'Fraunces', serif; font-size: 42px; font-weight: 600; color: {NAVY}; }}
.model-metrics .l {{ font-size: 14px; color: #444C58; margin-top: 6px; line-height: 1.4; }}
.model-metrics .muted {{ color: {GRAY}; }}
"""

HTML = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:wght@500;600&family=Source+Sans+3:wght@400;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>
{''.join(SLIDES)}
</body></html>"""

(RAIZ / "reports/_apresentacao.html").write_text(HTML, encoding="utf-8")
print("html gerado:", len(SLIDES), "slides")

import streamlit as st
import streamlit.components.v1 as components
from database.config import SessionLocal
import urllib.parse

# --- IMPORTAÇÃO DOS MODELOS (Ordem para evitar erros de mapeamento) ---
from classes.familias import Familia  
from classes.regras import RegraTag
from classes.metas import Meta
from classes.ativos import Ativo
from classes.usuarios import Usuario
from classes.contas import Conta
from classes.transacoes import Transacao
from classes.categorias import Categoria
from classes.indices import IndiceFinanceiro

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import joinedload
import locale
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.utf-8')
except:
    locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')

# ==========================================
# 🎨 CENTRAL DE ESTILO E DESIGN 
# ==========================================
# region

TEMA_ATUAL = "ClaroVivo" 
CORES_TEMA = {
    "ClaroVivo": {"card": "#F0F0F0", "texto": "#565555", "botao_off": "#f0f2f6", "botao_texto": "#565555"},
    "EscuroVivo": {"card": "#1E1E1E", "texto": "#FFFFFF", "botao_off": "#333333", "botao_texto": "#AAAAAA"}
}
c = CORES_TEMA[TEMA_ATUAL]

COR_PRINCIPAL = "#298173" 
RAIO_BORDA = "50px" 
ESPACO_INTERNO = "50px" 
FONTE_SANS = "Montserrat"

st.set_page_config(page_title="MeuDinheiro Resumo", layout="centered")

# endregion


# ==========================================
# 📊 LÓGICA DE DADOS
# ==========================================
#region
with SessionLocal() as db: 
    # Carrega categorias e contas com transações (evita DetachedInstanceError)
    categorias = db.query(Categoria).options(joinedload(Categoria.transacoes)).filter(Categoria.id_usuario == 1).all()
    contas_usuario = db.query(Conta).options(joinedload(Conta.transacoes)).filter(Conta.id_usuario == 1).all()
    saldototal_usuario = sum([c.saldo_atual for c in contas_usuario])

# --- TOPO DO APP ---
st.title("Painel de Controle Financeiro")

st.session_state.privacidade = st.checkbox("Privacidade", value=True)

if st.session_state.privacidade:  
    exibicao_saldo = "R$ ****"
else:
    exibicao_saldo = f"R$ {saldototal_usuario:,.2f}"

st.write(f"## Saldo total: {exibicao_saldo}")

st.markdown("<br>", unsafe_allow_html=True)
st.write(f"### <span style='color: {COR_PRINCIPAL};'>DESPESAS POR CATEGORIA</span>", unsafe_allow_html=True)
#endregion

# 1. Seleção de Período (Funcional e Nativa)
# Usamos colunas para centralizar e controlar a largura total
_, col_botoes, _ = st.columns([0.5, 9, 0.5])
with col_botoes:
    opcao = st.segmented_control(
        "Período",
        ["Mensal", "Semanal", "Bimestral", "Trimestral", "Semestral", "Anual"],
        default="Mensal",
        key="periodo_selector",
        label_visibility="collapsed"
    )

if not opcao:
    opcao = "Mensal"

# 2. Lógica de Datas
hoje = date.today()
if opcao == "Semanal": data_inicio, data_fim = hoje - timedelta(days=7), hoje
elif opcao == "Bimestral": data_inicio, data_fim = hoje - relativedelta(months=2), hoje
elif opcao == "Trimestral": data_inicio, data_fim = hoje - relativedelta(months=3), hoje
elif opcao == "Semestral": data_inicio, data_fim = hoje - relativedelta(months=6), hoje
elif opcao == "Anual": data_inicio, data_fim = hoje - relativedelta(years=1), hoje
else: data_inicio, data_fim = hoje - timedelta(days=30), hoje # Mensal

# 3. Nome do Período (MARÇO)
meses_pt = ["JANEIRO", "FEVEREIRO", "MAR&Ccedil;O", "ABRIL", "MAIO", "JUNHO", 
            "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"]
nome_periodo = meses_pt[hoje.month - 1] if opcao == "Mensal" else opcao.upper()

# 4. Processamento de Dados (Filtro e Legenda)
labels_grafico, valores_grafico, cores_grafico = [], [], []
itens_legenda_html = ""
for cat in categorias:
    total = sum([t.valor for t in cat.transacoes if (t.tipo in ["Despesa", "Transferencia", "Investimento"]) and data_inicio <= t.data.date() <= data_fim])
    if total > 0:
        labels_grafico.append(cat.nome); valores_grafico.append(total); cores_grafico.append(cat.cor_hex)
        v_txt = "R$ ****" if st.session_state.privacidade else f"R$ {total:,.2f}"
        itens_legenda_html += f'<div style="display: flex; justify-content: space-between; margin-bottom: 12px;"><span style="color: {cat.cor_hex}; font-weight: 700; text-transform: uppercase; font-size: 0.9rem;">{cat.nome}</span><span style="color: {cat.cor_hex}; font-weight: 700; font-size: 0.9rem;">{v_txt}</span></div>'

if not valores_grafico:
    labels_grafico, dados_js, cores_grafico = ["Sem Dados"], [1], ["#DDDDDD"]
else:
    dados_js = [1 for _ in valores_grafico] if st.session_state.privacidade else valores_grafico

# --- CSS INJETADO PARA INTEGRAR BOTÕES AO CARD ---
st.markdown(f"""
    <style>
    /* Estilo Pílula e Cores para os botões do Streamlit */
    button[data-testid="stBaseButton-secondary"] {{
        border-radius: 50px !important;
        background-color: {COR_PRINCIPAL}15 !important;
        color: {COR_PRINCIPAL} !important;
        border: 1px solid {COR_PRINCIPAL}33 !important;
        padding: 0.2rem 1rem !important;
    }}
    button[aria-selected="true"] {{
        background-color: {COR_PRINCIPAL} !important;
        color: white !important;
        font-weight: 700 !important;
    }}
    /* "Puxa" o card para cima dos botões */
    div[data-testid="stVerticalBlock"] > div:has(iframe) {{
        margin-top: -55px !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- HTML E JS PARA O GRÁFICO ---
html_final = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
        body {{ margin: 0; padding: 20px; background: transparent; font-family: 'Montserrat', sans-serif; overflow: hidden; }}
        .widget-card {{
            background-color: {c['card']}; border-radius: {RAIO_BORDA}; 
            padding: {ESPACO_INTERNO}; border: 1px solid #E0E0E0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05); color: {c['texto']};
            min-height: 380px;
        }}
        .grid {{ display: flex; align-items: center; gap: 30px; padding-top: 30px; }}
        .titulo {{ color: {COR_PRINCIPAL}; font-weight: 700; text-align: right; font-size: 1.6rem; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <div class="widget-card">
        <div class="grid">
            <div style="flex: 1.3; max-width: 280px; position: relative;">
                <canvas id="myChart"></canvas>
            </div>
            <div style="flex: 1;">
                <div class="titulo">{nome_periodo}</div>
                {itens_legenda_html}
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        const ctx = document.getElementById('myChart').getContext('2d');
        new Chart(ctx, {{
            type: 'doughnut',
            data: {{
                labels: {labels_grafico},
                datasets: [{{
                    data: {dados_js},
                    backgroundColor: {cores_grafico},
                    borderWidth: 0
                }}]
            }},
            options: {{ 
                responsive: true,
                maintainAspectRatio: true,
                cutout: '70%', 
                plugins: {{ legend: {{ display: false }} }} 
            }}
        }});
    </script>
</body>
</html>
"""

html_encoded = f"data:text/html;charset=utf-8,{urllib.parse.quote(html_final)}"
components.iframe(html_encoded, height=500)
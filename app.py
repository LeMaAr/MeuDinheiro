import streamlit as st
import streamlit.components.v1 as components
from database.config import SessionLocal
from classes.usuarios import Usuario
from classes.contas import Conta
from classes.transacoes import Transacao
from classes.indices import IndiceFinanceiro
from classes.categorias import Categoria
from classes.metas import Meta
from classes.familias import Familia
from classes.regras import RegraTag
from classes.ativos import Ativo
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

# region: Configuração básica da página
st.set_page_config(page_title="MeuDinheiro Dash", layout="centered") # Define o título da página e o layout como "wide" para aproveitar toda a largura da tela
st.title(" Painel de Controle Financeiro") # Título principal do painel de controle
# endregion

# region: Configuração do banco de dados e elementos para a contrução dos gráficos

# Função para obter uma sessão de banco de dados e garantir que ela seja fechada corretamente após o uso, mesmo que ocorram erros durante as operações de leitura e escrita. 
def get_db():
   
    db = SessionLocal()
    try:
        yield db # Gera uma sessão de banco de dados para ser usada em operações de leitura e escrita, garantindo que a sessão seja fechada corretamente após o uso, mesmo que ocorram erros durante as operações.
    finally:
        db.close() # Fecha a sessão do banco de dados para liberar recursos e evitar conexões pendentes, garantindo que a aplicação funcione de maneira eficiente e segura.


# buscando os dados do banco de dados para exibir no painel de controle do usuário, utilizando a função get_db() para garantir que a sessão do banco de dados 
# seja gerenciada corretamente, evitando conexões pendentes e garantindo que os recursos sejam liberados adequadamente após as operações de leitura e escrita.
with SessionLocal() as db: 

#region: consulta as categorias e contas do usuário:
    # Consulta as categorias associadas ao usuário atual, filtrando pelo ID do usuário. Retorna uma lista de objetos Categoria que pertencem ao usuário 
    # (os objetos são: id_categoria, nome, cor_hex, icone, id_usuario, e os relacionamentos com transações e subcategorias). 
    categorias = db.query(Categoria).filter(Categoria.id_usuario == 1 ).all()  

    # Consulta as contas associadas ao usuário atual, filtrando pelo ID do usuário. Retorna uma lista de objetos Conta que pertencem ao usuário 
    # (os objetos são: id_conta, nome_conta, saldo_atual, tipo_conta, limite_seguranca, id_usuario, id_indice, e os relacionamentos com transações e índices financeiros).
    contas_usuario = db.query(Conta).filter(Conta.id_usuario == 1 ).all()   

    # Calcula o saldo total do usuário somando os saldos atuais de todas as contas associadas ao usuário, para exibir o saldo total do usuário no painel de controle. 
    saldototal_usuario = sum([c.saldo_atual for c in contas_usuario])

#endregion


# endregion

# region: Exibição do saldo total do usuário e configuração de privacidade 

#region: Saldo e Privacidade (Topo do App)
st.session_state.privacidade = st.checkbox("Privacidade", value=True)

if st.session_state.privacidade:  
    exibicao_saldo = "R$ ****"
else:
    exibicao_saldo = f"R$ {saldototal_usuario:,.2f}"

st.write(f"## Saldo total: {exibicao_saldo}")
#endregion

# --- INÍCIO DO WIDGET ---
with st.container(border=True):
    
    # 1. Seleção de Período
    opcao = st.segmented_control(
        "Período",
        ["Mensal", "Semanal", "Trimestral", "Semestral", "Anual", "Personalizado"],
        default="Mensal",
        key="periodo_selector",
        label_visibility="collapsed"
    )

    # 2. Lógica de Datas
    hoje = date.today()
    if opcao == "Semanal": data_inicio, data_fim = hoje - timedelta(days=7), hoje
    elif opcao == "Mensal": data_inicio, data_fim = hoje - timedelta(days=30), hoje
    elif opcao == "Trimestral": data_inicio, data_fim = hoje - relativedelta(months=3), hoje
    elif opcao == "Semestral": data_inicio, data_fim = hoje - relativedelta(months=6), hoje
    elif opcao == "Anual": data_inicio, data_fim = hoje - relativedelta(years=1), hoje
    else:
        c1, c2 = st.columns(2)
        data_inicio = c1.date_input("Início", hoje - timedelta(days=30), format="DD/MM/YYYY")
        data_fim = c2.date_input("Fim", hoje, format="DD/MM/YYYY")

    # 3. Busca de Dados 
    labels_grafico, valores_grafico, cores_grafico = [], [], []
    with SessionLocal() as db:
        for cat in categorias:
            total_despesa = sum([
                t.valor for t in cat.transacoes 
                if (t.tipo in ["Despesa", "Transferencia", "Investimento"]) 
                and data_inicio <= t.data.date() <= data_fim
            ])
            if total_despesa > 0:
                labels_grafico.append(cat.nome)
                valores_grafico.append(total_despesa)
                cores_grafico.append(cat.cor_hex)

    if not valores_grafico:
        labels_grafico, valores_grafico, cores_grafico = ["Sem transações"], [1], ["#DDDDDD"]

    # 4. Lógica de Privacidade (Movida para cá para evitar o NameError)
    if st.session_state.privacidade:
        dados_js = [1 for _ in valores_grafico]
    else:
        dados_js = valores_grafico

    # 5. Definição do Gráfico (Movida para cá para ler as variáveis corretas)
    codigo_grafico = f"""
    <div style="font-family: 'Montserrat', sans-serif;">
        <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap" rel="stylesheet">
        <canvas id="myChart"></canvas>
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
                    borderWidth: 0,
                    hoverOffset: 20
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                cutout: '65%',
                plugins: {{ legend: {{ display: false }} }}
            }}
        }});
        </script>
    </div>"""

    # 6. Renderização Final
    col_grafico, col_legenda = st.columns([1.2, 1], gap="medium")
    with col_grafico:
        components.html(codigo_grafico, height=380)

    with col_legenda:
        st.markdown(f"<div style='color: {COR_CABECALHO}; font-family: {FONTE_ESCOLHIDA}; font-weight: 700; text-align: right; font-size: 1.5rem; margin-bottom: 30px;'>{opcao.upper()}</div>", unsafe_allow_html=True)
        for label, valor, cor in zip(labels_grafico, valores_grafico, cores_grafico):
            if label == "Sem transações": continue
            valor_txt = "R$ ****" if st.session_state.privacidade else f"R$ {valor:,.2f}"
            st.markdown(f'<div style="display: flex; justify-content: space-between; margin-bottom: 18px; font-family: \'{FONTE_ESCOLHIDA}\';"><span style="color: {cor}; font-weight: 700; text-transform: uppercase;">{label}</span><span style="color: {cor}; font-weight: 700;">{valor_txt}</span></div>', unsafe_allow_html=True)
# endregion

#endregion      

#endregion   
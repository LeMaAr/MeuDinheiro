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

# Função para obter uma sessão de banco de dados e garantir que ela seja fechada corretamente após o uso, mesmo que ocorram erros durante as operações de leitura e escrita. 
# Isso é importante para liberar recursos e evitar conexões pendentes, garantindo que a aplicação funcione de maneira eficiente e segura.
def get_db():
   
    db = SessionLocal()
    try:
        yield db # Gera uma sessão de banco de dados para ser usada em operações de leitura e escrita, garantindo que a sessão seja fechada corretamente após o uso, mesmo que ocorram erros durante as operações.
    finally:
        db.close() # Fecha a sessão do banco de dados para liberar recursos e evitar conexões pendentes, garantindo que a aplicação funcione de maneira eficiente e segura.

# Configuração básica da página
st.set_page_config(page_title="MeuDinheiro Dash", layout="centered") # Define o título da página e o layout como "wide" para aproveitar toda a largura da tela
st.title(" Painel de Controle Financeiro") # Título principal do painel de controle

with SessionLocal() as db: 
    #Todas_as_contas = db.query(Conta).all() # Consulta todas as contas do banco de dados
    #nomes = [c.nome_conta for c in Todas_as_contas] # Extrai os nomes das contas para exibir no dropdown
    #saldos = [c.saldo_atual for c in Todas_as_contas] # Extrai os saldos das contas para exibir no gráfico
    #contas_usuario = db.query(Conta).filter(Conta.id_usuario == self.usuario_id).all() # Consulta as contas associadas ao usuário atual, filtrando pelo ID do usuário para garantir que apenas as contas relevantes sejam exibidas no painel de controle
    contas_usuario = db.query(Conta).filter(Conta.id_usuario == 1 ).all()
    categorias_usuario = db.query(Categoria).filter(Categoria.id_categoria).all() # Consulta as categorias associadas ao usuário atual, filtrando pelo nome para garantir que apenas as categorias relevantes sejam exibidas no painel de controle, fornecendo uma visão organizada das categorias de despesas e receitas do usuário.
    saldototal_usuario = sum([c.saldo_atual for c in contas_usuario]) # Extrai a soma dos saldos das contas do usuário para exibir o saldo total do usuário no painel de controle, fornecendo uma visão geral da situação financeira do usuário.
    saldototaloculto_usuario = "R$*****" # Define um valor oculto para o saldo total do usuário, garantindo que as informações sensíveis sejam protegidas quando a privacidade estiver ativada, permitindo que o usuário escolha se deseja ocultar ou exibir informações sensíveis no painel de controle, como saldos das contas ou transações recentes, garantindo que o usuário tenha controle sobre a visibilidade de suas informações financeiras.
    transcoesporcategoria_usuario = db.query(Transacao, Categoria).join(Categoria, Transacao.id_categoria == Categoria.id_categoria).filter(Transacao.id_usuario == 1).all() # Consulta as transações do usuário agrupadas por categoria, utilizando um join entre as tabelas de transações e categorias para obter os nomes das categorias associadas a cada transação, filtrando pelo ID do usuário para garantir que apenas as transações relevantes sejam exibidas no painel de controle, fornecendo uma visão detalhada das despesas e receitas do usuário por categoria.
st.session_state.privacidade = st.checkbox("Privacidade", value=True) # Checkbox para ativar ou desativar a privacidade, permitindo que o usuário escolha se deseja ocultar ou exibir informações sensíveis no painel de controle, como saldos das contas ou transações recentes, garantindo que o usuário tenha controle sobre a visibilidade de suas informações financeiras.

if st.session_state.privacidade: # Verifica o estado do checkbox de privacidade para determinar se as informações sensíveis devem ser exibidas ou ocultadas no painel de controle, garantindo que o usuário tenha controle sobre a visibilidade de suas informações financeiras.
    st.write("R$*****") # Exibe um valor oculto para o saldo total do usuário, garantindo que as informações sensíveis sejam protegidas quando a privacidade estiver ativada.


codigo_grafico = f"""

<div>
    <canvas id="myChart"></canvas>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <script>
    
    const ctx = document.getElementById('myChart').getContext('2d');

    const myChart = new Chart (ctx, {{ type:'doughnut', 
                                       data: {{labels: {categorias_usuario}, 
                                       datasets: [{{label: 'Saldo total', 
                                                    data: {saldototal_usuario}, 
                                                    backgroundColor: ['#FF6384','#36A2EB','#FFCE56','#4BC0C0','#9966FF','#FF9F40','#C9CBCF','#46BFBD','#FDB45C','#949FB1'], 
                                                    hoverOffset: 20}}] 
                                                    }},
                                                    
                                       options: {{responsive: true, plugins: {{legend: {{position: 'top'}}}}}}
                                       }});
    </script>
</div>""" # Código HTML e JavaScript para criar um gráfico de rosca usando a biblioteca Chart.js, onde os rótulos são os nomes das contas e os dados são os saldos das contas
                                            
components.html(codigo_grafico, height= 1200) # Exibe o gráfico usando o componente HTML do Streamlit, definindo a altura do componente para 1200 pixels

        
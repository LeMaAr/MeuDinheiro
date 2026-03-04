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

# Configuração básica da página
st.set_page_config(page_title="MeuDinheiro Dash", layout="centered") # Define o título da página e o layout como "wide" para aproveitar toda a largura da tela
st.title(" Painel de Controle Financeiro") # Título principal do painel de controle

db = SessionLocal() # Cria uma sessão de banco de dados para interagir com os dados

Todas_as_contas = db.query(Conta).all() # Consulta todas as contas do banco de dados

nomes = [c.nome_conta for c in Todas_as_contas] # Extrai os nomes das contas para exibir no dropdown
saldos = [c.saldo_atual for c in Todas_as_contas] # Extrai os saldos das contas para exibir no gráfico

db.close() # Fecha a sessão do banco de dados após a consulta

nomes = [c.nome_conta for c in Todas_as_contas] # Extrai os nomes das contas para exibir no dropdown
saldos = [c.saldo_atual for c in Todas_as_contas] # Extrai os saldos das contas para exibir no gráfico

codigo_grafico = f"""

<div>
    <canvas id="myChart"></canvas>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <script>
    
    const ctx = document.getElementById('myChart').getContext('2d');

    const myChart = new Chart (ctx, {{ type:'doughnut', 
                                       data: {{labels: {nomes}, 
                                       datasets: [{{label: 'Saldo das contas', 
                                                    data: {saldos}, 
                                                    backgroundColor: ['#FF6384','#36A2EB','#FFCE56','#4BC0C0','#9966FF','#FF9F40','#C9CBCF','#46BFBD','#FDB45C','#949FB1'], 
                                                    hoverOffset: 20}}] 
                                                    }},
                                                    
                                       options: {{responsive: true, plugins: {{legend: {{position: 'top'}}}}}}
                                       }});
    </script>
</div>""" # Código HTML e JavaScript para criar um gráfico de rosca usando a biblioteca Chart.js, onde os rótulos são os nomes das contas e os dados são os saldos das contas
                                            
components.html(codigo_grafico, height= 1200) # Exibe o gráfico usando o componente HTML do Streamlit, definindo a altura do componente para 1200 pixels

        
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

# region: Configuração básica da página
st.set_page_config(page_title="MeuDinheiro Dash", layout="centered") # Define o título da página e o layout como "wide" para aproveitar toda a largura da tela
st.title(" Painel de Controle Financeiro") # Título principal do painel de controle
# endregion

# region: Configuração do banco de dados e criação de tabelas

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
    
    # Consulta as categorias associadas ao usuário atual, filtrando pelo ID do usuário. Retorna uma lista de objetos Categoria que pertencem ao usuário 
    # (os objetos são: id_categoria, nome, cor_hex, icone, id_usuario, e os relacionamentos com transações e subcategorias). 
    categorias = db.query(Categoria).filter(Categoria.id_usuario == 1 ).all()  

    # Consulta as contas associadas ao usuário atual, filtrando pelo ID do usuário. Retorna uma lista de objetos Conta que pertencem ao usuário 
    # (os objetos são: id_conta, nome_conta, saldo_atual, tipo_conta, limite_seguranca, id_usuario, id_indice, e os relacionamentos com transações e índices financeiros).
    contas_usuario = db.query(Conta).filter(Conta.id_usuario == 1 ).all()   

    labels_grafico = [] # Lista para armazenar os rótulos do gráfico, que são os nomes das categorias
    valores_grafico = [] # Lista para armazenar os valores do gráfico, que são as somas dos valores das transações associadas a cada categoria
    cores_grafico = [] # Lista para armazenar as cores do gráfico, que são as cores hexadecimais associadas a cada categoria

    # Calcula o saldo total do usuário somando os saldos atuais de todas as contas associadas ao usuário, para exibir o saldo total do usuário no painel de controle. 
    saldototal_usuario = sum([c.saldo_atual for c in contas_usuario])

    for cat in categorias: # Itera sobre as categorias do usuário para preencher as listas de rótulos, valores e cores do gráfico
        total_despesa = sum([t.valor for t in cat.transacoes if t.tipo == "Despesa" or t.tipo == "Transferencia" or t.tipo == "Investimento"]) # Calcula a soma dos valores das transações associadas à categoria que são do tipo "Despesa", "Transferencia" ou "Investimento", para obter o total de despesas da categoria
        
        if total_despesa > 0: # Verifica se o total de despesas da categoria é maior que zero para incluir a categoria no gráfico.
            labels_grafico.append(cat.nome) # Adiciona o nome da categoria à lista de rótulos do gráfico
            valores_grafico.append(total_despesa) # Adiciona o total de despesas da categoria à lista de valores do gráfico
            cores_grafico.append(cat.cor_hex) # Adiciona a cor hexadecimal da categoria à lista de cores do gráfico.
# endregion

# region: Exibição do saldo total do usuário e gráfico de despesas por categoria e configuração de privacidade 

# Checkbox para ativar ou desativar a privacidade, permitindo que o usuário escolha se deseja ocultar ou exibir informações sensíveis no painel de controle, 
# como saldos das contas ou transações recentes, garantindo que o usuário tenha controle sobre a visibilidade de suas informações financeiras.
st.session_state.privacidade = st.checkbox("Privacidade", value=True) 

# Verifica o estado do checkbox de privacidade para determinar se as informações sensíveis devem ser exibidas ou ocultadas no painel de controle, 
# garantindo que o usuário tenha controle sobre a visibilidade de suas informações financeiras.
# Se a privacidade estiver desativada, exibe o saldo total do usuário; caso contrário, exibe um valor oculto para proteger as informações sensíveis.
if st.session_state.privacidade:  
    exibicao_saldo = "R$ ****" # Exibe um valor oculto para o saldo total do usuário, protegendo as informações sensíveis quando a privacidade estiver ativada.
    dados_js = [1 for _ in valores_grafico] # Gera uma lista de valores fictícios para o gráfico, substituindo os valores reais por 1, para ocultar as informações sensíveis no gráfico quando a privacidade estiver ativada.
else:
    exibicao_saldo = f"R$ {saldototal_usuario:.2f}" # Exibe o saldo total do usuário formatado como moeda, mostrando as informações reais quando a privacidade estiver desativada.
    dados_js = valores_grafico # Usa os valores reais para o gráfico, mostrando as informações reais no gráfico quando a privacidade estiver desativada.

st.write(f"## Saldo total: {exibicao_saldo}") # Exibe o saldo total do usuário no painel de controle, usando a variável exibicao_saldo para mostrar ou ocultar as informações sensíveis.
# endregion

# region: Renderização do gráfico de despesas por categoria usando Chart.js e Streamlit


codigo_grafico = f"""

<div>
    <canvas id="myChart"></canvas>
 
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <script>
    
    const ctx = document.getElementById('myChart').getContext('2d');

    const myChart = new Chart (ctx, {{ type:'doughnut', 
                                       data: {{labels: {labels_grafico}, 
                                       datasets: [{{label: 'Saldo total', 
                                                    data: {dados_js}, 
                                                    backgroundColor: {cores_grafico}, 
                                                    hoverOffset: 20}}] 
                                                    }},
                                                    
                                       options: {{responsive: true, plugins: {{legend: {{position: 'top'}}}}}}
                                       }});
    </script>
</div>""" # Código HTML e JavaScript para criar um gráfico de rosca usando a biblioteca Chart.js, onde os rótulos são os nomes das contas e os dados são os saldos das contas
                                            
components.html(codigo_grafico, height= 1200) # Exibe o gráfico usando o componente HTML do Streamlit, definindo a altura do componente para 1200 pixels

# endregion
        
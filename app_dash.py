from dash import Dash, html, dcc, Input, Output, clientside_callback
import dash_bootstrap_components as dbc
from data_provider import get_saldo_geral, get_data_despesas

# 1. DEFINIÇÃO DE COMPONENTES (MOLDES)
def criar_widget(tipo):
    if tipo == "despesas_cat":
        return html.Div(className="widget-card", children=[
            html.H4("DESPESAS POR CATEGORIA", className="card-title-inner"),
            html.Canvas(id="chart-donut-despesas"),
            dcc.Store(id="store-dados-despesas")
        ])
    elif tipo == "ultimas_mov":
        return html.Div(className="widget-card", children=[
            html.H4("ÚLTIMAS MOVIMENTAÇÕES"),
            html.Div(id="tabela-movimentacoes")
        ])
    return html.Div("Widget não encontrado")

# 2. CONFIGURAÇÃO DO APP
app = Dash(__name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    external_scripts=["https://cdn.jsdelivr.net/npm/chart.js"]
)

# 3. LAYOUT (O QUE APARECE NA TELA)
app.layout = html.Div(id="main-container", className="tema-escuro-vivo", children=[
    
    # Header do seu design do Illustrator
    html.Div(className="header-container", children=[
        html.H1("RESUMO", className="text-title"),
        html.P("GRÁFICOS | CONTAS | INVESTIMENTOS | METAS", className="text-subtitle"),
    ]),

    # Seletor de Tema (Dentro do layout)
    html.Div(className="config-area", children=[
        html.Label("Selecione o Tema:", style={'color': 'white'}),
        dcc.Dropdown(
            id='theme-selector',
            options=[
                {'label': 'Escuro Vivo', 'value': 'tema-escuro-vivo'},
                {'label': 'Claro Vivo', 'value': 'tema-claro-vivo'},
                {'label': 'Escuro Pastel', 'value': 'tema-escuro-pastel'}
            ],
            value='tema-escuro-vivo',
            style={'color': 'black', 'width': '200px'}
        ),
    ]),

    # Card de Saldo
    html.Div(className="card-financeiro", children=[
        html.P("SALDO EM CONTAS", className="card-label"),
        html.H2(id="saldo-display", className="card-value"),
    ]),

    # Container de Widgets Dinâmicos
    html.Div(id="widget-container", children=[
        criar_widget("despesas_cat") 
    ]),

    # Trigger para carregar os dados
    dcc.Interval(id='interval-load', interval=1*500, n_intervals=0, max_intervals=1)
])

# 4. CALLBACKS (LÓGICA)

# Mudar o Tema
@app.callback(
    Output("main-container", "className"),
    Input("theme-selector", "value")
)
def update_theme(selected_theme):
    return selected_theme

# Carregar Dados do SQLAlchemy
@app.callback(
    [Output("saldo-display", "children"),
     Output("store-dados-despesas", "data")],
    [Input("interval-load", "n_intervals")]
)
def carregar_dados_iniciais(n):
    id_user = 1 
    saldo = get_saldo_geral(id_user)
    dados_grafico = get_data_despesas(id_user)
    
    # Formatação de Moeda Brasileira
    saldo_formatado = f"R$ {saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return saldo_formatado, dados_grafico

# Ponte JavaScript para o Chart.js
clientside_callback(
    """
    function(dados) {
        if(dados && window.dash_clientside.clientside.renderizarGraficoDonut) {
            window.dash_clientside.clientside.renderizarGraficoDonut(dados);
        }
        return "";
    }
    """,
    Output("chart-donut-despesas", "className"),
    Input("store-dados-despesas", "data")
)

if __name__ == "__main__":
    app.run(debug=True)
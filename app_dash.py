from dash import Dash, html, dcc, Input, Output, clientside_callback
import dash_bootstrap_components as dbc
from data_provider import get_saldo_geral, get_data_despesas, get_ultimas_movimentacoes

# 1. DEFINIÇÃO DE COMPONENTES (MOLDES)
def criar_widget(tipo, dados_grafico=None, dados_mov=None):
    if tipo == "despesas_cat":
        return html.Div(className="widget-card", children=[
            html.H4("DESPESAS POR CATEGORIA", className="card-title-inner"),
            html.Div(className="chart-container", children=[
                html.Canvas(id="chart-donut-despesas")
            ]),
            dcc.Store(id="store-dados-despesas", data=dados_grafico)
        ])
    elif tipo == "ultimas_mov":
        rows = [
            html.Div(className="movimentacao-row", children=[
                html.Span(m['descricao'], className="mov-desc"),
                html.Span(f"R$ {m['valor']:,.2f}", 
                         className="mov-valor " + ("red" if m['tipo'] == 'despesa' else "green")),
                html.Span(m['data'], className="mov-data")
            ]) for m in (dados_mov or [])
        ]
        return html.Div(className="widget-card", children=[
            html.H4("ÚLTIMAS MOVIMENTAÇÕES", className="card-title-inner"),
            html.Div(rows, className="tabela-container")
        ])
    
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
    criar_widget("despesas_cat"),
    criar_widget("ultimas_mov")
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

# Ponte JavaScript para o Chart.js
clientside_callback(
    """
    function(dados) {
        if(dados && window.dash_clientside && window.dash_clientside.clientside) {
            // Chamada com pequena espera para garantir o DOM pronto
            setTimeout(function() {
                window.dash_clientside.clientside.renderizarGraficoDonut(dados);
            }, 100);
        }
        return "";
    }
    """,
    Output("chart-donut-despesas", "className"),
    Input("store-dados-despesas", "data")
)

@app.callback(
    [Output("saldo-display", "children"),
     Output("store-dados-despesas", "data"),
     Output("widget-container", "children")],
    [Input("interval-load", "n_intervals")]
)
def carregar_dados_reais(n):
    id_user = 1
    saldo = get_saldo_geral(id_user)
    dados_grafico = get_data_despesas(id_user)
    dados_mov = get_ultimas_movimentacoes(id_user)
    
    saldo_formatado = f"R$ {saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    # Criamos os widgets injetando os dados buscados
    widgets = [
        criar_widget("despesas_cat", dados_grafico=dados_grafico),
        criar_widget("ultimas_mov", dados_mov=dados_mov)
    ]
    
    return saldo_formatado, dados_grafico, widgets

if __name__ == "__main__":
    app.run(debug=True)


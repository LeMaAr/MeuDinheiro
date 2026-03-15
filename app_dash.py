import dash
from dash import html, dcc, Input, Output, clientside_callback
import dash_bootstrap_components as dbc
from datetime import datetime
import locale

# Importando suas funções
from data_provider import get_saldo_geral, get_data_despesas

# 1. Adicionamos o Chart.js de forma limpa aqui
app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    external_scripts=["https://cdn.jsdelivr.net/npm/chart.js"] # Carrega o motor do gráfico
)

app.scripts.config.serve_locally = True

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# --- COMPONENTES DE INTERFACE ---

def criar_card_saldo():
    return html.Div(className="widget-card-saldo", children=[
        html.H4("SALDO EM CONTAS", className="card-title-inner"),
        html.H2(id="saldo-display", className="saldo-valor")
    ])

def criar_widget_grafico():
    return html.Div(className="widget-card-grafico", children=[
        html.H4("DESPESAS POR CATEGORIA", className="card-title-inner"),
        html.Div(id="titulo-periodo", className="titulo-mes-referencia"),
        
        # Container Flex para Gráfico (Esquerda) e Legenda (Direita)
        html.Div(className="layout-grafico-container", children=[
            html.Div(className="chart-container", children=[
                html.Canvas(id="chart-donut-despesas")
            ]),
            html.Div(id="legenda-lateral-container", className="legenda-lateral")
        ]),
        dcc.Store(id="store-dados-despesas")
    ])

# --- LAYOUT PRINCIPAL ---

app.layout = html.Div(id="main-container", className="escuro-vivo", children=[
    dcc.Interval(id="interval-load", interval=10000, n_intervals=0), # Atualiza a cada 10s
    
    # Cabeçalho e Seletores
    html.Div(className="header-container", children=[
        html.H1("RESUMO", className="main-title"),
        html.Div(className="controles-row", children=[
            html.Div([
                html.Label("Selecione o Tema:"),
                dcc.Dropdown(
                    id="theme-selector",
                    options=[
                        {'label': 'Escuro Vivo', 'value': 'escuro-vivo'},
                        {'label': 'Claro UI', 'value': 'claro-ui'}
                    ],
                    value='escuro-vivo',
                    clearable=False
                )
            ], className="control-group"),
            
            html.Div([
                html.Label("Período:"),
                dcc.Dropdown(
                    id="filtro-tempo",
                    options=[
                        {'label': 'Hoje', 'value': 'hoje'},
                        {'label': 'Semanal', 'value': 'semanal'},
                        {'label': 'Mensal', 'value': 'mensal'},
                        {'label': 'Trimestral', 'value': 'trimestral'},
                        {'label': 'Semestral', 'value': 'semestral'},
                        {'label': 'Anual', 'value': 'anual'},
                    ],
                    value='mensal',
                    clearable=False
                )
            ], className="control-group")
        ])
    ]),

    # Grid de Widgets
    html.Div(className="content-grid", children=[
        criar_card_saldo(),
        criar_widget_grafico()
    ])
])

# --- CALLBACKS (CÉREBRO DO APP) ---

# 1. Callback de Tema
@app.callback(
    Output("main-container", "className"),
    Input("theme-selector", "value")
)
def update_theme(selected_theme):
    return selected_theme or "escuro-vivo"

# 2. Callback de Dados (Saldo + Gráfico + Legenda)
@app.callback(
    [Output("saldo-display", "children"),
     Output("store-dados-despesas", "data"),
     Output("legenda-lateral-container", "children"),
     Output("titulo-periodo", "children")],
    [Input("interval-load", "n_intervals"),
     Input("filtro-tempo", "value")]
)
def atualizar_dados_dashboard(n, periodo):
    id_user = 1
    periodo = periodo or "mensal"
    
    # Busca dados no banco
    saldo = get_saldo_geral(id_user)
    dados_grafico = get_data_despesas(id_user, periodo=periodo)
    
    # Formata Saldo
    saldo_txt = f"R$ {saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    # Nome do mês para o título
    mes_ref = datetime.now().strftime('%B %Y').upper()
    
    # Gera itens da legenda lateral (bolinhas coloridas)
    itens_legenda = [
        html.Div(className="legenda-row", children=[
            html.Div(className="legenda-cor", style={"backgroundColor": i['cor_hex']}),
            html.Span(i['categoria'], className="legenda-nome"),
            html.Span(f"R$ {i['valor']:,.2f}", className="legenda-valor")
        ]) for i in dados_grafico
    ]
    
    return saldo_txt, dados_grafico, itens_legenda, mes_ref

# 3. Ponte JavaScript para o Chart.js
clientside_callback(
    """
    function(dados) {
        if(dados && window.dash_clientside && window.dash_clientside.clientside) {
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
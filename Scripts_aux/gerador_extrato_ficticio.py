import pandas as pd
import random
from datetime import datetime, timedelta

# Configurações do teste
categorias_teste = ["Alimentação", "Transporte", "Lazer", "Saúde", "Educação"]
descricoes_comuns = [
    "UBER TRIP", "IFOOD LUNCH", "MERCADO SAO JOSE", "FARMACIA PRECO BOM",
    "POSTO DE GASOLINA", "NETFLIX", "ACADEMIA FIT", "PADARIA DO ZE", "PIX RECEBIDO"
]

data_inicial = datetime(2026, 2, 1)
dados = []

for i in range(30):
    data = data_inicial + timedelta(days=random.randint(0, 24))
    desc = random.choice(descricoes_comuns)
    # Gera valores negativos para despesas e positivos para receitas (PIX)
    valor = random.uniform(10.0, 500.0)
    if "PIX" not in desc:
        valor *= -1
    
    dados.append({
        "Data Lançamento": data.strftime("%d/%m/%Y"),
        "Histórico": desc + f" {random.randint(100, 999)}", # Adiciona sufixo para variar
        "Valor (R$)": round(valor, 2),
        "Saldo Final": 0.0 # Coluna extra para testar a resiliência do mapeador
    })

# Criando o DataFrame e salvando
df_teste = pd.DataFrame(dados)
df_teste.to_csv("meu_extrato_teste.csv", index=False)
print("Arquivo 'meu_extrato_teste.csv' gerado com sucesso!")
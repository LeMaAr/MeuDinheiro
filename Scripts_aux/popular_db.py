import sys
import os

# 1. Garante o path primeiro
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'meudinheiro.db'))

if os.path.exists(db_path):
    print(f"🗑️ Removendo banco de dados antigo em: {db_path}")
    os.remove(db_path)

# 2. Importa o Base e o Engine
from database.config import SessionLocal, engine, Base


from classes.familias import Familia  # Importe Familia ANTES de Usuario
from classes.usuarios import Usuario
from classes.contas import Conta
from classes.categorias import Categoria
from classes.transacoes import Transacao
from classes.indices import IndiceFinanceiro
from classes.metas import Meta
from classes.regras import RegraTag
from classes.ativos import Ativo

import datetime
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import random

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()

def popular():
    print("🚀 Iniciando povoamento do banco de dados...")

    # 1. Criar Usuário Principal (O que o app.py consome)
    leandro = Usuario(nome="Leandro", email="leandro@email.com", senha_plana="senha123")
    db.add(leandro)
    db.commit()

    # 2. Criar Categorias com as cores do seu design
    cats = [
        Categoria(nome="Alimentação", cor_hex="#FF4B2B", id_usuario=leandro.id_usuario), 
        Categoria(nome="Transporte", cor_hex="#008080", id_usuario=leandro.id_usuario),
        Categoria(nome="Saúde", cor_hex="#3357FF", id_usuario=leandro.id_usuario),
        Categoria(nome="Lazer", cor_hex="#F333FF", id_usuario=leandro.id_usuario),
        Categoria(nome="Moradia", cor_hex="#FFD700", id_usuario=leandro.id_usuario)
    ]
    
    db.add_all(cats)
    db.commit()

    # 3. Criar Contas (Corrente e Cartões conforme seu mockup)
    contas = [
        Conta(nome_conta="Itaú", saldo_inicial=10000.0, id_usuario=leandro.id_usuario, tipo_conta="Corrente"),
        Conta(nome_conta="Banco C6", saldo_inicial=0.0, id_usuario=leandro.id_usuario, tipo_conta="Cartão", limite=15000.0),
        Conta(nome_conta="Banco Inter", saldo_inicial=1000.0, id_usuario=leandro.id_usuario, tipo_conta="Investimento")
    ]
    db.add_all(contas)
    db.commit()

    # 4. Gerador de Histórico (2.5 anos atrás até hoje)
    data_final = datetime.now()
    data_inicial = data_final - relativedelta(years=2, months=6)

    for _ in range(565):
        dias_diff = (data_final - data_inicial).days # Total de dias entre a data inicial e final
        data_aleatoria = data_inicial + timedelta(days=random.randint(0, dias_diff)) # Gera uma data aleatória dentro do intervalo

        #tipo = random.choice(["Despesa", "Receita", "Transferencia", "Investimento"], weights = [60, 20, 10, 10])[0] # Aumenta a probabilidade de gerar mais despesas.
        tipo = random.choices(["Despesa", "Receita", "Transferencia", "Investimento"], weights=[60, 20, 10, 10])[0] # Aumenta a probabilidade de gerar mais despesas.
        cat_escolhida = random.choice(cats) # Escolhe uma categoria aleatória da lista de categorias criadas

        t = Transacao(
            tipo_registro="comum",
            tipo=tipo,
            valor=random.uniform(20.0, 800.0) if tipo == "Despesa" else random.uniform(2000.0, 5000.0),
            id_conta=random.choice(contas).id_conta, # Escolhe uma conta aleatória da lista de contas criadas
            id_usuario=leandro.id_usuario,
            id_categoria=cat_escolhida.id_categoria if tipo == "Despesa" else None,
            descricao=f"{tipo} em {data_aleatoria.strftime('%d/%m/%Y')}",
            data=data_aleatoria, # O campo datetime aceita o objeto direto
            quitada=True
        )
        db.add(t)
    db.commit()

    print("✅ Banco de dados populado com successo!")

if __name__ == "__main__":
    popular()
    db.close()
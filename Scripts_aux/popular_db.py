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
        Categoria(nome="Lazer", cor_hex="#F333FF", id_usuario=leandro.id_usuario)
    ]
    db.add_all(cats)
    db.commit()

    # 3. Criar Contas (Corrente e Cartões conforme seu mockup)
    contas = [
        Conta(nome_conta="Principal Itaú", saldo_inicial=5000.0, id_usuario=leandro.id_usuario, tipo_conta="Corrente"),
        Conta(nome_conta="Banco C6", saldo_inicial=2000.0, id_usuario=leandro.id_usuario, tipo_conta="Cartão", limite=15000.0),
        Conta(nome_conta="Banco Inter", saldo_inicial=1000.0, id_usuario=leandro.id_usuario, tipo_conta="Investimento")
    ]
    db.add_all(contas)
    db.commit()

    # 4. Gerar Transações de DESPESA (Para o gráfico de rosca)
    for cat in cats:
        for _ in range(3): # 3 gastos por categoria
            t = Transacao(
                tipo_registro="comum",
                tipo="Despesa", # ATENÇÃO: Maiúsculo conforme seu app.py
                valor=random.uniform(50, 400),
                id_conta=contas[0].id_conta,
                id_usuario=leandro.id_usuario,
                id_categoria=cat.id_categoria,
                descricao=f"Compra em {cat.nome}",
                quitada=True
            )
            db.add(t)
    
    db.commit()
    print("✅ Banco de dados populado! Usuário ID 1 criado com sucesso.")

if __name__ == "__main__":
    popular()
    db.close()
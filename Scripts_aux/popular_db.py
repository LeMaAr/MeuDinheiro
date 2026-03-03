import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.config import SessionLocal, engine
from classes.regras import RegraTag
from classes.indices import IndiceFinanceiro
from classes.metas import Meta
from classes.usuarios import Usuario
from classes.familias import Familia
from classes.contas import Conta
from classes.transacoes import Transacao
from classes.categorias import Categoria
import random
from datetime import datetime, timedelta

db = SessionLocal()

def popular():
    
    print("🚀 Limpando dados antigos e iniciando povoamento...")
    
    # Apaga tudo das tabelas para evitar erro de duplicidade (UNIQUE constraint)
    db.query(Transacao).delete()
    db.query(Conta).delete()
    db.query(Usuario).delete()
    db.query(Familia).delete()
    db.query(Categoria).delete()
    db.commit()

    print(" Iniciando povoamento do banco de dados...")

    # 1. Criar 15 Usuários
    nomes = ["Leandro", "Aline", "Marcos", "Julia", "Ricardo", "Beatriz", "Tiago", 
             "Fernanda", "Lucas", "Carla", "Roberto", "Sonia", "Andre", "Patrícia", "Bruno"]
    usuarios = []
    for i, nome in enumerate(nomes):
        user = Usuario(
            nome=nome, 
            email=f"{nome.lower()}@email.com", 
            senha_plana="senha123",
        )

        usuarios.append(user)
    db.add_all(usuarios)
    db.commit()

    # 2. Criar Famílias
    fams = [Familia(nome_familia=n) for n in ["Silva", "Oliveira", "Santos"]]
    for f in fams:
        primeiro_membro = db.query(Usuario).filter_by(id_familia=f.id_familia).first()
        if primeiro_membro:
            f.id_admin = primeiro_membro.id_usuario

    db.add_all(fams)
    db.commit()

    # 3. Criar Categorias Básicas
    cats = [Categoria(nome="Alimentação", cor_hex="#FF5733"), 
            Categoria(nome="Lazer", cor_hex="#33FF57"),
            Categoria(nome="Saúde", cor_hex="#3357FF"),
            Categoria(nome="Investimentos", cor_hex="#F333FF")]
    db.add_all(cats)
    db.commit()

    # 4. Criar Contas para cada Usuário
    for u in usuarios:
        # Cada usuário terá uma conta corrente e alguns uma corretora
        c1 = Conta(nome_conta=f"Principal {u.nome}", saldo_inicial=random.uniform(1000, 5000), 
                   id_usuario=u.id_usuario, tipo_instituicao="banco", cor_perfil="#2E7D32")
        db.add(c1)
        
        if random.random() > 0.5: # 50% chance de ter conta investimento
            c2 = Conta(nome_conta=f"Investimentos {u.nome}", saldo_inicial=random.uniform(5000, 20000), 
                       id_usuario=u.id_usuario, tipo_instituicao="corretora", cor_perfil="#1565C0")
            db.add(c2)
    db.commit()

    # 5. Gerar Transações (Últimos 30 dias)
    contas_db = db.query(Conta).all()
    for conta in contas_db:
        for _ in range(10): # 10 transações por conta
            dias_atras = random.randint(0, 30)
            data = datetime.now() - timedelta(days=dias_atras)
            valor = random.uniform(10, 500)
            t = Transacao(
                tipo_registro="comum",
                tipo=random.choice(["despesa", "receita", "transferência", "investimento"]),
                descricao=f"Gasto em {random.choice(['Mercado', 'Farmácia', 'Posto', 'Streaming'])}",
                valor=valor,
                data=data,
                id_conta=conta.id_conta,
                id_usuario=conta.id_usuario,
                id_categoria=random.choice(cats).id_categoria,
                quitada=True,
                essencial=random.choice([True, False]) # Para Item 6: Reserva
            )
            db.add(t)
    
    db.commit()
    print("Banco de dados populado com sucesso!")

if __name__ == "__main__":
    popular()
    db.close()
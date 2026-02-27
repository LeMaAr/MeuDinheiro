import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.config import SessionLocal, Base, engine
from classes.usuarios import Usuario
from classes.categorias import Categoria, Subcategoria
from classes.transacoes import Transacao
from classes.familias import Familia
from classes.contas import Conta
from classes.regras import RegraTag
from datetime import datetime
from sqlalchemy import text

def testar_sistema_visual(): # Função para testar a criação de categorias, a geração de cores aleatórias e o relacionamento entre transações e categorias.
    print("Limpando e recriando tabelas...")
    
    # Comando para o SQLite ignorar as travas de chave estrangeira no momento do DROP
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys = OFF;")) # <--- ADICIONE text()
        Base.metadata.drop_all(bind=conn)
        Base.metadata.create_all(bind=conn)
        conn.execute(text("PRAGMA foreign_keys = ON;")) # <--- ADICIONE text()
        conn.commit() # Importante para garantir que as tabelas sejam criadas
    
    db = SessionLocal()
    
    try:
        # 2. Cria um Usuário de Teste
        # Adicionando o argumento 'senha_plana' que a classe Usuario exige
        user = Usuario(
            nome="Leandro", 
            email="leandro@teste.com", 
            senha_plana="123456" # Verifique se o nome do argumento é exatamente este
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        conta_teste = Conta(nome_conta="Carteira", saldo_inicial=100.0, id_usuario=user.id_usuario)
        db.add(conta_teste)
        db.commit()
        db.refresh(conta_teste)

        cat1 = Categoria(nome="Alimentação", id_usuario=user.id_usuario, icone="utensils")
        db.add(cat1)
        db.commit()
        db.refresh(cat1)

        print(f"\n--- Categoria Criada ---")
        print(f"Nome: {cat1.nome} | Cor: {cat1.cor_hex} | Ícone: {cat1.icone}")

        # 3. Cria Categorias (Sem passar cor, para testar a paleta de cores aleatórias)
        print("\n--- Testando Gerador de Cores Aleatórias ---")
        cat1 = Categoria(nome="Alimentação", id_usuario=user.id_usuario, icone="utensils")
        cat2 = Categoria(nome="Transporte", id_usuario=user.id_usuario, icone="car")
        cat3 = Categoria(nome="Lazer", id_usuario=user.id_usuario, icone="ticket")
        
        for c in [cat1, cat2, cat3]:
            c.add_categoria()
            print(f"Categoria: {c.nome:<15} | Cor: {c.cor_hex} | Ícone: {c.icone}")

        # 4. Cria uma Transação vinculada
        print("\n--- Testando Relacionamento (Ponte de Dados) ---")
        t1 = Transacao(
            tipo_registro="comum",
            valor=50.0,
            tipo="despesa",
            id_conta=conta_teste.id_conta, # <--- USAR O ID REAL AQUI
            id_usuario=user.id_usuario,
            id_categoria=cat1.id_categoria,
            descricao="Pizza de Sábado"
        )
        # Lembre-se de adicionar e dar commit no t1 também!
        db.add(t1)
        db.commit()
        db.refresh(t1)

        # 5. Acessaa a cor através da transação
        print(f"\nSucesso!")
        print(f"Transação: {t1.descricao}")
        print(f"Acessando Cor via Relacionamento: {t1.categoria.cor_hex}")
        print(f"Acessando Ícone via Relacionamento: {t1.categoria.icone}")

    except Exception as e:
        print(f"Erro no teste: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    testar_sistema_visual()
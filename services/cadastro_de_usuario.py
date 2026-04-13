from database.config import SessionLocal
from classes.usuarios import Usuario

def realizar_cadastro(nome, email, senha):
    db = SessionLocal()
    try:
        # 1. Criamos o objeto (aqui a senha vira hash automaticamente no __init__)
        novo_usuario = Usuario(
            nome=nome,
            email=email,
            senha_plana=senha
        )

        # 2. Adicionamos ao banco para gerar o ID
        db.add(novo_usuario)
        db.commit() # Salvamos o usuário
        db.refresh(novo_usuario) # Agora o Python sabe qual é o ID dele

        # 3. Geramos as categorias padrão usando o método que criamos
        # Passamos a sessão aberta para que tudo seja feito na mesma conexão
        novo_usuario.inicializar_novo_usuario(db)

        print(f"✅ Sucesso! Usuário '{nome}' cadastrado com categorias padrão.")
        return novo_usuario

    except Exception as e:
        db.rollback()
        print(f"❌ Erro no cadastro: {e}")
    finally:
        db.close()

# TESTE PRÁTICO:
if __name__ == "__main__":
    realizar_cadastro("Seu Nome", "teste@email.com", "senha123")
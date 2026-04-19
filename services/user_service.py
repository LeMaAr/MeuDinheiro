from database.config import SessionLocal
from classes.usuarios import Usuario
from database.mixin import CRUDMixin

def realizar_cadastro(nome, email, senha):
# Função responsável por criar o cadastro de um novo usuário no banco de dados, ela já inclui as categorias predefinidas em usuários.
    
    try:
        # 1. Cria e salva o usuário (Usa a sessão interna do Mixin)
        novo_usuario = Usuario(
            nome=nome,
            email=email,
            senha_plana=senha
        )
        novo_usuario.salvar() 

        # 2. Abre a sessão APENAS para as categorias
        db = SessionLocal()
        try:
            u = db.query(Usuario).filter_by(id_usuario=novo_usuario.id_usuario).first()
            u.inicializar_novo_usuario(db)
            db.commit()
            print(f"Sucesso! Usuário '{nome}' cadastrado com categorias padrão.")
            return novo_usuario
        
        except Exception as e_cat:
            db.rollback() 
            print(f"Usuário criado, mas erro nas categorias: {e_cat}")
            return novo_usuario
        
        finally:
            db.close()

    except Exception as e:
        print(f"Erro crítico no cadastro: {e}")
        return None

if __name__ == "__main__":
    realizar_cadastro("Seu Nome", "teste@email.com", "senha123")
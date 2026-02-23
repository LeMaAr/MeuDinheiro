import bcrypt
from database.config  import Base, SessionLocal
from sqlalchemy import Column, Integer, Float, String, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship

# Criando a classe usuário:
class Usuario(Base):
    
    __tablename__= "usuarios" # criando a tabela usuarios
    
    id_usuario = Column(Integer, primary_key=True, autoincrement=True) # id única do usuário, o primary key impede que hajam duas chaves iguais e o autoincrement adiciona 1 a cada novo usuário
    nome = Column(String) # nome do usuário
    email = Column(String, unique=True, nullable=False) # email do usuário
    senha_hash = Column(String) # código hash da senha do usuário
    tipo_usuario = Column(String) # Se o usuário é comum ou admin
    id_familia = Column(Integer, ForeignKey("familias.id_familia")) # id da família, se houver. Cria um relationship com a coluna id_familia da tabela famílias
    familia_vinculada = relationship("Familia", back_populates="usuarios")
    
    def __init__(self, nome, email, senha_plana, tipo_usuario= "comum", id_familia = None):
        self.nome = nome
        self.email = email
        self.tipo_usuario = tipo_usuario
        self.id_familia = id_familia

        # configurando o hash da senha:
        salt = bcrypt.gensalt()
        self.senha_hash = bcrypt.hashpw(senha_plana.encode('utf-8'),salt).decode('utf-8')

    def checar_senha(self, senha_digitada):
        return bcrypt.checkpw(senha_digitada.encode('utf-8'), self.senha_hash.encode('utf-8'))
    
    def atualizar_senha(self, nova_senha_plana):
        salt = bcrypt.gensalt()
        self.senha_hash = bcrypt.hashpw(nova_senha_plana.encode('utf-8'), salt).decode('utf-8')
        self.mod_usuario() # aplica a função para modificar o usuário
    
    def add_usuario(self):
        db = SessionLocal() # Estabelece a conexão com o banco de Dados.

        try:
            db.add(self) # adiciona o usuário ao bd
            db.commit() # comita a mudança
            db.refresh(self) # atualiza o bd
            print (f"Usuário {self.id_usuario} adicionado com sucesso!") # imprime uma mensagem de conclusão.
        
        except Exception as e:
            db.rollback() # caso haja algum erro, desfaz a operação.
            print (f"Erro ao adicionar o usuário{self.id_usuario}: {e}") # imprime uma mensagem de conclusão.
            raise e # lança o erro para fora da função.

        finally:
            db.close() # fecha a conexão com o BD

    def del_usuario(self):
        db = SessionLocal() # Estabelece a conexão com o banco de Dados.

        try:
            db.delete(self) # deleta o usuário do DB
            db.commit() # faz a alteração permanentemente
            print(f"Usuário {self.id_usuario} excluído com sucesso!") # imprime uma mensagem de conclusão.

        except Exception as e:
            db.rollback() # caso haja algum erro, desfaz a operação.
            print (f"Erro ao excluir o usuário{self.id_usuario}: {e}") # imprime uma mensagem de conclusão.
            raise e # lança o erro para fora da função.
        
        finally:
            db.close() # fecha a conexão com o BD

    def mod_usuario(self):

        db = SessionLocal() # Estabelece a conexão com o banco de Dados.
        
        try:
            db.merge(self) # mescla o estado atual do objeto com seu equivalente no BD
            db.commit() # salva a alteração no bd
            db.refresh(self) # atualiza o bd com a alteração
            print (f"Dados do usuário{self.id_usuario} alterados com sucesso.") # imprime a msg de conclusão
        
        except Exception as e:
            db.rollback() # caso haja algum erro, desfaz a operação.
            print (f"Erro ao alterar os dados: {e}") # imprime uma mensagem de conclusão.
            raise e # lança o erro para fora da função.

        finally:
            db.close() # fecha a conexão com o BD
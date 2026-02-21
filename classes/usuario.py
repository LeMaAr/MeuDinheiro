import bcrypt
from database.config  import Base, SessionLocal
from sqlalchemy import Column, Integer, Float, String, DateTime, Date

# Criando a classe usuário:
class usuario(Base):
    
    __tablename__= "usuarios" # criando a tabela usuarios
    
    id = Column(Integer, primary_key=True, autoincrement=True) # id única da transação, o primary key impede que hajam duas chaves iguais e o autoincrement adiciona 1 a cada novo usuário
    nome = Column(String) # nome do usuário
    email = Column(String, unique=True, nullable=False) # email do usuário
    senha_hash = Column(String) # código hash da senha do usuário
    tipo_usuario = Column(String) # Se o usuário é comum ou admin
    id_familia = Column(Integer) # id da família, se houver.

    def __init__(self, nome, email, senha_plana, tipo_usuario= "comum", id_familia= None):
        self.nome = nome
        self.email = email
        self.tipo_usuario = tipo_usuario
        self.id_familia = id_familia

        # configurando o hash da senha:
        salt = bcrypt.gensalt()
        self.senha_hash = bcrypt.hashpw(senha_plana.encode('utf-8'),salt).decode('utf-8')
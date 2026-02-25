from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, Float, String, DateTime

# configurando a engine do BD
DATABASE_URL = "sqlite:///database/meudinheiro.db"  # quando migrarmos para o postgreSQL, essa variável será alterada 
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread" : False})

# Criando a session, que usaremos para enviar comandos:
SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine, expire_on_commit=False)

# A 'Base' é a "mãe" de todas as classes (Transacao, Conta, etc)
# Todas as classes que herdarem dela serão transformadas em tabelas no banco
Base = declarative_base()


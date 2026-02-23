from sqlalchemy import Column, Integer, Float, String, DateTime, Date
from database.config import Base, SessionLocal

# Criando a classe contas:

class Conta(Base):

    __tablename__ = "conta" #criando a tabela conta.

    id = Column(Integer, primary_key=True, autoincrement=True)
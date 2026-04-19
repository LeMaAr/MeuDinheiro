from database.config  import Base, SessionLocal 
from database.mixin import CRUDMixin
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

"""############################### FAMILIAS ########################################################"""
class Familia(Base, CRUDMixin):

#region TABELA E RELACIONAMENTOS:    
    __tablename__= "familias" # criando a tabela familia
    
    # campos da tabela:
    id_familia = Column(Integer, primary_key=True, autoincrement=True) # id única da familia, o primary key impede que hajam duas chaves iguais e o autoincrement adiciona 1 a cada novo usuário
    nome_familia = Column(String, nullable=False) # nome da familia
        
    # relacionamentos com outras tabelas:    
    membros = relationship("Usuario", back_populates="familia")                                            # CONFERIDO
    contas = relationship("Conta", back_populates="familia")                                               # CONFERIDO
    convites = relationship("ConviteFamilia", back_populates="familia", cascade="all, delete-orphan")      # CONFERIDO
    metas = relationship("Meta", back_populates="familia", cascade="all, delete-orphan")                   # CONFERIDO

#endregion

#region INIT:
    def __init__(self, nome_familia):
        self.nome_familia = nome_familia
#endregion
    

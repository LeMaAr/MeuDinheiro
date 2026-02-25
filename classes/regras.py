from database.config import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

""" Essa classe vai ser responsável por automatizar a escolha de tags durante a importação de arquivos csv. 
Ela cria uma tabela no bd com palavras-chave associadas às suas respectivas tags"""

class RegraTag(Base):
    __tablename__ = "regras_tags"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    palavra_chave = Column(String, unique=True, nullable=False) # Ex: 'UBER'
    tag_destino = Column(String, nullable=False) # Ex: 'Transporte'
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))
    
    # Relacionamento para facilitar buscas
    usuario = relationship("Usuario", back_populates="regras")

    def __init__(self, palavra_chave, tag_destino, id_usuario):
        self.palavra_chave = palavra_chave.upper() # Padronizamos para maiúsculo para facilitar a busca
        self.tag_destino = tag_destino
        self.id_usuario = id_usuario
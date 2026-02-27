from database.config import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

""" Essa classe vai ser responsável por automatizar a escolha de tags durante a importação de arquivos csv. 
Ela cria uma tabela no bd com palavras-chave associadas às suas respectivas tags"""

class RegraTag(Base):
    __tablename__ = "regras_tags"
    
    id = Column(Integer, primary_key=True, autoincrement=True) # id único da regra, o primary key impede que hajam mais de uma chave igual e o autoincrement adiciona 1 a cada nova regra
    palavra_chave = Column(String, unique=True, nullable=False) # palavra ou expressão que, quando encontrada no texto da transação, aciona a regra. Ex: 'uber', 'mercado', 'netflix', etc. O unique=True garante que não haja regras duplicadas para a mesma palavra-chave.
    tag_destino = Column(String, nullable=False) # tag que deve ser aplicada à transação quando a palavra-chave for encontrada. Ex: 'Transporte', 'Alimentação', 'Lazer', etc.
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario")) # id do usuário ao qual a regra pertence, para garantir que cada usuário tenha suas próprias regras personalizadas.
    
    # relacionamento com a tabela de usuários, permitindo acessar as regras de um usuário através do atributo 'regras' do objeto Usuario.
    usuario = relationship("Usuario", back_populates="regras") 

    def __init__(self, palavra_chave, tag_destino, id_usuario):
        self.palavra_chave = palavra_chave.upper() # Padronizamos para maiúsculo para facilitar a busca
        self.tag_destino = tag_destino
        self.id_usuario = id_usuario
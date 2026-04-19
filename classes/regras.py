from database.config import Base, SessionLocal
from database.mixin import CRUDMixin
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

"""############################### REGRAS TAG ########################################################"""
class RegraTag(Base, CRUDMixin):
    """ Essa classe vai ser responsável por automatizar a escolha de tags durante a importação de arquivos csv. 
    Ela cria uma tabela no bd com palavras-chave associadas às suas respectivas tags"""
    
#region TABELA E RELACIONAMENTOS:
    __tablename__ = "regras_tags"
    
    # CAMPOS DA TABELA
    id_regra = Column(Integer, primary_key=True, autoincrement=True) # id único da regra, o primary key impede que hajam mais de uma chave igual e o autoincrement adiciona 1 a cada nova regra
    palavra_chave = Column(String, nullable=False) # palavra ou expressão que, quando encontrada no texto da transação, aciona a regra. Ex: 'uber', 'mercado', 'netflix', etc. O unique=True garante que não haja regras duplicadas para a mesma palavra-chave.
    
    # CHAVES ESTRANGEIRAS
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario")) # id do usuário ao qual a regra pertence, para garantir que cada usuário tenha suas próprias regras personalizadas.
    id_categoria =  Column(Integer, ForeignKey("categorias.id_categoria"))
    id_subcategoria = Column(Integer, ForeignKey("subcategorias.id_subcategoria"))
    
    # RELACIONAMENTOS
    usuario = relationship("Usuario", back_populates="regras_tag")
    categoria = relationship("Categoria")
    subcategoria = relationship("Subcategoria")

    # RESTRIÇÃO DE UNICIDADE
    __table_args__ = (UniqueConstraint('palavra_chave', 'id_usuario', name='_palavra_chave_usuario_uc'),)
         
#endregion

#region INIT
    def __init__(self, 
                 palavra_chave, 
                 id_usuario,
                 id_categoria,
                 id_subcategoria,
                 ):
        
        self.palavra_chave = palavra_chave.upper() # Padronizamos para maiúsculo para facilitar a busca
        self.id_usuario = id_usuario
        self.id_categoria = id_categoria
        self.id_subcategoria = id_subcategoria
#endregion

#region MÉTODOS:

    @classmethod
    def buscar_regra(cls, texto_transacao, id_usuario):
        """Método de Classe responsável conferir nas regras cadastradas se o texto de entrada já existe"""

        db =  SessionLocal()

        try:
            # busca pelas regras do usuário.
            regras = db.query(cls).filter(cls.id_usuario == id_usuario).all()

            # agora verifica se alguma palavra chave está contida no texto da transação.
            for regra in regras:
                if regra.palavra_chave in texto_transacao.upper():
                    return regra # retorna a regra encontrada 

            return None # nenhuma regra encontrada
        
        finally:
            db.close()

#endregion
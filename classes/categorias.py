from database.config import Base
from database.mixin import CRUDMixin
from sqlalchemy import Column, Integer, Float, String, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from classes.transacoes import TipoTransacao
from utils.tools import gerar_cor

"""############################### CATEGORIAS ########################################################"""
class Categoria(Base, CRUDMixin):

#region TABELA E RELACIONAMENTOS:
    __tablename__ = "categorias" # criando a tabela "categorias"
    
    # CAMPOS DA TABELA:
    id_categoria = Column(Integer, primary_key=True, autoincrement=True) # id única da categoria, o primary key impede que hajam mais de uma chave igual e o autoincrement adiciona 1 a cada nova categoria
    nome = Column(String, nullable=False) # nome da categoria
    cor_hex = Column(String) # cor hexadecimal da categoria
    icone = Column(String(50)) # nome do ícone da categoria
    tipo = Column(Enum(TipoTransacao)) # tipo de transação associado a categoria
    limite_gastos_mensal = Column(Float, nullable=True) # limite de gastos mensal para a categoria, pode ser nulo caso o usuário não queira estipular um limite
    ordem_exibicao = Column(Integer, nullable=True) # campo para definir a ordem de exibição das categorias, pode ser nulo caso o usuário não queira estipular uma ordem específica
    ativa = Column(Boolean, nullable=False, default=True) # campo para indicar se a categoria está ativa ou inativa.
    
    # CHAVE ESTRANGEIRA:
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=True) # id de usuário

    # RELACIONAMENTOS:
    usuario = relationship("Usuario", back_populates="categorias") # relacionamento com a tabela de usuários
    subcategorias = relationship("Subcategoria", back_populates="categoria", cascade="all, delete-orphan") # relacionamento com a tabela de subcategorias
    transacoes = relationship("Transacao", back_populates="categoria") # relacionamento com a tabela de transações
#endregion
    
#region INIT:
    def __init__(self, 
                 nome, 
                 id_usuario = None, 
                 cor_hex = None, 
                 icone = None,
                 tipo = None,
                 limite_gastos_mensal = None,
                 ordem_exibicao = None,
                 ativa = True
                 ):
        
        self.nome = nome
        self.icone = icone if icone else "tag" # Ícone padrão caso nenhum seja fornecido
        self.id_usuario = id_usuario
        self.tipo = tipo
        
        # Se uma cor hexadecimal for fornecida, use-a; caso contrário, gere uma cor aleatória usando a função gerar_cor(). 
        # Isso permite que as categorias tenham cores personalizadas, mas também garante que cada categoria tenha uma cor distinta 
        # mesmo se o usuário não escolher uma.
        if cor_hex: 
            self.cor_hex = cor_hex
        else:
            self.cor_hex = gerar_cor()

        self.limite_gastos_mensal = limite_gastos_mensal
        self.ordem_exibicao = ordem_exibicao
        self.ativa = ativa

#endregion

"""############################### SUBCATEGORIAS #####################################################"""
class Subcategoria(Base, CRUDMixin):

#region TABELA E RELACIONAMENTOS:
    __tablename__ = "subcategorias" # criando a tabela "subcategorias"
    
    # CAMPOS DA TABELA:
    id_subcategoria = Column(Integer, primary_key=True, autoincrement=True) # id única da subcategoria, o primary key impede que hajam mais de uma chave igual e o autoincrement adiciona 1 a cada nova subcategoria
    nome = Column(String, nullable=False) # nome da subcategoria
    icone = Column(String(50)) # nome do ícone da subcategoria
    tipo = Column(Enum(TipoTransacao)) # tipo de transação associado a subcategoria
    limite_gastos_mensal = Column(Float, nullable=True) # limite de gastos mensal para a subcategoria, pode ser nulo caso o usuário não queira estipular um limite
    ordem_exibicao = Column(Integer, nullable=True) # campo para definir a ordem de exibição das categorias, pode ser nulo caso o usuário não queira estipular uma ordem específica
    ativa = Column(Boolean, nullable=False, default=True) # campo para indicar se a subcategoria está ativa ou inativa.

    # CHAVES ESTRANGEIRAS:
    id_categoria = Column(Integer, ForeignKey("categorias.id_categoria")) # id da categoria pai
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario")) # id de usuário

    # RELACIONAMENTOS:
    categoria = relationship("Categoria", back_populates="subcategorias") # relacionamento com a tabela de categorias
    usuario = relationship("Usuario", back_populates="subcategorias") # relacionamento com a tabela de usuários
    transacoes = relationship("Transacao", back_populates="subcategoria") # relacionamento com a tabela de transações
#endregion

#region INIT:
    def __init__(self, 
                 nome, 
                 id_categoria, 
                 id_usuario,
                 icone = None,
                 tipo = None,
                 limite_gastos_mensal = None,
                 ordem_exibicao = None,
                 ativa = True
                 ):

        self.nome = nome
        self.id_categoria = id_categoria
        self.id_usuario = id_usuario
        self.tipo = tipo
        self.icone = icone if icone else "tag" # Ícone padrão caso nenhum seja fornecido
        self.limite_gastos_mensal = limite_gastos_mensal   
        self.ordem_exibicao = ordem_exibicao
        self.ativa = ativa
#endregion

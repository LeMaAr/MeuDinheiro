from database.config import Base, SessionLocal
from sqlalchemy import Column, Integer, Float, String, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
import random


# classes responsáveis pela criação da tabela categorias no banco de dados

class Categoria(Base):

    __tablename__ = "categorias" # criando a tabela "categorias"
    
    id_categoria = Column(Integer, primary_key=True, autoincrement=True) # id única da categoria, o primary key impede que hajam mais de uma chave igual e o autoincrement adiciona 1 a cada nova categoria
    nome = Column(String, nullable=False) # nome da categoria
    cor_hex = Column(String) # cor hexadecimal da categoria
    icone = Column(String(50)) # nome do ícone da categoria
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario")) # id de usuário

    usuario = relationship("Usuario", back_populates="categorias") # relacionamento com a tabela de usuários
    subcategorias = relationship("Subcategoria", back_populates="categoria") # relacionamento com a tabela de subcategorias
    transacoes = relationship("Transacao", back_populates="categoria") # relacionamento com a tabela de transações

    # métodos da classe:

    def __init__(self, nome: str, id_usuario: int, cor_hex: str = None, icone: str = None):
        
        self.nome = nome
        self.icone = icone if icone else "tag" # Ícone padrão caso nenhum seja fornecido
        self.id_usuario = id_usuario
        # Se uma cor hexadecimal for fornecida, use-a; caso contrário, gere uma cor aleatória usando a função gerar_cor(). 
        # Isso permite que as categorias tenham cores personalizadas, mas também garante que cada categoria tenha uma cor distinta 
        # mesmo se o usuário não escolher uma.
        if cor_hex: 
            self.cor_hex = cor_hex
        else:
            self.cor_hex = gerar_cor()

    def add_categoria(self):
          
        db = SessionLocal() # Estabelece a conexão com o banco de Dados.
        
        try:
            db.add(self) # adiciona a transação atual no Banco de Dados
            db.commit() # Salva a transação permanentemente
            db.refresh(self) # atualiza o objeto criado com a ID gerada pelo BD
            print(f"Categoria {self.id_categoria} incluída com sucesso!") # imprime uma mensagem de conclusão.

        except Exception as e:
            db.rollback() # caso haja algum erro, desfaz a operação.
            print (f"Erro ao gravar a categoria: {e}") # imprime uma mensagem de conclusão.
            raise e # lança o erro para fora da função.

        finally:
            db.close() # fecha a conexão

    def mod_categoria(self):

        db = SessionLocal() # Estabelece a conexão com o banco de Dados.
        
        try:
            db.merge(self) # atualiza a categoria atual no Banco de Dados
            db.commit() # Salva a categoria permanentemente
            print(f"Categoria {self.id_categoria} modificada com sucesso!") # imprime uma mensagem de conclusão.

        except Exception as e:
            db.rollback() # caso haja algum erro, desfaz a operação.
            print (f"Erro ao modificar a categoria: {e}") # imprime uma mensagem de conclusão.
            raise e # lança o erro para fora da função.

        finally:
            db.close() # fecha a conexão

    def del_categoria(self):

        db = SessionLocal() # Estabelece a conexão com o banco de Dados.
        
        try:
            db.delete(self) # deleta a categoria atual no Banco de Dados
            db.commit() # Salva a categoria permanentemente
            print(f"Categoria {self.id_categoria} deletada com sucesso!") # imprime uma mensagem de conclusão.

        except Exception as e:
            db.rollback() # caso haja algum erro, desfaz a operação.
            print (f"Erro ao deletar a categoria: {e}") # imprime uma mensagem de conclusão.
            raise e # lança o erro para fora da função.

        finally:
            db.close() # fecha a conexão

class Subcategoria(Base):

    __tablename__ = "subcategorias" # criando a tabela "subcategorias"
    
    id_subcategoria = Column(Integer, primary_key=True, autoincrement=True) # id única da subcategoria, o primary key impede que hajam mais de uma chave igual e o autoincrement adiciona 1 a cada nova subcategoria
    nome = Column(String, nullable=False) # nome da subcategoria
    icone = Column(String(50)) # nome do ícone da subcategoria
    id_categoria = Column(Integer, ForeignKey("categorias.id_categoria")) # id da categoria pai
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario")) # id de usuário

    categoria = relationship("Categoria", back_populates="subcategorias") # relacionamento com a tabela de categorias
    usuario = relationship("Usuario", back_populates="subcategorias") # relacionamento com a tabela de usuários
    transacoes = relationship("Transacao", back_populates="subcategoria") # relacionamento com a tabela de transações

        # métodos da classe:

    def __init__(self, nome: str, id_categoria: int, id_usuario: int):
        self.nome = nome
        self.id_categoria = id_categoria
        self.id_usuario = id_usuario

    def add_subcategoria(self):
          
        db = SessionLocal() # Estabelece a conexão com o banco de Dados.
        
        try:
            db.add(self) # adiciona a transação atual no Banco de Dados
            db.commit() # Salva a transação permanentemente
            db.refresh(self) # atualiza o objeto criado com a ID gerada pelo BD
            print(f"Subcategoria {self.id_subcategoria} incluída com sucesso!") # imprime uma mensagem de conclusão.

        except Exception as e:
            db.rollback() # caso haja algum erro, desfaz a operação.
            print (f"Erro ao gravar a categoria: {e}") # imprime uma mensagem de conclusão.
            raise e # lança o erro para fora da função.

        finally:
            db.close() # fecha a conexão

    def mod_subcategoria(self):

        db = SessionLocal() # Estabelece a conexão com o banco de Dados.
        
        try:
            db.merge(self) # atualiza a subcategoria atual no Banco de Dados
            db.commit() # Salva a subcategoria permanentemente
            print(f"Subcategoria {self.id_subcategoria} modificada com sucesso!") # imprime uma mensagem de conclusão.

        except Exception as e:
            db.rollback() # caso haja algum erro, desfaz a operação.
            print (f"Erro ao modificar a subcategoria: {e}") # imprime uma mensagem de conclusão.
            raise e # lança o erro para fora da função.

        finally:
            db.close() # fecha a conexão

    def del_subcategoria(self):

        db = SessionLocal() # Estabelece a conexão com o banco de Dados.
        
        try:
            db.delete(self) # deleta a subcategoria atual no Banco de Dados
            db.commit() # Salva a subcategoria permanentemente
            print(f"Subcategoria {self.id_subcategoria} deletada com sucesso!") # imprime uma mensagem de conclusão.

        except Exception as e:
            db.rollback() # caso haja algum erro, desfaz a operação.
            print (f"Erro ao deletar a subcategoria: {e}") # imprime uma mensagem de conclusão.
            raise e # lança o erro para fora da função.

        finally:
            db.close() # fecha a conexão

def gerar_cor():
    #  define uma paleta de cores pré-definida, onde cada cor é representada por seu código hexadecimal. 
    # A função random.choice() é usada para selecionar aleatoriamente uma cor da paleta, 
    # garantindo que as categorias criadas tenham cores variadas e visualmente distintas.

    paleta = ["#E83442", "#AD1457", "#6A1B9A", "#4527A0", "#283593", 
              "#1565C0", "#0277BD", "#00838F", "#00695C", "#2E7D32"
              "#558B2F", "#9E9D24", "#F9A825", "#FF8F00", "#D84315", "#ED1111"]
    
    return random.choice(paleta)
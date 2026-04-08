from database.config  import Base, SessionLocal 
from sqlalchemy import Column, Integer, Float, String, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship

class Familia(Base):
    
    __tablename__= "familias" # criando a tabela familia
    
    id_familia = Column(Integer, primary_key=True, autoincrement=True) # id única da familia, o primary key impede que hajam duas chaves iguais e o autoincrement adiciona 1 a cada novo usuário
    nome_familia = Column(String, nullable=False) # nome da familia
        
    membros = relationship("Usuario", back_populates="familia")
    contas = relationship("Conta", back_populates="familia")
    convites = relationship("ConviteFamilia", back_populates="familia", cascade="all, delete-orphan") # relacionamento com a tabela convites_familia, com cascade para deletar os convites relacionados quando a família for deletada
    
    def __init__(self, nome_familia):
        self.nome_familia = nome_familia
    
    
    def add_familia(self):
        db = SessionLocal() # Estabelece a conexão com o banco de Dados.

        try:
            db.add(self) # adiciona o usuário ao bd
            db.commit() # comita a mudança
            db.refresh(self) # atualiza o bd
            print (f"Família {self.id_familia} adicionada com sucesso!") # imprime uma mensagem de conclusão.
        
        except Exception as e:
            db.rollback() # caso haja algum erro, desfaz a operação.
            print (f"Erro ao adicionar a família {self.id_familia}: {e}") # imprime uma mensagem de conclusão.
            raise e # lança o erro para fora da função.

        finally:
            db.close() # fecha a conexão com o BD

    def del_familia(self):
        db = SessionLocal() # Estabelece a conexão com o banco de Dados.

        try:
            db.delete(self) # deleta o usuário do DB
            db.commit() # faz a alteração permanentemente
            print(f"Família {self.id_familia} excluído com sucesso!") # imprime uma mensagem de conclusão.

        except Exception as e:
            db.rollback() # caso haja algum erro, desfaz a operação.
            print (f"Erro ao excluir a família{self.id_familia}: {e}") # imprime uma mensagem de conclusão.
            raise e # lança o erro para fora da função.
        
        finally:
            db.close() # fecha a conexão com o BD

    def mod_familia(self):

        db = SessionLocal() # Estabelece a conexão com o banco de Dados.
        
        try:
            db.merge(self) # mescla o estado atual do objeto com seu equivalente no BD
            db.commit() # salva a alteração no bd
            db.refresh(self) # atualiza o bd com a alteração
            print (f"Dados da família{self.id_familia} alterados com sucesso.") # imprime a msg de conclusão
        
        except Exception as e:
            db.rollback() # caso haja algum erro, desfaz a operação.
            print (f"Erro ao alterar os dados: {e}") # imprime uma mensagem de conclusão.
            raise e # lança o erro para fora da função.

        finally:
            db.close() # fecha a conexão com o BD
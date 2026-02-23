from datetime import datetime, date
from typing import List, Optional
from database.config import Base, SessionLocal
from sqlalchemy import Column, Integer, Float, String, DateTime, Date, ForeignKey

# Definindo a classe transações.

class Transacao(Base):

    __tablename__ = "transacoes" # criando a tabela "transacoes"
    
    id = Column(Integer, primary_key=True, autoincrement=True) # id única da transação, o primary key impede que hajam mais de uma chave igual e o autoincrement adiciona 1 a cada nova transação
    valor = Column(Float, nullable=False) # valor da transação
    tipo = Column(String) # Receita ou Despesa
    categoria = Column(String) # categoria da transação. Ex.: Moradia, Transporte, Saúde, etc.
    subcategoria = Column(String) # subcategorias da transação. Ex.: aluguel, conta de luz, conta de água, etc.
    data = Column(DateTime, default=datetime.now) # data da transação 
    id_conta = Column(Integer, ForeignKey("contas.id_conta")) # id da conta no banco
    descricao = Column(String) # Campo curto para o usuário adicionar algum comentário sobre a transação
    local = Column(String) # Local onde a transação ocorreu. Ex.: Mercado X, Padaria Y, etc
    tipo_registro = Column(String) # identificador de transação comum ou recorrente
    
    __mapper_args__ = {
        'polymorphic_on': tipo_registro,
        'polymorphic_identity': 'comum'
    }

    # métodos da classe:

    def __init__(self, 
                 valor: float,
                 tipo: str,
                 categoria: str, 
                 idconta: int,
                 subcategoria: str = None, 
                 data: Optional[datetime] = None, 
                 descricao: Optional[str] = None, 
                 local: str = ""
                 ):
        
        # atributos da classe: 
                                
        if data is None:
            self.data = datetime.now()
        else:
            self.data = data
        
        self.valor = valor
        self.tipo = tipo
        self.categoria = categoria
        self.subcategoria = subcategoria
        self.idconta = idconta
        self.descricao = descricao
        self.local = local
    
    def add_transacao(self):
        
        db = SessionLocal() # Estabelece a conexão com o banco de Dados.
        
        try:
            db.add(self) # adiciona a transação atual no Banco de Dados
            db.commit() # Salva a transação permanentemente
            db.refresh(self) # atualiza o objeto criado com a ID gerada pelo BD
            print(f"Transação {self.id} incluída com sucesso!") # imprime uma mensagem de conclusão.

        except Exception as e:
            db.rollback() # caso haja algum erro, desfaz a operação.
            print (f"Erro ao gravar a transação: {e}") # imprime uma mensagem de conclusão.
            raise e # lança o erro para fora da função.

        finally:
            db.close() # fecha a conexão

    def del_transacao(self):

        db = SessionLocal() # Estabelece a conexão com o banco de Dados.

        try:
            db.delete(self) # deleta a transação atual no Banco de Dados
            db.commit() # Salva a transação permanentemente
            print(f"Transação {self.id} excluída com sucesso!") # imprime uma mensagem de conclusão.
                    

        except Exception as e:
            db.rollback() # caso haja algum erro, desfaz a operação.
            print (f"Erro ao excluir a transação: {e}") # imprime uma mensagem de conclusão.
            raise e # lança o erro para fora da função.

        finally:
            db.close() # fecha a conexão

    def mod_transacao(self):

        db = SessionLocal() # Estabelece a conexão com o banco de Dados.
        
        try:
            db.merge(self) # mescla o estado atual do objeto com seu equivalente no BD
            db.commit() # salva a alteração no bd
            db.refresh(self) # atualiza o bd com a alteração
            print (f"Transação {self.id} alterada com sucesso.") # imprime a msg de conclusão
        
        except Exception as e:
            db.rollback() # caso haja algum erro, desfaz a operação.
            print (f"Erro ao alterar a transação: {e}") # imprime uma mensagem de conclusão.
            raise e # lança o erro para fora da função.

        finally:
            db.close() # fecha a conexão com o BD


class TransacaoRecorrente(Transacao):

    # Atributos específicos:
    data_inicio = Column(Date) # data do início das cobranças
    ciclo = Column(String) # periodicidade
    data_termino = Column(Date) # data do vencimento da última cobrança

    __mapper_args__ = {
        'polymorphic_identity': 'recorrente'
    }

    def __init__(self, 
                 valor: float, 
                 tipo: str, 
                 categoria: str, 
                 idconta : int,
                 data_inicio: date, 
                 ciclo: str, 
                 descricao: str = None,
                 local: str = None,
                 subcategoria : str = None,
                 data_termino: date = None, 
                 data: date = None
                 ):
        
        # O super() chama o __init__ da classe pai (Transacao)
        
        super().__init__(valor=valor, tipo=tipo, categoria=categoria, idconta=idconta, subcategoria=subcategoria, descricao=descricao, local=local, data = data)
        self.data_inicio = data_inicio
        self.ciclo = ciclo
        self.data_termino = data_termino
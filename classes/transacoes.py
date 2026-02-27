from datetime import datetime, date
from typing import List, Optional
from database.config import Base, SessionLocal
from sqlalchemy import Column, Integer, Float, String, DateTime, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship

# Definindo a classe transações.

class Transacao(Base):

    __tablename__ = "transacoes" # criando a tabela "transacoes"
    
    # definindo as colunas da tabela:
    id_transacao = Column(Integer, primary_key=True, autoincrement=True) # id única da transação, o primary key impede que hajam mais de uma chave igual e o autoincrement adiciona 1 a cada nova transação
    valor = Column(Float, nullable=False) # valor da transação
    tipo = Column(String) # tipo da transação, se é Receita , Despesa , Transferência (como para mesadas ou movimentação entre contas, por exemplo) ou Investimento
    tag = Column(String) # tags para organizar os gráficos
    data = Column(DateTime, default=datetime.now) # data e hora da transação, o default define que, caso o usuário não informe uma data, a data atual será usada
    descricao = Column(String) # Campo curto para o usuário adicionar algum comentário sobre a transação
    local = Column(String) # Local onde a transação ocorreu. Ex.: Mercado X, Padaria Y, etc
    essencial = Column(Boolean, default=False) # se a transação é essencial ou não. Será usada para que o usuário possa filtrar os gráficos e cálculos para mostrar apenas as transações essenciais, por exemplo, para ter uma noção melhor de quanto ele gasta com coisas essenciais e quanto gasta com coisas supérfluas.
    tipo_registro = Column(String) # identificador de transação comum ou recorrente
    recorrente = Column(Boolean, default=False) # se a transação é recorrente ou não
    quitada = Column(Boolean, default=True) # se a transação já foi paga ou não. Será usada para as transações recorrentes, para que o usuário possa marcar como paga a transação do mês atual, por exemplo.
    ignore = Column(Boolean, default=False) # se a transação deve ser ignorada nos gráficos e cálculos. Será usada para qualquer transação, para que o usuário possa marcar como ignorada alguma movimentação, como quando o usuário tem alguma despesa de um familiar em sua conta e ela não é necessariamente uma despesa do usuário.
    automatico = Column(Boolean, default=False) # se a transação foi criada automaticamente a partir da leitura de um SMS, por exemplo. Será usada para que o usuário possa filtrar as transações criadas automaticamente e revisar se estão corretas, para depois marcar como automáticas e não precisar revisar toda vez.
    texto_bruto = Column(String) # campo para armazenar texto para a função de leitura de sms futura. A função deverá ser capaz de ler o texto bruto e extrair as informações necessárias para criar uma transação a partir dele. 
    id_recorrencia = Column(Integer) # id da recorrência, caso a transação seja recorrente. Será usado para vincular as transações geradas a partir de uma mesma recorrência.
    data_inicio = Column(Date, nullable=True) # data do início das cobranças, para as transações recorrentes. Pode ser nula, para as transações comuns ou para as recorrências que não têm uma data de início definida, como uma mensalidade de academia, por exemplo, que o usuário começou a pagar há um tempo e não tem certeza de quando começou a pagar.
    ciclo = Column(String, nullable=True) # periodicidade das cobranças, para as transações recorrentes. Ex.: mensal, semanal, anual, etc. Pode ser nulo, para as transações comuns ou para as recorrências que não têm um ciclo definido, como uma mensalidade de academia que é cobrada todo mês, mas o usuário não tem certeza de qual é o ciclo, ou seja, se é mensal, bimestral, etc.
    data_termino = Column(Date, nullable=True) # data do vencimento da última cobrança, para as transações recorrentes. Pode ser nula, para as recorrências que não têm data de término definida, como uma mensalidade de academia, por exemplo.
 
    # chaves estrangeiras para relacionar a transação com outras tabelas:
    id_categoria = Column(Integer, ForeignKey("categorias.id_categoria")) # categoria da transação. Ex.: Moradia, Transporte, Saúde, etc.
    id_subcategoria = Column(Integer, ForeignKey("subcategorias.id_subcategoria")) # subcategorias da transação. Ex.: aluguel, conta de luz, conta de água, etc.
    id_conta = Column(Integer, ForeignKey("contas.id_conta")) # id da conta no banco
    id_usuario = Column (Integer, ForeignKey("usuarios.id_usuario")) # id de usuário
    
    # relacionamentos com outras tabelas: 
    categoria = relationship("Categoria", back_populates="transacoes") # relacionamento com a tabela de categorias
    subcategoria = relationship("Subcategoria", back_populates="transacoes") # relacionamento com a tabela de subcategorias
    conta = relationship("Conta", back_populates="transacoes")  # relacionamento com a tabela de contas
    usuario = relationship("Usuario", back_populates="transacoes") # relacionamento com a tabela de usuários
    
    
    def __init__(self, 
                 tipo_registro: str,
                 valor: float, 
                 tipo: str, 
                 id_conta: int, 
                 id_usuario: int,
                 essencial: bool = False,
                 automatico: bool = False,
                 data_inicio: Optional[date] = None, 
                 ciclo: Optional[str] = None, 
                 data_termino: Optional[date] = None,
                 texto_bruto: str = None,
                 ignore: bool = False,
                 quitada: bool = True,
                 id_recorrencia: int = None,
                 id_categoria: int = None, 
                 id_subcategoria: int = None,
                 recorrente: bool = False,
                 tag : str = None, 
                 data: Optional[datetime] = None, 
                 descricao: Optional[str] = None, 
                 local: str = "" 
                 ):
        
        # atributos da classe: 

        self.tipo_registro = tipo_registro                        
        self.valor = valor  
        self.tipo = tipo
        self.id_conta = id_conta
        self.id_usuario = id_usuario
        self.essencial = essencial
        self.automatico = automatico
        self.data_inicio = data_inicio if data_inicio else date.today()
        self.ciclo = ciclo
        self.data_termino = data_termino
        self.texto_bruto = texto_bruto
        self.ignore = ignore
        self.quitada = quitada
        self.id_recorrencia = id_recorrencia
        self.id_categoria = id_categoria
        self.id_subcategoria = id_subcategoria
        self.recorrente = recorrente
        self.tag = tag
        if data is None:
            self.data = datetime.now()
        else:
            self.data = data
        self.descricao = descricao
        self.local = local
    
    def add_transacao(self):
        
        db = SessionLocal() # Estabelece a conexão com o banco de Dados.
        
        try:
            db.add(self) # adiciona a transação atual no Banco de Dados
            db.commit() # Salva a transação permanentemente
            db.refresh(self) # atualiza o objeto criado com a ID gerada pelo BD
            print(f"Transação {self.id_transacao} incluída com sucesso!") # imprime uma mensagem de conclusão.

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
            print(f"Transação {self.id_transacao} excluída com sucesso!") # imprime uma mensagem de conclusão.
                    

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
            print (f"Transação {self.id_transacao} alterada com sucesso.") # imprime a msg de conclusão
        
        except Exception as e:
            db.rollback() # caso haja algum erro, desfaz a operação.
            print (f"Erro ao alterar a transação: {e}") # imprime uma mensagem de conclusão.
            raise e # lança o erro para fora da função.

        finally:
            db.close() # fecha a conexão com o BD


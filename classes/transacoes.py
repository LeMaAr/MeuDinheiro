from datetime import datetime, date
import enum
from typing import List, Optional
from database.config import Base, SessionLocal
from sqlalchemy import Column, Integer, Float, String, DateTime, Date, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
import hashlib

#region ENUMS
class TipoTransacao(str, enum.Enum):
    RECEITA = "receita"                  # para receitas comuns, como salário, venda de um item, etc.
    DESPESA = "despesa"                  # para despesas comuns, como compras, contas, etc.
    TRANSFERENCIA = "transferencia"      # para transferências entre contas do próprio usuário, como quando o usuário remaneja dinheiro de uma conta para outra.
    COMPRA = "compra"                    # para compras de ativos, como ações, fundos imobiliários, etc.
    VENDA = "venda"                      # para vendas de ativos, como ações, fundos imobiliários, etc.
    DIVIDENDO = "dividendo"              # para recebimento de dividendos de ativos, como ações, fundos imobiliários, etc.

class TipoRegistro(str, enum.Enum):
    COMUM = "comum"
    RECORRENTE = "recorrente"
    PARCELADO = "parcelado"
    EXTORNO = "extorno"

class StatusConferencia(str, enum.Enum):
    PENDENTE = "pendente"
    CONFERIDO = "conferido"
    DISCREPANCIA = "discrepancia"

#endregion

"""############################### TRANSAÇÕES ########################################################"""
class Transacao(Base):

#region TABELA E COLUNAS
    __tablename__ = "transacoes" # criando a tabela "transacoes"

    # CAMPOS DA TABELA:
    id_transacao = Column(Integer, primary_key=True, autoincrement=True) # id única da transação, o primary key impede que hajam mais de uma chave igual e o autoincrement adiciona 1 a cada nova transação
    valor = Column(Float, nullable=False) # valor da transação
    tipo = Column(Enum(TipoTransacao)) # tipo da transação, se é Receita , Despesa , Transferência (como para mesadas ou movimentação entre contas, por exemplo) ou Investimento
    tag = Column(String) # tags para organizar os gráficos
    data = Column(DateTime, default=datetime.now) # data e hora da transação, o default define que, caso o usuário não informe uma data, a data atual será usada
    descricao = Column(String) # Campo curto para o usuário adicionar algum comentário sobre a transação
    local = Column(String) # Local onde a transação ocorreu. Ex.: Mercado X, Padaria Y, etc
    essencial = Column(Boolean, default=False) # se a transação é essencial ou não. Será usada para que o usuário possa filtrar os gráficos e cálculos para mostrar apenas as transações essenciais, por exemplo, para ter uma noção melhor de quanto ele gasta com coisas essenciais e quanto gasta com coisas supérfluas.
    quantidade = Column(Integer, nullable=True) # quantidade de itens relacionados à transação. Será usada primariamente para transações de compra de ativos como ações em que a quantidade é relevante para calcular o valor investido total.
    tipo_registro = Column(Enum(TipoRegistro), default=TipoRegistro.COMUM) # identificador de transação comum, recorrente, parcelada ou extorno.
    quitada = Column(Boolean, default=True) # se a transação já foi paga ou não. Será usada para as transações recorrentes, para que o usuário possa marcar como paga a transação do mês atual, por exemplo.
    ignore = Column(Boolean, default=False) # se a transação deve ser ignorada nos gráficos e cálculos. Será usada para qualquer transação, para que o usuário possa marcar como ignorada alguma movimentação, como quando o usuário tem alguma despesa de um familiar em sua conta e ela não é necessariamente uma despesa do usuário.
    automatico = Column(Boolean, default=False) # se a transação foi criada automaticamente a partir da leitura de um SMS, por exemplo. Será usada para que o usuário possa filtrar as transações criadas automaticamente e revisar se estão corretas, para depois marcar como automáticas e não precisar revisar toda vez.
    texto_bruto = Column(String) # campo para armazenar texto para a função de leitura de sms futura. A função deverá ser capaz de ler o texto bruto e extrair as informações necessárias para criar uma transação a partir dele. 
    id_recorrencia = Column(Integer) # id da recorrência, caso a transação seja recorrente. Será usado para vincular as transações geradas a partir de uma mesma recorrência.
    data_inicio = Column(Date, nullable=True) # data do início das cobranças, para as transações recorrentes. Pode ser nula, para as transações comuns ou para as recorrências que não têm uma data de início definida, como uma mensalidade de academia, por exemplo, que o usuário começou a pagar há um tempo e não tem certeza de quando começou a pagar.
    ciclo = Column(String, nullable=True) # periodicidade das cobranças, para as transações recorrentes. Ex.: mensal, semanal, anual, etc. Pode ser nulo, para as transações comuns ou para as recorrências que não têm um ciclo definido, como uma mensalidade de academia que é cobrada todo mês, mas o usuário não tem certeza de qual é o ciclo, ou seja, se é mensal, bimestral, etc.
    data_termino = Column(Date, nullable=True) # data do vencimento da última cobrança, para as transações recorrentes. Pode ser nula, para as recorrências que não têm data de término definida, como uma mensalidade de academia, por exemplo.
    moeda = Column(String, default="BRL") # moeda da transação, para o caso de o usuário querer usar outra moeda além do Real, como o Dólar, por exemplo. O default é BRL, mas o usuário pode escolher outra moeda, como USD, EUR, etc.
    hash_unico = Column(String, unique=True) # hash único para cada transação, gerado a partir de suas informações, para evitar que haja transações duplicadas, principalmente a partir da leitura de SMS, onde pode haver o risco de ler o mesmo SMS mais de uma vez e criar transações duplicadas. O hash pode ser gerado a partir do valor, data, descrição e local da transação, por exemplo, para garantir que cada transação tenha um hash único que a identifique de forma exclusiva.
    status_conferencia = Column(Enum(StatusConferencia), default=StatusConferencia.PENDENTE) # status da conferência da transação, para que o usuário possa marcar se a transação já foi conferida, se está pendente de conferência ou se há alguma discrepância na conferência, como quando o valor da transação no extrato do banco é diferente do valor registrado na transação, por exemplo. 

    # CHAVES ESTRANGEIRAS:
    id_categoria = Column(Integer, ForeignKey("categorias.id_categoria")) # categoria da transação. Ex.: Moradia, Transporte, Saúde, etc.
    id_subcategoria = Column(Integer, ForeignKey("subcategorias.id_subcategoria")) # subcategorias da transação. Ex.: aluguel, conta de luz, conta de água, etc.
    id_conta = Column(Integer, ForeignKey("contas.id_conta")) # id da conta relacionada à transação, para que seja possível relacionar a transação com uma conta específica, como a conta corrente do usuário, por exemplo.
    id_usuario = Column (Integer, ForeignKey("usuarios.id_usuario")) # id de usuário relacionado à transação, para que seja possível relacionar a transação com um usuário específico, como o próprio usuário do sistema, por exemplo.
    id_ativo = Column(Integer, ForeignKey("ativos.id_ativo"), nullable=True) # id do ativo, caso a transação esteja relacionada a um ativo, como uma compra ou venda de um ativo.
    id_meta = Column(Integer, ForeignKey("metas.id_meta"), nullable=True) # id da meta, caso a transação esteja relacionada a uma meta, como uma transação que foi criada para acompanhar o progresso de uma meta.

    # RELACIONAMENTOS COM OUTRAS TABELAS: 
    categoria = relationship("Categoria", back_populates="transacoes") # relacionamento com a tabela de categorias.             #
    subcategoria = relationship("Subcategoria", back_populates="transacoes") # relacionamento com a tabela de subcategorias.    #
    conta = relationship("Conta", back_populates="transacoes")  # relacionamento com a tabela de contas.                        # CONFERIDO
    usuario = relationship("Usuario", back_populates="transacoes") # relacionamento com a tabela de usuários.                   # CONFERIDO
    ativo = relationship("Ativo", back_populates="transacoes") # relacionamento com a tabela de ativos.                         #   
    meta = relationship("Meta", back_populates="transacoes") # relacionamento com a tabela de metas.                            # CONFERIDO
#endregion    
    
#region INIT    
    def __init__(self,
                 valor, 
                 tipo, 
                 id_conta, 
                 id_usuario,
                 quantidade = None,
                 moeda = "BRL",
                 hash_unico = None,
                 status_conferencia = StatusConferencia.PENDENTE,
                 essencial = False,
                 automatico = False,
                 tipo_registro = TipoRegistro.COMUM,
                 data_inicio = None, 
                 ciclo = None, 
                 data_termino = None,
                 texto_bruto = None,
                 ignore = False,
                 quitada = True,
                 id_recorrencia = None,
                 id_categoria = None, 
                 id_subcategoria = None,
                 id_meta = None,
                 tag = None, 
                 data = None, 
                 descricao = None, 
                 local = "" 
                 ):
        
        # atributos da classe: 
                       
        self.valor = valor  
        self.tipo = tipo
        self.id_conta = id_conta
        self.id_usuario = id_usuario
        self.quantidade = quantidade
        self.moeda = moeda
        
        # se a data não for fornecida, a data atual será usada, garantindo que a transação seja registrada com a data atual caso o usuário não especifique uma data diferente.
        if data is None:
            self.data = datetime.now()
        else:
            self.data = data
        
        # para as transações recorrentes, se a data_inicio não for fornecida, a data atual será usada como data de início, 
        # garantindo que a recorrência comece a partir da data atual caso o usuário não especifique uma data de início diferente.
        self.data_inicio = data_inicio if data_inicio else datetime.now()

        self.descricao = descricao
        self.local = local
        self.status_conferencia = status_conferencia
        self.essencial = essencial
        self.automatico = automatico
        self.tipo_registro = tipo_registro 
        self.ciclo = ciclo
        self.data_termino = data_termino
        self.texto_bruto = texto_bruto
        self.ignore = ignore
        self.quitada = quitada
        self.id_recorrencia = id_recorrencia
        self.id_categoria = id_categoria
        self.id_subcategoria = id_subcategoria
        self.id_meta = id_meta
        self.tag = tag

        # se o hash_unico não for fornecido, cria um hash único a partir das informações da transação usando a função criar_hash_unico. 
        # Isso garante que cada transação tenha um hash único, mesmo que o usuário não forneça um hash específico.
        if not hash_unico:
            self.criar_hash_unico()
        else:
            self.hash_unico = hash_unico

#endregion

#region FUNÇÕES DA CLASSE    

    @property
    def preco_unitario(self):
        # propriedade para calcular o preço unitário dos itens relacionados à transação, dividindo o valor total da transação pela quantidade de itens, caso a quantidade seja fornecida.
        # Essa propriedade é útil para transações de compra de ativos, como ações, em que o preço unitário é relevante para calcular o valor investido total.
        return self.valor / self.quantidade if self.quantidade else None
    
    def criar_hash_unico(self):
        # função para criar um hash único para a transação, a partir de suas informações, para evitar que haja transações duplicadas, principalmente a partir da leitura de SMS, 
        # onde pode haver o risco de ler o mesmo SMS mais de uma vez e criar transações duplicadas. O hash pode ser gerado a partir do valor, data, descrição e local da transação, 
        # por exemplo, para garantir que cada transação tenha um hash único que a identifique de forma exclusiva.
        hash_input = f"{self.valor}-{self.data.strftime('%Y-%m-%d %H:%M:%S')}-{self.descricao}-{self.local}"
        self.hash_unico = hashlib.sha256(hash_input.encode()).hexdigest()

    def verificar_hash_unico(self):
        # função para verificar se já existe uma transação com o mesmo hash único no banco de dados, para evitar a criação de transações duplicadas. 
        # A função consulta o banco de dados para verificar se já existe uma transação com o mesmo hash_unico e retorna True se encontrar uma transação com o mesmo hash, 
        # indicando que a transação é duplicada, ou False se não encontrar, indicando que a transação é única e pode ser criada.

        db = SessionLocal() # Estabelece a conexão com o banco de Dados.
        try:
            transacao_existente = db.query(Transacao).filter_by(hash_unico=self.hash_unico).first()
            return transacao_existente is not None
        
        except Exception as e:
            print(f"Erro ao verificar hash único: {e}")
            raise e
        
        finally:
            db.close() # fecha a conexão com o BD

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
#endregion

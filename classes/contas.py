from sqlalchemy import Column, Integer, Float, String, DateTime, Date, ForeignKey, Boolean, Enum
from database.config import Base, SessionLocal
from sqlalchemy.orm import relationship
import datetime
import enum

# region ENUMS

class TipoInstituicao(enum.Enum):
    banco = "banco"
    fintech = "fintech"
    corretora = "corretora"
    carteira_digital = "carteira_digital"
    outro = "outro"

class SubtipoConta(enum.Enum):
    corrente = "corrente"
    cartao = "cartao"
    poupanca = "poupanca"
    dinheiro = "dinheiro"
    investimento = "investimento"
    salario = "salario"
    outro = "outro"

#endregion

"""############################### CONTA (BASE) ########################################################"""
class Conta(Base):
    """ A classe Conta representa a estrutura básica de uma conta financeira, com atributos comuns a todos os tipos de conta, como nome da conta, saldo inicial, tipo de conta, entre outros.
    A classe Conta é a classe base para as classes Conta_Corrente e Conta_Cartao, que herdam os atributos e métodos da classe Conta e adicionam funcionalidades específicas para cada tipo de conta."""

#region TABELA E COLUNAS
    __tablename__ = "contas" #criando a tabela conta.

    # CAMPOS DA TABELA
    id_conta = Column(Integer, primary_key=True, autoincrement=True) # coluna id conta
    saldo_inicial = Column(Float, default=0.0) # coluna de saldo inicial
    nome_conta = Column(String) # Coluna nome da conta
    banco = Column(String) # nome do banco
    tipo_instituicao = Column(Enum(TipoInstituicao), default=TipoInstituicao.banco) # tipo de instituição financeira, como banco, fintech, corretora, etc.
    ignorar_patrimonio = Column(Boolean, default=False) # se a conta deve ser ignorada no cálculo do patrimônio líquido, útil para contas que não representam um ativo real, como contas de teste ou contas de investimento que não devem ser consideradas no patrimônio líquido do usuário.
    cor_perfil = Column(String, nullable=True) # cor para representar a conta nos gráficos, pode ser nula, caso o usuário não queira escolher uma cor específica para a conta, e nesse caso, o sistema pode atribuir uma cor padrão ou escolher uma cor aleatória para a conta.
    tipo_conta = Column(String, nullable=False) # coluna com o tipo de conta (Ex.: conta corrente, poupança, cartão de crédito, dinheiro, etc.). O campo tipo_conta é usado para categorizar as contas do usuário e pode ser útil para filtrar as contas em gráficos e relatórios, ou para aplicar regras específicas de acordo com o tipo de conta, como por exemplo, não considerar contas do tipo dinheiro no cálculo do patrimônio líquido.
    subtipo_conta = Column(Enum(SubtipoConta), nullable=True) # coluna com o subtipo de conta. O campo subtipo_conta é usado para fornecer uma categorização mais detalhada das contas do usuário, permitindo uma organização mais granular e personalizada das contas, e pode ser útil para filtrar as contas em gráficos e relatórios, ou para aplicar regras específicas de acordo com o subtipo de conta.
    limite_seguranca = Column (Float, nullable=True) # limite de segurança estipulado pelo usuário
    ativa = Column(Boolean, default=True) # campo para indicar se a conta está ativa ou inativa, permitindo que o usuário desative contas que não estão mais em uso sem precisar deletá-las do sistema, e assim manter um histórico das contas anteriores. O campo ativa é usado para filtrar as contas ativas e inativas em gráficos e relatórios, e para evitar que contas inativas sejam consideradas em cálculos como o saldo total ou o patrimônio líquido do usuário.
    
    # CONTA CORRENTE
    # Essas colunas são usadas apenas para contas do tipo corrente, e podem ser nulas para outros tipos de conta.
    cheque_especial = Column(Float, default= 0.0 ) # coluna de cheque especial para contas correntes, por padrão será 0.0 para contas que não possuam essa funcionalidade.
    vencimento = Column (Integer, nullable=True) #  Dia do mês que vence o cheque especial para contas correntes com essa função.

    # CARTÃO DE CRÉDITO
    # Essas colunas são usadas apenas para contas do tipo cartão, e podem ser nulas para outros tipos de conta.
    limite = Column(Float, default=0.0 ) # coluna de limite para contas do tipo cartão,
    vencimento_cartao = Column(Integer, nullable=True) #  Dia do mês que vence a fatura do cartão.
    fechamento_cartao = Column(Integer, nullable=True) #  Dia do mês que em que a fatura do cartão é fechada.

    # CHAVES ESTRANGEIRAS
    id_familia = Column(Integer, ForeignKey("familias.id_familia", ondelete="SET NULL"), nullable=True) # coluna de id da família, que permitirá associar a conta a uma família. Pode ser nula para contas que não sejam associadas a uma família.
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario")) # recuperando a id de usuário da tabela usuários
    id_indice = Column(Integer, ForeignKey("indices.id_indice")) # id de indice financeiro

    # RELACIONAMENTOS COM OUTRAS TABELAS  
    transacoes = relationship("Transacao", back_populates="conta") # relacionamento com a tabela de transações.                  # CONFERIDO
    usuario = relationship("Usuario", back_populates="contas") # relacionamento com a tabela de usuários                         # CONFERIDO       
    indice = relationship("IndiceFinanceiro", back_populates="contas") # relacionamento com a tabela de índices financeiros.     # CONFERIDO
    familia = relationship("Familia", back_populates="contas") # relacionamento com a tabela de famílias.                        # CONFERIDO

    # ATALHO PARA AS TRANSACOES PENDENTES
    transacoes_pendentes = relationship(
        "Transacao", 
        primaryjoin="and_(Conta.id_conta == Transacao.id_conta, "
                    "Transacao.quitada == False, "
                    "Transacao.tipo != 'receita')", 
        viewonly=True
    )

    # CONFIGURAÇÃO PARA STI (Single Table Inheritance)
    __mapper_args__ = {
        'polymorphic_on': tipo_conta, # campo usado para diferenciar os tipos de conta na tabela, permitindo que o SQLAlchemy saiba qual classe usar para instanciar os objetos ao recuperar os dados do banco.
        'polymorphic_identity': 'conta_base' # valor do campo tipo_conta que identifica os registros que correspondem à classe base Conta, ou seja, registros com tipo_conta igual a 'conta' serão instanciados como objetos da classe Conta, enquanto registros com tipo_conta igual a 'corrente' ou 'cartao' serão instanciados como objetos das classes Conta_Corrente e Conta_Cartao, respectivamente.
    }

#endregion

#region INIT    
    def __init__(self, 
                 nome_conta,      # Obrigatório (Sem default)
                 id_usuario,      # Obrigatório (Sem default)
                 tipo_conta,      # Obrigatório (Sem default)
                 saldo_inicial=0.0,  
                 subtipo_conta=None,
                 cheque_especial=0.0,
                 vencimento=None,
                 limite=0.0,
                 vencimento_cartao=None,
                 fechamento_cartao=None,
                 ativa=True,
                 id_indice=None,
                 tipo_instituicao="banco",
                 ignorar_patrimonio=False,
                 cor_perfil=None,
                 limite_seguranca=None,
                 banco=None):

        self.nome_conta = nome_conta
        self.saldo_inicial = saldo_inicial
        self.id_usuario = id_usuario
        self.tipo_conta = tipo_conta 
        self.subtipo_conta = subtipo_conta
        self.cheque_especial = cheque_especial
        self.vencimento = vencimento   
        self.limite = limite
        self.vencimento_cartao = vencimento_cartao
        self.fechamento_cartao = fechamento_cartao
        self.ativa = ativa
        self.id_indice = id_indice 
        self.tipo_instituicao = tipo_instituicao
        self.ignorar_patrimonio = ignorar_patrimonio
        self.cor_perfil = cor_perfil
        self.limite_seguranca = limite_seguranca
        self.banco = banco 
#endregion

#region PROPRIEDADES E MÉTODOS DE CONTA

#region PROPRIEDADES E MÉTODOS ESPECÍFICOS:
    # PROPRIEDADES:
    @property
    def saldo_atual(self):
        """ propriedade para calcular o saldo atual da conta, levando em consideração o saldo inicial e as transações associadas à conta. 
        A função percorre as transações da conta e, para cada transação, verifica se é uma receita ou despesa e atualiza o saldo de acordo. 
        O resultado é o saldo atual da conta, que pode ser usado para exibir ao usuário ou para outras funcionalidades do sistema. """
        
        # o saldo atual começa com o saldo inicial da conta
        total = self.saldo_inicial
        hoje = datetime.date.today() # adiciona o dia de hoje em uma variável para comparar com a data das transações.

        # percorre as transações associadas à conta e atualiza o saldo de acordo com o tipo de transação (receita ou despesa)
        for t in self.transacoes:
            
            if t.data > hoje: # se a data da transação for maior que a data de hoje, ou seja, se a transação for futura, ela não é considerada no cálculo do saldo atual, pois ainda não ocorreu.
                continue

            if t.ignore: # se a transação estiver marcada para ser ignorada, ela não é considerada no cálculo do saldo.
                continue

            # verifica o tipo da transação, se for receita, o valor é adicionado ao total.
            if t.tipo == "receita":
                total += t.valor

            # verifica o tipo da transação, se for despesa, o valor é subtraído do total.
            elif t.tipo in ["despesa", "transferencia", "investimento"]: # se a transação for uma despesa, transferência ou investimento, o valor é subtraído do total, mas somente se a transação estiver marcada como quitada, ou seja, se a despesa já foi paga. Caso contrário, a despesa não é considerada no cálculo do saldo atual, pois ainda não foi paga.
                if t.quitada: # se a transação for uma despesa e estiver marcada como quitada, o valor é subtraído do total, caso contrário, a despesa não é considerada no cálculo do saldo atual, pois ainda não foi paga.
                    total -= t.valor

        return total
    
    # MÉTODOS ESPECÍFICOS:
    def verificar_gatilhos(self):
        """ função para verificar os gatilhos de alerta relacionados ao saldo da conta, como o limite de segurança e o uso do cheque especial. 
        A função percorre as transações da conta, calcula o saldo atual e verifica se o saldo está abaixo do limite de segurança estipulado pelo usuário 
        ou se o cheque especial está sendo usado. Se alguma dessas condições for verdadeira, a função adiciona uma mensagem de alerta à lista de alertas, 
        que pode ser exibida para o usuário. """
        try:
            alertas = [] # lista para armazenar os alertas gerados pela função
            saldo = self.saldo_atual # calcula o saldo atual da conta usando a propriedade saldo_atual, que leva em consideração o saldo inicial e as transações associadas à conta.
            
            # verifica se o saldo está abaixo do limite de segurança estipulado pelo usuário, e se o limite de segurança é maior que 0 para evitar alertas desnecessários 
            # quando o usuário não estipulou um limite de segurança.
            
            limite = self.limite_seguranca or 0

            if limite > 0 and saldo < limite and saldo > 0: 
                alertas.append(
                    f"Atenção! O saldo da conta {self.nome_conta} está abaixo do limite estipulado de R${limite:.2f}."
                    )
            
            cheque = self.cheque_especial or 0

            if cheque > 0 and saldo < 0:
                percentual_uso = (abs(saldo) / cheque)* 100
                alertas.append(
                    f"Alerta: Você está usando {percentual_uso:.1f}% do seu cheque especial na conta {self.nome_conta}."
                )

            return alertas
        
        except Exception as e:
            print (f"Não foi possível verificar os gatilho: {e}")
            raise e
#endregion

#region MÉTODOS DE BANCO DE DADOS:
    def add_conta(self):
        db = SessionLocal()
        
        try:
            db.add(self) # adiciona a conta ao bd
            db.commit() # comita a mudança
            db.refresh(self) # atualiza o bd
            print (f"Conta {self.id_conta} adicionada com sucesso!") # imprime uma mensagem de conclusão.
        
        except Exception as e:
            db.rollback() # caso haja algum erro, desfaz a operação.
            print (f"Erro ao adicionar a conta {self.id_conta}: {e}") # imprime uma mensagem de conclusão.
            raise e # lança o erro para fora da função.

        finally:
            db.close() # fecha a conexão com o BD

    def mod_conta(self):
        db =  SessionLocal()

        try:
            db.merge(self) # mescla o estado atual do objeto com seu equivalente no BD
            db.commit() # salva a alteração no bd
            db.refresh(self) # atualiza o bd com a alteração
            print (f"Conta {self.id_conta} alterada com sucesso.") # imprime a msg de conclusão
        
        except Exception as e:
            db.rollback() # caso haja algum erro, desfaz a operação.
            print (f"Erro ao alterar os dados: {e}") # imprime uma mensagem de conclusão.
            raise e # lança o erro para fora da função.

        finally:
            db.close() # fecha a conexão com o BD

    def del_conta(self):
        db = SessionLocal() # Estabelece a conexão com o banco de Dados.

        try:
            db.delete(self) # deleta o usuário do DB
            db.commit() # faz a alteração permanentemente
            print(f"Conta {self.id_conta} excluída com sucesso!") # imprime uma mensagem de conclusão.

        except Exception as e:
            db.rollback() # caso haja algum erro, desfaz a operação.
            print (f"Erro ao excluir a conta{self.id_conta}: {e}") # imprime uma mensagem de conclusão.
            raise e # lança o erro para fora da função.
        
        finally:
            db.close() # fecha a conexão com o BD
#endregion

#endregion

"""############################### CONTA CORRENTE ######################################################"""
class Conta_Corrente(Conta):
    """ A classe Conta_Corrente representa uma conta corrente, que é um tipo específico de conta financeira. Ela possui atributos exclusivos como cheque especial e vencimento do cheque especial"""

#region TABELA E COLUNAS
    __mapper_args__ = {
        'polymorphic_identity': 'corrente' # Valor que será gravado em tipo_conta
    }
#endregion

#region INIT
    def __init__(self, 
                 nome_conta, 
                 id_usuario, 
                 tipo_conta="corrente", 
                 saldo_inicial=0.0,      
                 subtipo_conta=None,
                 cheque_especial=0.0, 
                 vencimento=None, 
                 ativa=True, 
                 id_indice=None, 
                 tipo_instituicao="banco", 
                 ignorar_patrimonio=False, 
                 cor_perfil=None, 
                 limite_seguranca=None, 
                 banco=None):

        super().__init__(nome_conta, 
                         id_usuario, 
                         tipo_conta, 
                         saldo_inicial, 
                         subtipo_conta,
                         cheque_especial, 
                         vencimento, 
                         0.0,             
                         None,            
                         None,            
                         ativa, 
                         id_indice, 
                         tipo_instituicao, 
                         ignorar_patrimonio, 
                         cor_perfil, 
                         limite_seguranca, 
                         banco)
        
        self.cheque_especial = cheque_especial
        self.vencimento = vencimento
#endregion

#region PROPRIEDADES E MÉTODOS DA CONTA CORRENTE
    @property
    def limite_disponivel(self):
        # propriedade para calcular o limite disponível. Se o saldo estiver negativo, a função retorna a soma do valor negativo do saldo com o valor do cheque especial, indicando o limite disponível.
        # Se o saldo for negativo, o cheque especial está sendo usado

        if self.saldo_atual < 0:
            return self.cheque_especial + self.saldo_atual
        return self.cheque_especial

    @property
    def uso_cheque_especial(self):
        # property que nos dirá o gasto com o cheque especial do usuário, pegamos o saldo atual e se estiver negativo, retornamos o valor absoluto e com isso sabemos o uso do Cheque especial.

        if self.saldo_atual < 0:
            return abs(self.saldo_atual)
        return 0.0

    @property
    def saldo_total_disponivel(self):
        # Essa propriedade soma o dinheiro real com o limite do banco, nos dando o valor total disponível naquela conta para o usuário.

        return self.saldo_atual + self.cheque_especial
#endregion

"""############################### CONTA CARTÂO ########################################################"""
class Conta_Cartao(Conta):
    """ A classe Conta_Cartao representa uma conta de cartão de crédito, que é um tipo específico de conta financeira. Ela possui atributos exclusivos como limite do cartão, vencimento da fatura e fechamento da fatura."""

#region TABELA E COLUNAS    
    __mapper_args__ = {
        'polymorphic_identity': 'cartao' # Valor que será gravado em tipo_conta
    }
#endregion

#region INIT   
    def __init__(self, 
                 nome_conta, 
                 id_usuario, 
                 tipo_conta="cartao",
                 saldo_inicial=0.0,
                 subtipo_conta="cartao",
                 limite=0.0,
                 vencimento_cartao=None,
                 fechamento_cartao=None,
                 ativa=True, 
                 id_indice=None,
                 tipo_instituicao="banco", 
                 ignorar_patrimonio=False, 
                 cor_perfil=None, 
                 limite_seguranca=None, 
                 banco=None):

        super().__init__(nome_conta, 
                         id_usuario, 
                         tipo_conta, 
                         saldo_inicial, 
                         subtipo_conta,
                         0.0,
                         None,
                         limite,
                         vencimento_cartao,
                         fechamento_cartao,
                         ativa, 
                         id_indice, 
                         tipo_instituicao, 
                         ignorar_patrimonio, 
                         cor_perfil, 
                         limite_seguranca, 
                         banco)
        
        self.limite = limite
        self.vencimento_cartao = vencimento_cartao
        self.fechamento_cartao = fechamento_cartao
#endregion

#region PROPRIEDADES E MÉTODOS DA CONTA CARTÃO
    @property
    def fatura_atual_cartao(self):
        # essa property vai ser responsável por passar o valor da fatura atual, calculando o valor acumulado de gastos que ainda não foram quitados
        
        return sum(t.valor for t in self.transacoes_pendentes)
    
    @property
    def saldo_disponivel_cartao(self):
        # Propriedade para calcular o saldo disponível do cartão, subtraindo o valor da fatura atual do limite do cartão.
        # O resultado é o saldo disponível do cartão, que pode ser usado para exibir ao usuário ou para outras funcionalidades do sistema.
        
        return self.limite - self.fatura_atual_cartao

#endregion

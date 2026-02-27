from sqlalchemy import Column, Integer, Float, String, DateTime, Date, ForeignKey, Boolean
from database.config import Base, SessionLocal
from sqlalchemy.orm import relationship

# Criando a classe contas:

class Conta(Base):

    __tablename__ = "contas" #criando a tabela conta.

    id_conta = Column(Integer, primary_key=True, autoincrement=True) # coluna id conta
    saldo_inicial = Column(Float) # coluna de saldo inicial
    nome_conta = Column(String) # Coluna nome da conta
    banco = Column(String) # nome do banco
    tipo_instituicao = Column(String, default="banco") # tipo de instituição financeira, como banco, fintech, corretora, etc.
    ignorar_patrimonio = Column(Boolean, default=False) # se a conta deve ser ignorada no cálculo do patrimônio líquido, útil para contas que não representam um ativo real, como contas de teste ou contas de investimento que não devem ser consideradas no patrimônio líquido do usuário.
    cor_perfil = Column(String, nullable=True) # cor para representar a conta nos gráficos, pode ser nula, caso o usuário não queira escolher uma cor específica para a conta, e nesse caso, o sistema pode atribuir uma cor padrão ou escolher uma cor aleatória para a conta.
    tipo_conta = Column(String) # coluna com o tipo de conta (Ex.: conta corrente, poupança, cartão de crédito, dinheiro, etc.). O campo tipo_conta é usado para categorizar as contas do usuário e pode ser útil para filtrar as contas em gráficos e relatórios, ou para aplicar regras específicas de acordo com o tipo de conta, como por exemplo, não considerar contas do tipo dinheiro no cálculo do patrimônio líquido.
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario")) # recuperando a id de usuário da tabela usuários
    limite_seguranca = Column (Float, nullable=True) # limite de segurança estipulado pelo usuário

    # colunas específicas para conta corrente, como cheque especial e vencimento do cheque especial. 
    # Essas colunas são usadas apenas para contas do tipo corrente, e podem ser nulas para outros tipos de conta.
    cheque_especial = Column(Float, nullable=True) # coluna de cheque especial para contas correntes, pode ser nula para outros tipos de conta que não têm essa funcionalidade, como contas de poupança ou dinheiro. O campo cheque_especial é usado para armazenar o valor do limite do cheque especial disponível para a conta corrente, e pode ser usado para calcular o limite disponível e gerar alertas quando o saldo da conta estiver próximo ou ultrapassar o limite do cheque especial.
    vencimento = Column (Date, nullable=True) # data de vencimento do cheque especial para contas correntes, pode ser nula para outros tipos de conta que não têm essa funcionalidade. O campo vencimento é usado para armazenar a data de vencimento do cheque especial da conta corrente, e pode ser usado para gerar alertas quando a data de vencimento estiver próxima, para que o usuário possa se planejar para pagar o valor utilizado do cheque especial antes do vencimento e evitar juros e taxas.
    
    # colunas específicas para cartão de crédito, como limite do cartão, vencimento da fatura e data de fechamento da fatura. 
    # Essas colunas são usadas apenas para contas do tipo cartão, e podem ser nulas para outros tipos de conta.
    limite = Column(Float, nullable=True) # coluna de limite para contas do tipo cartão,
    vencimento_cartao = Column(Date, nullable=True) # coluna de vencimento do cartão para contas do tipo cartão, pode ser nula para outros tipos de conta que não têm essa funcionalidade. O campo vencimento_cartao é usado para armazenar a data de vencimento da fatura do cartão de crédito, e pode ser usado para gerar alertas quando a data de vencimento estiver próxima, para que o usuário possa se planejar para pagar a fatura do cartão antes do vencimento e evitar juros e taxas.
    fechamento_cartao = Column(Date, nullable=True) # coluna de data de fechamento da f

    # relacionamentos com outras tabelas:
    transacoes = relationship("Transacao", back_populates="conta") # relacionamento com a tabela de transações
    usuario = relationship("Usuario", back_populates="contas") # relacionamento com a tabela de usuários        


    def __init__(self, 
                 nome_conta, 
                 saldo_inicial, 
                 id_usuario,
                 cheque_especial=None,
                 vencimento=None,
                 limite=None,
                 vencimento_cartao=None, 
                 fechamento_cartao=None,
                 tipo_instituicao="banco",
                 ignorar_patrimonio=False,
                 cor_perfil=None,
                 limite_seguranca=None , 
                 banco=None):

        self.nome_conta = nome_conta
        self.saldo_inicial = saldo_inicial
        self.id_usuario = id_usuario
        self.tipo_instituicao = tipo_instituicao
        self.ignorar_patrimonio = ignorar_patrimonio
        self.cor_perfil = cor_perfil
        self.limite_seguranca = limite_seguranca
        self.banco = banco

        # configurações específicas para conta corrente
        self.cheque_especial = cheque_especial
        self.vencimento = vencimento
        
        # configurações específicas para cartão de crédito
        self.limite = limite
        self.vencimento_cartao = vencimento_cartao
        self.fechamento_cartao = fechamento_cartao

    @property
    def saldo_atual(self):
        """ propriedade para calcular o saldo atual da conta, levando em consideração o saldo inicial e as transações associadas à conta. 
        A função percorre as transações da conta e, para cada transação, verifica se é uma receita ou despesa e atualiza o saldo de acordo. 
        O resultado é o saldo atual da conta, que pode ser usado para exibir ao usuário ou para outras funcionalidades do sistema. """
        
        # o saldo atual começa com o saldo inicial da conta
        total = self.saldo_inicial
        
        # percorre as transações associadas à conta e atualiza o saldo de acordo com o tipo de transação (receita ou despesa)
        for t in self.transacoes:
            
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
  
    @property
    def limite_disponivel(self):
        # Se o saldo for negativo, o cheque especial está sendo usado
        if self.saldo_atual < 0:
            return self.cheque_especial + self.saldo_atual
        return self.cheque_especial

    @property
    def saldo_total_disponivel(self):
        # Soma o dinheiro real com o limite do banco
        return self.saldo_atual + self.cheque_especial    
    
    def verificar_gatilhos(self):
        """ função para verificar os gatilhos de alerta relacionados ao saldo da conta, como o limite de segurança e o uso do cheque especial. 
        A função percorre as transações da conta, calcula o saldo atual e verifica se o saldo está abaixo do limite de segurança estipulado pelo usuário 
        ou se o cheque especial está sendo usado. Se alguma dessas condições for verdadeira, a função adiciona uma mensagem de alerta à lista de alertas, 
        que pode ser exibida para o usuário. """
        
        alertas = [] # lista para armazenar os alertas gerados pela função
        saldo = self.saldo_atual # calcula o saldo atual da conta usando a propriedade saldo_atual, que leva em consideração o saldo inicial e as transações associadas à conta.
        
        # verifica se o saldo está abaixo do limite de segurança estipulado pelo usuário, e se o limite de segurança é maior que 0 para evitar alertas desnecessários 
        # quando o usuário não estipulou um limite de segurança.
        if self.limite_seguranca > 0 and saldo < self.limite_seguranca and saldo > 0:
            alertas.append(f"Atenção! O saldo da conta {self.nome_conta} está abaixo do limite estipulado de R${self.limite_seguranca}.")

        # verifica se o saldo está negativo, o que indica que o cheque especial está sendo usado, e se a conta tem a coluna cheque_especial para evitar erros em contas 
        # que não têm essa funcionalidade. Se o cheque especial estiver sendo usado, calcula o percentual do cheque especial que está sendo utilizado e 
        # adiciona um alerta à lista de alertas.
        if hasattr(self, 'cheque_especial') and saldo < 0:
            percentual_uso = (abs(saldo) / self.cheque_especial)*100
            alertas.append(f"Alerta: Você está usando {percentual_uso:.1f}% do seu cheque especial.")

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

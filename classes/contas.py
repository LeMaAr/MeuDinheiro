from sqlalchemy import Column, Integer, Float, String, DateTime, Date, ForeignKey
from database.config import Base, SessionLocal
from sqlalchemy.orm import relationship

# Criando a classe contas:

class Conta(Base):

    __tablename__ = "contas" #criando a tabela conta.

    id_conta = Column(Integer, primary_key=True, autoincrement=True) # coluna id conta
    saldo_inicial = Column(Float) # coluna de saldo inicial
    nome_conta = Column(String) # Coluna nome da conta
    banco = Column(String) # nome do banco
    tipo_conta = Column(String) # coluna com o tipo de conta
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario")) # recuperando a id de usuário da tabela usuários
    transacoes = relationship("Transacao", back_populates="conta")
    
    __mapper_args__ = {
        'polymorphic_on': tipo_conta,
        'polymorphic_identity': 'conta_base'
    }
    
    def __init__(self, nome_conta, saldo_inicial, id_usuario, banco=None):

        self.nome_conta = nome_conta
        self.saldo_inicial = saldo_inicial
        self.id_usuario = id_usuario
        self.banco = banco

    @property
    def saldo_atual(self):
        total = self.saldo_inicial
        for t in self.transacoes:
            if t.tipo.lower() == "receita":
                total += t.valor
            elif t.tipo.lower() == "despesa":
                total -= t.valor
        return total
    
    def add_conta(self):
        db = SessionLocal()
        
        try:
            db.add(self) # adiciona a conta ao bd
            db.commit() # comita a mudança
            db.refresh(self) # atualiza o bd
            print (f"Conta {self.id_conta} adicionada com sucesso!") # imprime uma mensagem de conclusão.
        
        except Exception as e:
            db.rollback() # caso haja algum erro, desfaz a operação.
            print (f"Erro ao adicionar o usuário{self.id_conta}: {e}") # imprime uma mensagem de conclusão.
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

class ContaCorrente(Conta):

    __tablename__ = "contas_correntes" #criando a tabela conta corrente.

    id_conta = Column(Integer, ForeignKey("contas.id_conta"), primary_key=True)
    cheque_especial = Column(Float) # coluna de cheque especial
    vencimento = Column (Date) # data de vencimento do cheque especial
    __mapper_args__ = {
        'polymorphic_identity': 'corrente'
    }
    
    def __init__(self, nome_conta, saldo_inicial, id_usuario, banco, cheque_especial, vencimento):

        super().__init__(nome_conta, saldo_inicial, id_usuario, banco)
        self.cheque_especial = cheque_especial
        self.vencimento = vencimento

class Cartao(Conta):

    __tablename__ = "cartoes" # criando a tabela cartão

    id_conta = Column(Integer, ForeignKey("contas.id_conta"), primary_key=True)
    limite = Column(Float, nullable=False) # coluna limite
    vencimento_cartao = Column(Date) # coluna vencimento do cartão
    fechamento_cartao = Column(Date) # coluna com a data de fechamento do cartão
    __mapper_args__ = {
        'polymorphic_identity': 'cartao'
    }

    def __init__(self, nome_conta, saldo_inicial, id_usuario, banco, limite, vencimento_cartao,fechamento_cartao):
        
        super().__init__(nome_conta, saldo_inicial, id_usuario, banco)
        self.limite = limite
        self.vencimento_cartao = vencimento_cartao
        self.fechamento_cartao = fechamento_cartao

class ContaPoupanca(Conta):
    __mapper_args__ = {
        'polymorphic_identity': 'poupanca'
    }

class Dinheiro(Conta):
    __mapper_args__ = {
        'polymorphic_identity': 'dinheiro'
    }
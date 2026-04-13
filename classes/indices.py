from datetime import datetime
from database.config import Base, SessionLocal
from sqlalchemy import Column, Integer, Float, String, DateTime, Date, UniqueConstraint
from sqlalchemy.orm import relationship

"""############################### ÍNDICES ########################################################"""
class IndiceFinanceiro(Base):
    """ criando a tabela "indices" para armazenar os índices financeiros, como SELIC, IPCA, CDI, etc. 
    Esses índices podem ser usados para calcular a rentabilidade de investimentos, corrigir valores monetários, etc."""
    
#region TABELA E RELACIONAMENTOS:
    __tablename__ = "indices"

    # CAMPOS DA TABELA:
    id_indice = Column(Integer, primary_key=True, autoincrement=True) # id única do índice, o primary key impede que hajam mais de uma chave igual e o autoincrement adiciona 1 a cada novo índice
    nome = Column(String, nullable=False) # nome do índice financeiro, como SELIC, IPCA, CDI, etc. O campo nome é usado para identificar o índice e deve ser único para evitar confusão entre índices diferentes. O campo nome é obrigatório, pois é essencial para a identificação do índice.
    valor = Column(Float, nullable=False) # valor do índice financeiro, como a taxa SELIC atual, a inflação medida pelo IPCA, etc. O campo valor é usado para armazenar o valor numérico do índice, que pode ser usado em cálculos financeiros. O campo valor é obrigatório, pois um índice sem valor não tem utilidade prática.
    data_referencia = Column(Date, nullable=False) # data de referência do valor do índice, ou seja, a data para a qual o valor do índice é válido. Por exemplo, se o valor do índice é a taxa SELIC atual, a data de referência seria a data atual. Se o valor do índice é a inflação medida pelo IPCA no mês passado, a data de referência seria o último dia do mês passado. O campo data_referencia é usado para garantir que o valor do índice seja interpretado corretamente no contexto temporal, e é obrigatório para evitar ambiguidades sobre a validade do valor do índice.
    ultima_atualizacao = Column(DateTime, default=datetime.now) # data e hora da última atualização do índice, o default define que, caso o usuário não informe uma data, a data atual será usada. O campo ultima_atualizacao é útil para rastrear quando o índice foi atualizado pela última vez, o que pode ser importante para garantir que os cálculos financeiros estejam usando valores atualizados.
    unidade = Column(String(10), nullable=False, default="percentual") # unidade de medida do índice, como "percentual", "pontos", "reais", etc. O campo unidade é usado para indicar a unidade de medida do valor do índice, o que é importante para interpretar corretamente o valor. 
    base_tempo = Column(String(20), nullable=True, default="mensal") # base de tempo do índice, como "mensal", "anual", etc. O campo base_tempo é usado para indicar a frequência com que o índice é atualizado, o que é importante para interpretar corretamente o valor.
    frequencia_atualizacao = Column(String(20), nullable=True, default="diária") # frequência de atualização do índice, como "diária", "semanal", "mensal", etc. O campo frequencia_atualizacao é usado para indicar com que frequência o índice é atualizado, o que é importante para garantir que os cálculos financeiros estejam usando valores atualizados.

    # RESTRIÇÃO DE UNICIDADE:
    __table_args__ = (UniqueConstraint('nome', 'data_referencia', name='_nome_data_uc'),) # garante que não haja mais de um registro com o mesmo nome e data de referência, evitando duplicidade de índices para a mesma data.

    # RELACIONAMENTOS:
    contas = relationship("Conta", back_populates="indice") # relacionamento com a tabela de contas.    # CONFERIDO
    ativos = relationship("Ativo", back_populates="indice") # relacionamento com a tabela de ativos.    # CONFERIDO
#endregion

#region INIT:
    def __init__(self, 
                 nome, 
                 valor, 
                 data_referencia,
                 ultima_atualizacao = None,
                 unidade = "percentual",
                 base_tempo = "mensal",
                 frequencia_atualizacao = "diária"
                 ):
        
        self.nome = nome
        self.valor = valor
        
        if hasattr(data_referencia, 'date'):
            self.data_referencia = data_referencia.date()
        else:
            self.data_referencia = data_referencia
        
        self.ultima_atualizacao = ultima_atualizacao or datetime.datetime.now() # se a data de última atualização não for fornecida.
        self.unidade = unidade
        self.base_tempo = base_tempo
        self.frequencia_atualizacao = frequencia_atualizacao

#endregion

#region MÉTODOS DE BANCO DE DADOS:
    def add_indice(self):
        db = SessionLocal()
        
        try:
            db.add(self)
            db.commit()
            db.refresh(self)
            print(f"Índice {self.nome} de {self.data_referencia} adicionado!")
     
        except Exception as e:
            db.rollback()
            raise e
     
        finally:
            db.close()

    def mod_indice(self):
        db = SessionLocal()
        
        try:
            db.merge(self) # Mescla as alterações feitas no objeto com o registro no banco
            db.commit() # Salva permanentemente
            db.refresh(self) # Atualiza o objeto local
            print(f"Índice {self.nome} de {self.data_referencia} atualizado com sucesso!")
        
        except Exception as e:
            db.rollback()
            print(f"Erro ao alterar índice: {e}")
            raise e
        
        finally:
            db.close()

    def del_indice(self):
        db = SessionLocal()
        
        try:
            db.delete(self) # Deleta o registro do banco
            db.commit() # Salva permanentemente
            print(f"Índice {self.nome} de {self.data_referencia} deletado com sucesso!")
        
        except Exception as e:
            db.rollback()
            print(f"Erro ao deletar índice: {e}")
            raise e
        
        finally:
            db.close()
#endregion
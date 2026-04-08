from database.config  import Base, SessionLocal 
from sqlalchemy import Column, Integer, Float, String, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
import datetime
import enum
import uuid

class StatusConvite(str, enum.Enum):
    PENDENTE = "pendente"
    ACEITO = "aceito"
    RECUSADO = "recusado"

class ConviteFamilia(Base):

    __tablename__ = "convites_familia"

    id_convite = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    email_convidado = Column(String, nullable=False)
    id_familia = Column(Integer, ForeignKey("familias.id_familia"), nullable=False)
    token = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pendente") # status do convite: pendente, aceito ou recusado
    data_criacao = Column(DateTime, default=datetime.datetime.now, nullable=False) # data de criação do convite, preenchida automaticamente com a data e hora atual quando o convite é criado

    familia = relationship("Familia", back_populates="convites")

    def gerar_token(self):
        # função para gerar um token único para cada convite, utilizando a biblioteca uuid para gerar um identificador único universal (UUID) 
        # e convertendo-o para string. O token é gerado automaticamente quando um novo convite é criado, garantindo que cada convite tenha um token exclusivo 
        # que pode ser usado para identificar e validar o convite.
        self.token = str(uuid.uuid4())

    def __init__(self, email_convidado, id_familia):
        self.email_convidado = email_convidado
        self.id_familia = id_familia
        self.status = StatusConvite.PENDENTE.value
        self.gerar_token() # chama a função gerar_token para criar um token único para o convite
  
    def validar_token(self, token):
        # função para validar o token do convite, comparando o token fornecido com o token armazenado no convite. 
        # Se os tokens corresponderem, a função retorna True, indicando que o token é válido e o convite pode ser aceito. 
        # Caso contrário, a função retorna False, indicando que o token é inválido e o convite não pode ser aceito.
        return self.token == token
    
    def modificar_status(self, novo_status):
        # função para modificar o status do convite, permitindo que o status seja atualizado para "aceito" ou "recusado" com base na ação do usuário. 
        # A função recebe o novo status como argumento e atualiza o campo status do convite de acordo. 
        # Isso permite que o sistema acompanhe o status de cada convite e tome as ações apropriadas com base no status atualizado.
        if novo_status in StatusConvite._value2member_map_:
            self.status = novo_status
        else:
            raise ValueError("Status inválido. Os valores permitidos são: 'pendente', 'aceito' ou 'recusado'.")

    def deletar_convite_por_tempo(self):
        # função para deletar convites que ultrapassaram um tempo limite, permitindo que o sistema mantenha apenas convites válidos e remova aqueles que não foram aceitos ou recusados dentro de um período específico. 
        # A função recebe o tempo limite em dias como argumento e compara a data de criação do convite com a data atual. 
        # Se a diferença entre as datas for maior que o tempo limite, o convite é deletado do banco de dados, garantindo que apenas convites recentes e relevantes sejam mantidos no sistema.
        db = SessionLocal() # Estabelece a conexão com o banco de Dados.

        try:
            tempo_limite = datetime.timedelta(days=7)# define o tempo limite para 7 dias, pode ser ajustado conforme necessário
            data_atual = datetime.datetime.now()
            if self.data_criacao + tempo_limite < data_atual:
                db.delete(self) # deleta o convite do DB
                db.commit() # faz a alteração permanentemente
                print(f"Convite {self.id_convite} excluído por ultrapassar o tempo limite!") # imprime uma mensagem de conclusão.

        except Exception as e:
            db.rollback() # caso haja algum erro, desfaz a operação.
            print (f"Erro ao excluir o convite {self.id_convite} por tempo: {e}") # imprime uma mensagem de conclusão.
            raise e # lança o erro para fora da função.
        
        finally:
            db.close() # fecha a conexão com o BD

    def add_convite(self):
        db = SessionLocal() # Estabelece a conexão com o banco de Dados.

        try:
            db.add(self) # adiciona o convite ao bd
            db.commit() # comita a mudança
            db.refresh(self) # atualiza o bd
            print (f"Convite {self.id_convite} adicionado com sucesso!") # imprime uma mensagem de conclusão.
        
        except Exception as e:
            db.rollback() # caso haja algum erro, desfaz a operação.
            print (f"Erro ao adicionar o convite {self.id_convite}: {e}") # imprime uma mensagem de conclusão.
            raise e # lança o erro para fora da função.

        finally:
            db.close() # fecha a conexão com o BD

    def mod_convite(self):

        db = SessionLocal() # Estabelece a conexão com o banco de Dados.
        
        try:
            db.merge(self) # mescla o estado atual do objeto com seu equivalente no BD
            db.commit() # salva a alteração no bd
            db.refresh(self) # atualiza o bd com a alteração
            print(f"Convite {self.id_convite} modificado com sucesso!") # imprime uma mensagem de conclusão.

        except Exception as e:
            db.rollback() # caso haja algum erro, desfaz a operação.
            print (f"Erro ao modificar o convite {self.id_convite}: {e}") # imprime uma mensagem de conclusão.
            raise e # lança o erro para fora da função.
        
        finally:
            db.close() # fecha a conexão com o BD

    def del_convite(self):
        db = SessionLocal() # Estabelece a conexão com o banco de Dados.

        try:
            db.delete(self) # deleta o convite do DB
            db.commit() # faz a alteração permanentemente
            print(f"Convite {self.id_convite} excluído com sucesso!") # imprime uma mensagem de conclusão.

        except Exception as e:
            db.rollback() # caso haja algum erro, desfaz a operação.
            print (f"Erro ao excluir o convite {self.id_convite}: {e}") # imprime uma mensagem de conclusão.
            raise e # lança o erro para fora da função.
        
        finally:
            db.close() # fecha a conexão com o BD
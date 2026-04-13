from database.config  import Base, SessionLocal 
from sqlalchemy import Column, Integer, Float, String, DateTime, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
import datetime
import enum
import uuid

#region ENUMS:
class StatusConvite(str, enum.Enum):
    PENDENTE = "pendente"
    ACEITO = "aceito"
    RECUSADO = "recusado"
#endregion

"""############################### USUÁRIOS ########################################################"""
class ConviteFamilia(Base):

#region TABELA E RELACIONAMENTOS:
    # CAMPOS DA TABELA:
    __tablename__ = "convites_familia"

    id_convite = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    email_convidado = Column(String, nullable=False)
    token = Column(String, nullable=False)
    status = Column(Enum(StatusConvite), nullable=False) # status do convite: pendente, aceito ou recusado
    data_criacao = Column(DateTime, default=datetime.datetime.now, nullable=False) # data de criação do convite, preenchida automaticamente com a data e hora atual quando o convite é criado
    
    # CHAVE ESTRANGEIRA:
    id_familia = Column(Integer, ForeignKey("familias.id_familia"), nullable=False)

    # RELACIONAMENTOS:
    familia = relationship("Familia", back_populates="convites") # CONFERIDO
#endregion

#region INIT:
    def __init__(self, 
                 email_convidado,
                 id_familia,
                 token=None, 
                 status=StatusConvite.PENDENTE):
        
        self.email_convidado = email_convidado
        self.id_familia = id_familia

        # Se um token for fornecido, use-o; caso contrário, gere um token único usando a função gerar_token().        
        if not token:
            self.gerar_token()
        else:
            self.token = token

        # Se o status for fornecido como string, converta-o para o tipo Enum StatusConvite; caso contrário, use o valor fornecido diretamente.
        if isinstance(status, str):
            self.status = StatusConvite(status)
        else:
            self.status = status
#endregion

# region MÉTODOS:
    def gerar_token(self):
        # função para gerar um token único para cada convite, utilizando a biblioteca uuid para gerar um identificador único universal (UUID) 
        # e convertendo-o para string. O token é gerado automaticamente quando um novo convite é criado, garantindo que cada convite tenha um token exclusivo 
        # que pode ser usado para identificar e validar o convite.
        self.token = str(uuid.uuid4())
 
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

    @classmethod
    def limpar_convites_expirados(cls, dias=7):
        """
        Método de classe que busca e deleta todos os convites 
        que foram criados há mais de 'X' dias.
        """
        db = SessionLocal()
        try:
            # Calcula a data de corte (hoje - 7 dias)
            data_corte = datetime.datetime.now() - datetime.timedelta(days=dias)
            
            # Busca todos os convites onde a data_criacao é menor que a data_corte
            convites_expirados = db.query(cls).filter(cls.data_criacao < data_corte).all()
            
            if convites_expirados:
                quantidade = len(convites_expirados)
                for convite in convites_expirados:
                    db.delete(convite)
                
                db.commit()
                print(f"Limpeza concluída: {quantidade} convites expirados foram removidos.")
            else:
                print("Nenhum convite expirado encontrado.")
                
        except Exception as e:
            db.rollback()
            print(f"Erro na limpeza de convites: {e}")
            raise e
        finally:
            db.close()
#endregion
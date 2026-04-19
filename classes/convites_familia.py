from database.config  import Base, SessionLocal 
from database.mixin import CRUDMixin
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import enum
import uuid

#region ENUMS:
class StatusConvite(str, enum.Enum):
    PENDENTE = "pendente"
    ACEITO = "aceito"
    RECUSADO = "recusado"
#endregion

"""############################### USUÁRIOS ########################################################"""
class ConviteFamilia(Base, CRUDMixin):

#region TABELA E RELACIONAMENTOS:
    # CAMPOS DA TABELA:
    __tablename__ = "convites_familia"

    id_convite = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    email_convidado = Column(String, nullable=False)
    token = Column(String, nullable=False)
    status = Column(Enum(StatusConvite), nullable=False) # status do convite: pendente, aceito ou recusado
    data_criacao = Column(DateTime, default=datetime.now, nullable=False) # data de criação do convite, preenchida automaticamente com a data e hora atual quando o convite é criado
    
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
        self.token = token or str(uuid.uuid4())

        # Se o status for fornecido como string, converta-o para o tipo Enum StatusConvite; caso contrário, use o valor fornecido diretamente.
        if isinstance(status, str):
            self.status = StatusConvite(status)
        else:
            self.status = status
#endregion

# region MÉTODOS:

    @classmethod
    def limpar_convites_expirados(cls, dias=7):
        """
        Método de classe que busca e deleta todos os convites 
        que foram criados há mais de 'X' dias.
        """
        db = SessionLocal()
        try:
            # Calcula a data de corte (hoje - 7 dias)
            data_corte = datetime.now() - timedelta(days=dias)
            
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

    def responder_convite(self, novo_status):
        """Atualiza o status e já salva no banco usando o Mixin."""
        if novo_status in StatusConvite.__members__.values() or novo_status in StatusConvite._value2member_map_:
            self.status = novo_status
            self.modificar() 
        else:
            raise ValueError("Status inválido.")

    def validar_token(self, token):
        # função para validar o token do convite, comparando o token fornecido com o token armazenado no convite. 
        # Se os tokens corresponderem, a função retorna True, indicando que o token é válido e o convite pode ser aceito. 
        # Caso contrário, a função retorna False, indicando que o token é inválido e o convite não pode ser aceito.
        return self.token == token
  
#endregion
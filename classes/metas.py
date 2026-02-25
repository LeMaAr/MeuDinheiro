from sqlalchemy import Column, Integer, Float, String, Date, ForeignKey
from database.config import Base, SessionLocal
from datetime import date

class Meta(Base):

    __tablename__ = "metas"

    id_meta = Column(Integer, primary_key=True, autoincrement=True)
    nome_meta = Column(String, nullable=False)
    valor_alvo = Column(Float, nullable=False)
    valor_poupado = Column(Float, default=0.0)
    data_inicio = Column(Date, default=date.today)
    prazo_final = Column(Date)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))
    id_familia = Column(Integer, ForeignKey("familias.id_familia"))

    def __init__(self, nome_meta, valor_alvo, valor_poupado, data_inicio: date, prazo_final: date, id_usuario, id_familia):

        self.nome_meta = nome_meta
        self.valor_alvo = valor_alvo
        self.valor_poupado = valor_poupado
        self.data_inicio = data_inicio
        self.prazo_final = prazo_final
        self.id_usuario = id_usuario
        self. id_familia = id_familia

    @property
    def progresso(self):
        
        if self.valor_alvo <= 0: return 0

        # retorna o progresso da meta em porcentagem
        return (self.valor_poupado / self.valor_alvo) * 100
    
    @property
    def valor_mensal_sugerido(self):
    
        hoje = date.today()
    
        valor_restante = self.valor_alvo - self.valor_poupado
    
        # se a meta estiver concluida cai nessa condicional
        if valor_restante <= 0:
            return 0.0

        # formula para encontrar quantos meses faltam para a conclusão da meta    
        meses_restantes = (self.prazo_final.year - hoje.year) * 12 + (self.prazo_final.month - hoje.month)
            
        if meses_restantes <= 0:
            return valor_restante
    
        # formula para encontrar quanto economizar por mês para concluir a meta.
        return valor_restante / meses_restantes

    @property
    def status_meta(self):
        hoje = date.today()

        dias_totais = (self.prazo_final - self.data_inicio).days

        if dias_totais <= 0:
            return " Erro: Prazo inválido "
        
        valor_diario = self.valor_alvo/ dias_totais

        dias_passados = (hoje - self.data_inicio).days

        if dias_passados < 0:
            return "Aguardando início."

        valor_esperado_hoje =  dias_passados * valor_diario
            
        # Loop de comparação final:

        if self.valor_poupado >= valor_esperado_hoje:
            return "Você está acima da meta!"
        elif self.valor_poupado < valor_esperado_hoje:
            return "Você está abaixo da meta. "
        else:
            return "Você está na meta."

    def add_meta(self):
        db = SessionLocal()
        
        try:
            db.add(self) # adiciona a meta ao bd
            db.commit() # comita a mudança
            db.refresh(self) # atualiza o bd
            print (f"Sua meta {self.id_meta} foi adicionada com sucesso!") # imprime uma mensagem de conclusão.
        
        except Exception as e:
            db.rollback() # caso haja algum erro, desfaz a operação.
            print (f"Erro ao adicionar a meta{self.nome_meta}: {e}") # imprime uma mensagem de conclusão.
            raise e # lança o erro para fora da função.

        finally:
            db.close() # fecha a conexão com o BD

    def mod_meta(self):
        db =  SessionLocal()

        try:
            db.merge(self) # mescla o estado atual do objeto com seu equivalente no BD
            db.commit() # salva a alteração no bd
            db.refresh(self) # atualiza o bd com a alteração
            print (f"Meta {self.nome_meta} alterada com sucesso.") # imprime a msg de conclusão
        
        except Exception as e:
            db.rollback() # caso haja algum erro, desfaz a operação.
            print (f"Erro ao modificar sua meta: {e}") # imprime uma mensagem de conclusão.
            raise e # lança o erro para fora da função.

        finally:
            db.close() # fecha a conexão com o BD

    def del_meta(self):
        db = SessionLocal() # Estabelece a conexão com o banco de Dados.

        try:
            db.delete(self) # deleta o usuário do DB
            db.commit() # faz a alteração permanentemente
            print(f"Meta {self.id_meta} foi excluída com sucesso!") # imprime uma mensagem de conclusão.

        except Exception as e:
            db.rollback() # caso haja algum erro, desfaz a operação.
            print (f"Erro ao excluir a meta {self.nome_meta}: {e}") # imprime uma mensagem de conclusão.
            raise e # lança o erro para fora da função.
        
        finally:
            db.close() # fecha a conexão com o BD

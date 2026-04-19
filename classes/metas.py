from sqlalchemy import Column, Integer, Float, String, Date, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from database.config import Base 
from database.mixin import CRUDMixin
from datetime import date

"""############################### METAS ########################################################"""
class Meta(Base, CRUDMixin):
    """ Classe para representar as metas financeiras dos usuários. Cada meta tem um nome, um valor alvo, um valor de aporte inicial, uma data de início, um prazo final, e está associada OU a um usuário Ou a uma família.
      A classe também inclui propriedades para calcular o progresso da meta, o valor mensal sugerido para alcançar a meta dentro do prazo, e o status da meta em relação ao progresso esperado."""
    __tablename__ = "metas"
    
#region TABELAS E RELACIONAMENTOS:
    # CAMPOS DA TABELA:
    id_meta = Column(Integer, primary_key=True, autoincrement=True)
    nome_meta = Column(String, nullable=False)
    valor_alvo = Column(Float, nullable=False)
    aporte_inicial = Column(Float, nullable=False, default=0.0)
    data_inicio = Column(Date, default=date.today)
    prazo_final = Column(Date)

    # CHAVES ESTRANGEIRAS:
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))
    id_familia = Column(Integer, ForeignKey("familias.id_familia"))

    # RELACIONAMENTOS:
    transacoes = relationship("Transacao", back_populates="meta") # relacionamento com a tabela de transações.  # CONFERIDO
    usuario = relationship("Usuario", back_populates="metas") # relacionamento com a tabela de usuário.         # CONFERIDO
    familia = relationship("Familia", back_populates="metas") # relacionamento com a tabela de família.         # CONFERIDO

    # RESTRIÇÃO PARA IMPEDIR QUE NENHUMA ENTRADA FIQUE SEM UM USUÁRIO OU UMA FAMÍLIA(EXCLUDENTEMENTE)
    __table_args__ = (
        CheckConstraint(
            '(id_usuario IS NOT NULL AND id_familia IS NULL) OR (id_usuario IS NULL AND id_familia IS NOT NULL)',
            name='check_proprietario_meta'
        ),
    )
#endregion

#region INIT:
    def __init__(self, 
                 nome_meta, 
                 valor_alvo, 
                 data_inicio: date, 
                 prazo_final: date, 
                 id_usuario = None, 
                 id_familia = None,                  
                 aporte_inicial = 0.0
                 ):

        if id_usuario and id_familia:
            raise ValueError("Uma meta não pode pertencer a um usuário e a uma família simultaneamente.")
        if not id_usuario and not id_familia:
            raise ValueError("A meta deve pertencer a pelo menos um usuário ou a uma família.")
        
        self.nome_meta = nome_meta
        self.valor_alvo = valor_alvo
        self.aporte_inicial = aporte_inicial
        self.data_inicio = data_inicio

        self.prazo_final = prazo_final
        if prazo_final <= data_inicio:
            raise ValueError("O prazo final deve ser posterior à data de início.")

        self.id_usuario = id_usuario
        self.id_familia = id_familia
#endregion

#region PROPRIEDADES E MÉTODOS DE METAS:
    @property
    def valor_poupado(self):
        """
        Calcula o total acumulado na meta.
        Considera o aporte inicial + depósitos (receitas/transferências) 
        - retiradas (despesas).
        """
        entradas = sum(t.valor for t in self.transacoes if t.tipo in ["receita", "transferencia", "dividendo"])
        saidas = sum(t.valor for t in self.transacoes if t.tipo == "despesa")
        
        return self.aporte_inicial + (entradas - saidas)

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
        meses_diff = (self.prazo_final.year - hoje.year) * 12 + (self.prazo_final.month - hoje.month)

        meses_para_calculo = max(1, meses_diff)

        return round(valor_restante / meses_para_calculo, 2)

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
#endregion
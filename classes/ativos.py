from datetime import datetime, date
from database.config import Base, SessionLocal
from sqlalchemy import Column, ForeignKey, Integer, Float, String, DateTime, Date, foreignKey, Boolean
from sqlalchemy.orm import relationship

class Ativo(Base):
    """ Criando a tabela "ativos" para armazenar os ativos financeiros do usuário, como ações, fundos imobiliários, criptomoedas, etc. 
    Essa tabela pode ser usada para calcular o patrimônio líquido do usuário, a rentabilidade dos investimentos, etc."""
    
    __tablename__ = "ativos"

    id_ativo = Column(Integer, primary_key=True, autoincrement=True) # id único do ativo, o primary key impede que hajam mais de uma chave igual e o autoincrement adiciona 1 a cada novo ativo
    nome_ativo = Column (String, nullable = False) # nome do ativo financeiro, como o nome da ação, do fundo imobiliário, da criptomoeda, etc. O campo nome_ativo é usado para identificar o ativo e deve ser único para evitar confusão entre ativos diferentes. O campo nome_ativo é obrigatório, pois é essencial para a identificação do ativo.
    tipo_ativo = Column(String, nullable=False) # tipo do ativo financeiro, como ação, fundo imobiliário, criptomoeda, etc. O campo tipo_ativo é usado para categorizar os ativos do usuário e pode ser útil para filtrar os ativos em gráficos e relatórios, ou para aplicar regras específicas de acordo com o tipo de ativo, como por exemplo, calcular a rentabilidade de uma ação de forma diferente da rentabilidade de um fundo imobiliário.  
    quantidade = Column(Float, nullable=False) # quantidade do ativo financeiro que o usuário possui. O campo quantidade é usado para calcular o valor total do ativo, multiplicando a quantidade pelo preço unitário do ativo, e também para calcular a rentabilidade do ativo ao longo do tempo, levando em consideração as variações de preço e a quantidade de ativos que o usuário possui. O campo quantidade é obrigatório, pois um ativo sem quantidade não tem valor prático.
    preco_unitario = Column(Float, nullable=False) # preço unitário do ativo financeiro, ou seja, o preço de cada unidade do ativo. O campo preco_unitario é usado para calcular o valor total do ativo, multiplicando a quantidade pelo preço unitário, e também para calcular a rentabilidade do ativo ao longo do tempo, levando em consideração as variações de preço. O campo preco_unitario é obrigatório, pois um ativo sem preço unitário não tem valor prático.
    data_aquisicao = Column(Date, nullable=False) # data de aquisição do ativo financeiro, ou seja, a data em que o usuário comprou o ativo. O campo data_aquisicao é usado para calcular a rentabilidade do ativo ao longo do tempo, levando em consideração as variações de preço desde a data de aquisição, e também para exibir informações relevantes ao usuário, como há quanto tempo ele possui o ativo. O campo data_aquisicao é obrigatório, pois um ativo sem data de aquisição não tem valor prático.
    
    # relacionamento com outras tabelas:
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario")) # id do usuário ao qual o ativo pertence, para garantir que cada usuário tenha seus próprios ativos financeiros registrados no sistema. O campo id_usuario é usado para criar um relacionamento entre o ativo e o usuário, permitindo que o sistema associe os ativos ao usuário correto e exiba as informações dos ativos de forma personalizada para cada usuário. O campo id_usuario é uma chave estrangeira que referencia a coluna id_usuario da tabela de usuários, garantindo a integridade referencial entre os ativos e os usuários no banco de dados.
    id_indice = Column(Integer, ForeignKey("indices.id_indice"), nullable=True) # id do índice financeiro associado ao ativo, para permitir que o usuário vincule um índice financeiro específico ao ativo, como a taxa SELIC para uma ação de renda fixa, ou a inflação medida pelo IPCA para um fundo imobiliário. O campo id_indice é usado para criar um relacionamento entre o ativo e um índice financeiro, permitindo que o sistema utilize o valor do índice para calcular a rentabilidade do ativo ou corrigir o valor do ativo de acordo com a inflação, por exemplo. O campo id_indice é opcional, pois nem todos os ativos precisam estar associados a um índice financeiro.
    id_conta = Column(Integer, ForeignKey("contas.id_conta")) # id da conta associada ao ativo, para permitir que o usuário vincule um ativo a uma conta específica, como uma conta de investimento ou uma conta de poupança. O campo id_conta é usado para criar um relacionamento entre o ativo e uma conta, permitindo que o sistema associe os ativos às contas corretas e exiba as informações dos ativos de forma personalizada para cada conta. O campo id_conta é opcional, pois nem todos os ativos precisam estar associados a uma conta específica.
    id_familia = Column(Integer, ForeignKey("familias.id_familia"), nullable=True) # id da família associada ao ativo, para permitir que o usuário vincule um ativo a uma família específica, caso ele faça parte de uma família no sistema. O campo id_familia é usado para criar um relacionamento entre o ativo e uma família, permitindo que o sistema associe os ativos às famílias corretas e exiba as informações dos ativos de forma personalizada para cada família. O campo id_familia é opcional, pois nem todos os ativos precisam estar associados a uma família específica.

    usuario = relationship("Usuario", back_populates="ativos") # relacionamento com a tabela de usuários, permitindo acessar os ativos de um usuário através do atributo 'ativos' do objeto Usuario, e acessar o usuário associado a um ativo através do atributo 'usuario' do objeto Ativo.
    transacao = relationship("Transacao", back_populates="ativo") # relacionamento com a tabela de transações, permitindo acessar a transação associada a um ativo através do atributo 'transacao' do objeto Ativo, e acessar o ativo associado a uma transação através do atributo 'ativo' do objeto Transacao.
    indice = relationship("IndiceFinanceiro", back_populates="ativos") # relacionamento com a tabela de índices financeiros, permitindo acessar os ativos associados a um índice financeiro através do atributo 'ativos' do objeto IndiceFinanceiro, e acessar o índice financeiro associado a um ativo através do atributo 'indice' do objeto Ativo.

    def __init__(self, nome_ativo, tipo_ativo, quantidade, preco_unitario, data_aquisicao, id_usuario, id_indice=None, id_conta=None, id_familia=None):
        self.nome_ativo = nome_ativo
        self.tipo_ativo = tipo_ativo
        self.quantidade = quantidade
        self.preco_unitario = preco_unitario
        self.data_aquisicao = data_aquisicao
        self.id_usuario = id_usuario
        self.id_indice = id_indice
        self.id_conta = id_conta
        self.id_familia = id_familia
        

    @property
    def valor_investido_total(self):
        # propriedade para calcular o valor total investido no ativo, multiplicando a quantidade pelo preço unitário. 
        # Essa propriedade é útil para exibir o valor total do investimento em um ativo específico, e também para calcular o patrimônio líquido do usuário 
        # levando em consideração o valor total dos ativos que ele possui.
        return self.quantidade * self.preco_unitario
    
    @property
    def valor_atual_total(self):
        # propriedade para calcular o valor total atual do ativo, multiplicando a quantidade pelo preço unitário atualizado. 
        # Essa propriedade é útil para exibir o valor total atual do investimento em um ativo específico, e também para calcular a rentabilidade do ativo ao longo do tempo, 
        # levando em consideração as variações de preço desde a data de aquisição.
        # Para calcular o preço unitário atualizado, seria necessário integrar com uma API de mercado financeiro para obter o preço atual do ativo, 
        # ou permitir que o usuário atualize manualmente o preço unitário do ativo no sistema.
        pass

    @property
    def rentabilidade(self):
        # propriedade para calcular a rentabilidade do ativo, levando em consideração o valor investido total e o valor atual total do ativo. 
        # A rentabilidade pode ser calculada como a diferença entre o valor atual total e o valor investido total, dividida pelo valor investido total, 
        # e multiplicada por 100 para obter a rentabilidade em porcentagem. Essa propriedade é útil para exibir a rentabilidade do investimento em um ativo específico, 
        # e também para calcular a rentabilidade geral do portfólio de investimentos do usuário.
        pass

    @property
    def tempo_posse(self):
        # propriedade para calcular o tempo de posse do ativo, levando em consideração a data de aquisição do ativo e a data atual. 
        # O tempo de posse pode ser calculado como a diferença entre a data atual e a data de aquisição, e pode ser exibido em dias, meses ou anos, dependendo da preferência do usuário. 
        # Essa propriedade é útil para exibir há quanto tempo o usuário possui um ativo específico, o que pode ser relevante para avaliar a performance do investimento ao longo do tempo.
        pass
    @property
    def percentual_portfolio(self):
        # propriedade para calcular o percentual do ativo em relação ao portfólio total de investimentos do usuário, levando em consideração o valor atual total do ativo e o valor total do portfólio de investimentos do usuário. 
        # O percentual do ativo pode ser calculado como o valor atual total do ativo dividido pelo valor total do portfólio de investimentos do usuário, e multiplicado por 100 para obter o percentual. 
        # Essa propriedade é útil para exibir a participação de um ativo específico no portfólio de investimentos do usuário, o que pode ser relevante para avaliar a diversificação dos investimentos e tomar decisões sobre alocação de ativos.
        pass

    @property
    def volatilidade(self):
        # propriedade para calcular a volatilidade do ativo, levando em consideração as variações de preço do ativo ao longo do tempo. 
        # A volatilidade pode ser calculada como o desvio padrão das variações de preço do ativo em um determinado período, como 30 dias, por exemplo. 
        # Essa propriedade é útil para exibir a volatilidade de um ativo específico, o que pode ser relevante para avaliar o risco associado ao investimento em um ativo e tomar decisões sobre alocação de ativos.
        pass
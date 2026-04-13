from argon2 import PasswordHasher
from database.config  import Base, SessionLocal
from sqlalchemy import Column, Integer, Float, String, DateTime, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database.utils.constants import CATEGORIAS_DESPESAS, CATEGORIAS_RECEITA, CATEGORIAS_PATRIMONIO
from classes.categorias import Categoria, Subcategoria, gerar_cor
import datetime

"""############################### USUÁRIOS ########################################################"""
class Usuario(Base): 

#region TABELA E RELACIONAMENTOS:
    __tablename__= "usuarios" # criando a tabela usuarios
    
    # CAMPOS DA TABELA:
    id_usuario = Column(Integer, primary_key=True, autoincrement=True) # id única do usuário, o primary key impede que hajam duas chaves iguais e o autoincrement adiciona 1 a cada novo usuário
    nome = Column(String) # nome do usuário
    email = Column(String, unique=True, nullable=False) # email do usuário
    senha_hash = Column(String(255)) # hash da senha do usuário, para garantir a segurança das senhas armazenadas no banco de dados. O campo senha_hash é preenchido com o hash da senha fornecida pelo usuário durante a criação da conta ou atualização da senha, usando a biblioteca bcrypt para gerar o hash de forma segura. O campo senha_plana não é armazenado no banco de dados, ele é usado apenas para receber a senha em formato plano durante a criação ou atualização da senha, e depois é convertido para hash e armazenado no campo senha_hash.
    renda_mensal = Column(Float, nullable=True) # renda mensal do usuário, pode ser nula caso o usuário não queira informar
    nascimento = Column(Date, nullable=True) # data de nascimento do usuário, pode ser nula caso o usuário não queira informar
    objetivo_reserva = Column(Float, nullable=True) # valor que o usuário estipula como objetivo para sua reserva de emergência, pode ser nulo caso o usuário não queira informar
    data_criacao =  Column(DateTime, default=datetime.datetime.now, nullable=False) # data de criação do usuário, preenchida automaticamente com a data e hora atual quando o usuário é criado
    preferencia_moeda = Column(String(3),nullable=False, default="BRL") # moeda preferida do usuário, preenchida automaticamente com "BRL" caso o usuário não informe uma preferência
    admin_familia = Column(Boolean, nullable=False, default=False) # campo booleano para indicar se o usuário é admin da família.
    
    # CHAVE ESTRANGEIRA:
    id_familia = Column(Integer, ForeignKey("familias.id_familia", ondelete="SET NULL"), nullable=True) # id da família, se houver. Cria um relationship com a coluna id_familia da tabela famílias

    # RELACIONAMENTOS COM OUTRAS TABELAS:
    familia = relationship("Familia", back_populates="membros", foreign_keys=[id_familia])               # CONFERIDO 
    regras_tag = relationship("RegraTag", back_populates="usuario")                                      # CONFERIDO
    categorias = relationship("Categoria", back_populates="usuario")                                     # CONFERIDO
    subcategorias = relationship("Subcategoria", back_populates="usuario")                               # CONFERIDO
    transacoes = relationship("Transacao", back_populates="usuario", cascade="all, delete-orphan")       # CONFERIDO
    contas = relationship("Conta", back_populates="usuario", cascade="all, delete-orphan")               # CONFERIDO
    ativos = relationship("Ativo", back_populates="usuario", cascade="all, delete-orphan")               # CONFERIDO 
    metas = relationship("Meta", back_populates= "usuario", cascade="all, delete-orphan")                # CONFERIDO

#endregion    

#region INIT:
    def __init__(self, 
                 nome, 
                 email, 
                 senha_plana,
                 admin_familia = False,
                 preferencia_moeda = "BRL",
                 renda_mensal = None,
                 nascimento = None,
                 objetivo_reserva = None,
                 id_familia = None
                 ):
        
        self.nome = nome
        self.email = email
        self.admin_familia = admin_familia
        self.preferencia_moeda = preferencia_moeda
        self.id_familia = id_familia
        self.renda_mensal = renda_mensal
        self.nascimento = nascimento
        self.objetivo_reserva = objetivo_reserva
        self.definir_senha(senha_plana) # chama a função definir_senha para gerar o hash da senha e armazenar no campo senha_hash
#endregion

#region MÉTODOS:
    @property
    def saldo_total(self):
        """Soma o saldo de todas as contas ativas vinculadas ao usuário."""
        # O SQLAlchemy gerencia a busca das contas através do relacionamento
        return sum(conta.saldo for conta in self.contas if conta.ativa)

    def definir_senha(self, senha_plana):
        # função que irá gerar o hash a partir da senha digitada pelo usuário, utilizando o algoritmo argon2, e atualizar o campo senha_hash do usuário com o novo hash gerado. 
        # O argon2 é um algoritmo de hashing de senhas considerado muito seguro, e a função PasswordHasher do argon2 é usada para gerar o hash da senha de forma segura, 
        # utilizando parâmetros como tempo de execução, memória e paralelismo para dificultar ataques de força bruta. Depois de gerar o hash, 
        # a função chama a função mod_usuario para salvar a alteração no banco de dados.

        ph = PasswordHasher()
        self.senha_hash = ph.hash(senha_plana) # gera o hash da senha

    def checar_senha(self, senha_digitada):
        # função para verificar se a senha digitada pelo usuário corresponde ao hash armazenado no campo senha_hash do usuário. 
        # A função recebe a senha em formato plano, gera o hash a partir dela usando o mesmo algoritmo e parâmetros usados para gerar o hash original, e compara os dois hashes para verificar 
        # se são iguais. Se os hashes corresponderem, a função retorna True, indicando que a senha digitada é correta. Caso contrário, retorna False.

        ph = PasswordHasher()
        try:
            return ph.verify(self.senha_hash, senha_digitada) # verifica se a senha digitada corresponde ao hash armazenado
        except:
            return False

    def promover_a_admin(self):
    # Transforma o usuário atual em um administrador da sua família.

        from database import SessionLocal # Ajuste conforme seu projeto
        
        db = SessionLocal()
        try:
            # 1. Ativamos a flag de admin no objeto
            self.admin_familia = True
            
            # 2. Persistimos a mudança no banco
            db.merge(self)
            db.commit()
            db.refresh(self)
            
            print(f"Usuário {self.nome} agora é administrador da família {self.id_familia}.")

        except Exception as e:
            db.rollback()
            print(f"Erro ao promover usuário a admin: {e}")
            raise e
        finally:
            db.close()

    def inicializar_novo_usuario(self, session):
        """ Essa função adicionará categorias e subcategorias padrão ao usuário assim que um novo registro for criado."""
        mapa_padrao = {
            "despesa": CATEGORIAS_DESPESAS,
            "receita": CATEGORIAS_RECEITA,
            "patrimonio": CATEGORIAS_PATRIMONIO
        }

        # aqui pegamos os itens da variável mapa padrão que acabamos de criar (com os dados do dict criado em constants) e iteramos:
        for tipo, categorias in mapa_padrao.items():
            # pegamos os valores de mapa padrão e iteramos:
            for nome_cat, lista_subs in categorias.items():
                nova_cat = Categoria(
                    nome=nome_cat, # associamos o nome das chaves dos dicionarios que estão em constants ao nome da categoria
                    tipo=tipo,
                    id_usuario=self.id_usuario,
                    cor_hex= gerar_cor()
                )
                session.add(nova_cat)
                session.flush()

                for nome_sub in lista_subs:
                    nova_sub = Subcategoria(
                        nome=nome_sub,
                        tipo=tipo,
                        id_categoria=nova_cat.id_categoria,
                        id_usuario=self.id_usuario
                    )
                    session.add(nova_sub)
        
        session.commit()

    def add_usuario(self):
        db = SessionLocal() # Estabelece a conexão com o banco de Dados.

        try:
            db.add(self) # adiciona o usuário ao bd
            db.commit() # comita a mudança
            db.refresh(self) # atualiza o bd
            print (f"Usuário {self.id_usuario} adicionado com sucesso!") # imprime uma mensagem de conclusão.
        
        except Exception as e:
            db.rollback() # caso haja algum erro, desfaz a operação.
            print (f"Erro ao adicionar o usuário{self.id_usuario}: {e}") # imprime uma mensagem de conclusão.
            raise e # lança o erro para fora da função.

        finally:
            db.close() # fecha a conexão com o BD

    def del_usuario(self):
        db = SessionLocal() # Estabelece a conexão com o banco de Dados.

        try:
            db.delete(self) # deleta o usuário do DB
            db.commit() # faz a alteração permanentemente
            print(f"Usuário {self.id_usuario} excluído com sucesso!") # imprime uma mensagem de conclusão.

        except Exception as e:
            db.rollback() # caso haja algum erro, desfaz a operação.
            print (f"Erro ao excluir o usuário{self.id_usuario}: {e}") # imprime uma mensagem de conclusão.
            raise e # lança o erro para fora da função.
        
        finally:
            db.close() # fecha a conexão com o BD

    def mod_usuario(self):

        db = SessionLocal() # Estabelece a conexão com o banco de Dados.
        
        try:
            db.merge(self) # mescla o estado atual do objeto com seu equivalente no BD
            db.commit() # salva a alteração no bd
            db.refresh(self) # atualiza o bd com a alteração
            print (f"Dados do usuário{self.id_usuario} alterados com sucesso.") # imprime a msg de conclusão
        
        except Exception as e:
            db.rollback() # caso haja algum erro, desfaz a operação.
            print (f"Erro ao alterar os dados: {e}") # imprime uma mensagem de conclusão.
            raise e # lança o erro para fora da função.

        finally:
            db.close() # fecha a conexão com o BD
#endregion
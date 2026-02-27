import bcrypt
from database.config  import Base, SessionLocal
from sqlalchemy import Column, Integer, Float, String, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship

# Criando a classe usuário:
class Usuario(Base):
    
    __tablename__= "usuarios" # criando a tabela usuarios
    
    id_usuario = Column(Integer, primary_key=True, autoincrement=True) # id única do usuário, o primary key impede que hajam duas chaves iguais e o autoincrement adiciona 1 a cada novo usuário
    nome = Column(String) # nome do usuário
    email = Column(String, unique=True, nullable=False) # email do usuário
    senha_hash = Column(String) # hash da senha do usuário, para garantir a segurança das senhas armazenadas no banco de dados. O campo senha_hash é preenchido com o hash da senha fornecida pelo usuário durante a criação da conta ou atualização da senha, usando a biblioteca bcrypt para gerar o hash de forma segura. O campo senha_plana não é armazenado no banco de dados, ele é usado apenas para receber a senha em formato plano durante a criação ou atualização da senha, e depois é convertido para hash e armazenado no campo senha_hash.
    renda_mensal = Column(Float, nullable=True) # renda mensal do usuário, pode ser nula caso o usuário não queira informar
    nascimento = Column(Date, nullable=True) # data de nascimento do usuário, pode ser nula caso o usuário não queira informar
    objetivo_reserva = Column(Float, nullable=True) # valor que o usuário estipula como objetivo para sua reserva de emergência, pode ser nulo caso o usuário não queira informar
    tipo_usuario = Column(String) # Se o usuário é comum ou admin
    id_familia = Column(Integer, ForeignKey("familias.id_familia")) # id da família, se houver. Cria um relationship com a coluna id_familia da tabela famílias
    
    # relacionamentos com outras tabelas:
    familia_vinculada = relationship("Familia", back_populates="usuarios", foreign_keys=[id_familia])
    regras = relationship("RegraTag", back_populates="usuario")
    categorias = relationship("Categoria", back_populates="usuario")
    subcategorias = relationship("Subcategoria", back_populates="usuario")
    transacoes = relationship("Transacao", back_populates="usuario")
    contas = relationship("Conta", back_populates="usuario")
    
    def __init__(self, 
                 nome, 
                 email, 
                 senha_plana,
                 renda_mensal = None,
                 nascimento = None,
                 objetivo_reserva = None,
                 tipo_usuario = "comum", 
                 id_familia = None
                 ):
        
        self.nome = nome
        self.email = email
        self.tipo_usuario = tipo_usuario
        self.id_familia = id_familia
        self.renda_mensal = renda_mensal
        self.nascimento = nascimento
        self.objetivo_reserva = objetivo_reserva

        # gerando o hash da senha usando bcrypt, o salt é gerado automaticamente pela função gensalt, e o hash é gerado a partir da senha em formato plano e do salt, depois o hash é decodificado para string e armazenado no campo senha_hash do usuário.
        salt = bcrypt.gensalt()
        self.senha_hash = bcrypt.hashpw(senha_plana.encode('utf-8'),salt).decode('utf-8')

    def checar_senha(self, senha_digitada):
        # função para verificar se a senha digitada pelo usuário corresponde ao hash armazenado no banco de dados. 
        # Recebe a senha digitada em formato plano, converte para bytes, gera um hash usando o mesmo salt e compara com o hash armazenado. 
        # Retorna True se as senhas corresponderem e False caso contrário.

        return bcrypt.checkpw(senha_digitada.encode('utf-8'), self.senha_hash.encode('utf-8'))
        
    def atualizar_senha(self, nova_senha_plana):
    # função para atualizar a senha do usuário, recebe a nova senha em formato plano, gera um novo hash e atualiza o campo senha_hash do usuário com o novo hash. 
    # Depois chama a função mod_usuario para salvar a alteração no banco de dados.
    
        salt = bcrypt.gensalt() # gera um novo salt para a nova senha
        self.senha_hash = bcrypt.hashpw(nova_senha_plana.encode('utf-8'), salt).decode('utf-8') # atualiza o hash da senha com a nova senha fornecida pelo usuário
        self.mod_usuario() # salva a alteração no banco de dados, usando a função mod_usuario para fazer o merge do objeto atualizado com o banco de dados e comitar a mudança.
    
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
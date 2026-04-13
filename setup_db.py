from database.config import engine, Base  
from classes.usuarios import Usuario
from classes.familias import Familia
from classes.contas import Conta
from classes.transacoes import Transacao
from classes.metas import Meta
from classes.regras import RegraTag
from classes.indices import IndiceFinanceiro 
from classes.categorias import Categoria, Subcategoria
from classes.ativos import Ativo 
from classes.convites_familia import ConviteFamilia

def criar_banco():
    print("Iniciando a criação do banco de dados MeuDinheiro...")
    try:
        # Este comando lê todas as classes que herdam de 'Base' e cria as tabelas
        Base.metadata.create_all(bind=engine)
        print("Sucesso! O arquivo do banco de dados foi gerado com todas as tabelas.")
    except Exception as e:
        print(f"Erro ao criar o banco de dados: {e}")

if __name__ == "__main__":
    criar_banco()
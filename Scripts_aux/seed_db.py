from classes.transacoes import Transacao 
from classes.regras import RegraTag
from classes.contas import Conta      
from datetime import date, timedelta
from classes.usuarios import Usuario
from classes.familias import Familia
from classes.contas import ContaCorrente, Cartao
from classes.metas import Meta

### SCRIPT PARA TESTAR SE O BANCO DE DADOS ESTÁ FUNCIONANDO ###

def popular_banco():
    print("Populando o banco de dados com dados de teste...")

    try:
        # 1. Criando a Família
        # O id_admin será preenchido após criarmos o usuário
        familia_araujo = Familia(nome="Família Araujo", id_admin=1)
        familia_araujo.add_familia()

        # 2. Criando o Usuário (Leandro)
        # Localizado em São José dos Campos
        leandro = Usuario(
            nome="Leandro Marcondes Araujo", 
            email="leandro@email.com", 
            senha_plana="senha123", 
            id_familia=1
        )
        leandro.add_usuario()

        # 3. Criando uma Conta Corrente com Cheque Especial
        conta_nubank = ContaCorrente(
            nome_conta="Nubank Principal",
            saldo_inicial=5000.0,
            id_usuario=1,
            banco="Nubank",
            cheque_especial=1000.0,
            vencimento=date(2026, 12, 31)
        )
        conta_nubank.add_conta()
        
        # No seed_db.py, após o add_conta()
        from sqlalchemy.orm import selectinload
        from database.config import SessionLocal

        # Abrimos uma sessão rápida apenas para carregar os dados
        db = SessionLocal()
        # Buscamos a conta novamente, mas forçando o carregamento das transações
        conta_nubank = db.query(ContaCorrente).options(selectinload(ContaCorrente.transacoes)).filter_by(id_conta=1).first()
        db.close()

        # 4. Criando uma Meta de Economia (Data Science Portfolio)
        # Prazo de um ano a partir de hoje
        prazo = date.today() + timedelta(days=365)
        meta_estudos = Meta(
            nome_meta="Curso Avançado de Data Science",
            valor_alvo=2000.0,
            valor_poupado=500.0,
            data_inicio=date.today(),
            prazo_final=prazo,
            id_usuario=1,
            id_familia=1
        )
        meta_estudos.add_meta()

        print("\n--- Teste de Lógica ---")
        print(f"Usuário: {leandro.nome}")
        print(f"Saldo Disponível (c/ limite): R$ {conta_nubank.saldo_total_disponivel}")
        print(f"Status da Meta: {meta_estudos.status_meta}")
        print(f"Sugestão para guardar este mês: R$ {meta_estudos.valor_mensal_sugerido:.2f}")

    except Exception as e:
        print(f"Erro ao popular banco: {e}")

if __name__ == "__main__":
    popular_banco()
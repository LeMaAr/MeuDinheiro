from database.config import SessionLocal
from classes import Conta, Transacao


def testar_properties_conta():
    # script de teste para validar as properties da classe Conta, especialmente a property fatura_atual_cartao, que calcula o valor total das transações pendentes associadas a uma conta 
    # do tipo cartão. O script cria uma conta de teste, adiciona transações pendentes e verifica se a property retorna o valor correto. 
    # Após o teste, os dados são limpos do banco para manter a integridade dos dados de produção.
    
    db = SessionLocal()
    try:
        # 1. Criamos uma conta de teste (Cartão)
        nova_conta = Conta(
            nome_conta="Cartão Teste",
            saldo_inicial=0,
            id_usuario=1,
            tipo_conta="cartao",
            limite=1000.0
        )
        db.add(nova_conta)
        db.flush() # Gera o ID sem comitar definitivamente

        # 2. Criamos duas transações pendentes
        t1 = Transacao(id_conta=nova_conta.id_conta, valor=150.0, tipo="despesa", quitada=False, id_usuario=1)
        t2 = Transacao(id_conta=nova_conta.id_conta, valor=50.0, tipo="despesa", quitada=False, id_usuario=1)
        db.add_all([t1, t2])
        db.flush()

        # --- VALIDAÇÃO ---
        print(f"Teste Fatura: {nova_conta.fatura_atual_cartao}") 
        # Deve imprimir 200.0
        
        if nova_conta.fatura_atual_cartao == 200.0:
            print("✅ Property fatura_atual_cartao: OK!")
        else:
            print("❌ Erro no cálculo da fatura.")

    finally:
        db.rollback() # Limpa os dados de teste do banco
        db.close()

testar_properties_conta()
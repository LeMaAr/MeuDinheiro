import pandas as pd
from database.config import SessionLocal
from classes import Transacao, Categoria, Conta 

def get_saldo_geral(id_usuario):
    """Retorna apenas o valor do saldo somado de todas as contas."""
    db = SessionLocal()
    try:
        contas = db.query(Conta).filter(Conta.id_usuario == id_usuario).all()
        return sum(c.saldo_atual for c in contas) 
    finally:
        db.close()

def get_data_despesas(id_usuario):
    """Foco exclusivo na aba de Despesas."""
    db = SessionLocal()
    try:
        query = db.query(
            Transacao.valor,
            Categoria.nome.label("categoria"),
            Categoria.cor_hex
        ).join(Categoria, Transacao.id_categoria == Categoria.id_categoria)\
         .filter(Transacao.id_usuario == id_usuario, Transacao.tipo == "despesa").all() #
        
        df = pd.DataFrame(query)
        return df.to_dict('records') if not df.empty else []
    except Exception as e:
        print(f"Erro em get_data_despesas: {e}")
        return []
    finally:
        db.close()

def get_fluxo_caixa(id_usuario):
    """Visão completa: Despesas, Transferências e Investimentos."""
    db = SessionLocal()
    try:
        tipos_saida = ["despesa", "transferencia", "investimento"]
        query = db.query(
            Transacao.valor,
            Transacao.tipo,
            Categoria.nome.label("categoria"),
            Categoria.cor_hex
        ).join(Categoria, Transacao.id_categoria == Categoria.id_categoria)\
         .filter(Transacao.id_usuario == id_usuario, Transacao.tipo.in_(tipos_saida)).all()
        
        df = pd.DataFrame(query)
        return df.to_dict('records') if not df.empty else []
    except Exception as e:
        print(f"Erro em get_fluxo_caixa: {e}")
        return []
    finally:
        db.close()
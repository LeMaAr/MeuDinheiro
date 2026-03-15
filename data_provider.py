import pandas as pd
from database.config import SessionLocal
from classes import Transacao, Categoria, Conta 
from sqlalchemy import func
from datetime import datetime, timedelta

def get_saldo_geral(id_usuario):
    """Retorna apenas o valor do saldo somado de todas as contas."""
    db = SessionLocal()
    try:
        contas = db.query(Conta).filter(Conta.id_usuario == id_usuario).all()
        return sum(c.saldo_atual for c in contas) #
    finally:
        db.close()

from datetime import datetime, timedelta
from sqlalchemy import func
import pandas as pd

def get_data_despesas(id_usuario, periodo="mensal", data_inicio=None, data_fim=None):
    db = SessionLocal()
    try:
        hoje = datetime.now()
        # Query base: Valor, Categoria e Cor
        query = db.query(
            Transacao.valor,
            Categoria.nome.label("categoria"),
            Categoria.cor_hex
        ).join(Categoria, Transacao.id_categoria == Categoria.id_categoria)\
         .filter(Transacao.id_usuario == id_usuario, func.lower(Transacao.tipo) == "despesa")

        # --- LÓGICA DAS CONDICIONAIS DE TEMPO ---
        if periodo == "hoje":
            query = query.filter(func.date(Transacao.data) == hoje.date())
        
        elif periodo == "semanal":
            # Últimos 7 dias
            query = query.filter(Transacao.data >= hoje - timedelta(days=7))
            
        elif periodo == "mensal":
            # Mês e Ano correntes
            query = query.filter(func.strftime('%m-%Y', Transacao.data) == hoje.strftime('%m-%Y'))

        elif periodo == "bimestral":
            # Últimos 90 dias
            query = query.filter(Transacao.data >= hoje - timedelta(days=60))

        elif periodo == "trimestral":
            # Últimos 90 dias
            query = query.filter(Transacao.data >= hoje - timedelta(days=90))
            
        elif periodo == "semestral":
            # Últimos 180 dias
            query = query.filter(Transacao.data >= hoje - timedelta(days=180))
            
        elif periodo == "anual":
            # Ano corrente
            query = query.filter(func.strftime('%Y', Transacao.data) == hoje.strftime('%Y'))
            
        elif periodo == "personalizado" and data_inicio and data_fim:
            # Entre duas datas específicas (vinda de um DatePicker, por exemplo)
            query = query.filter(Transacao.data.between(data_inicio, data_fim))

        # --- PROCESSAMENTO DOS DADOS ---
        df = pd.DataFrame(query.all())
        
        if df.empty:
            return []

        # Agrupa os valores por categoria e seleciona as 6 maiores
        df_resumo = df.groupby(['categoria', 'cor_hex'])['valor'].sum().nlargest(6).reset_index()
        
        return df_resumo.to_dict('records')
        
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

def get_ultimas_movimentacoes(id_usuario, limite=5):
    """Busca as transações mais recentes para o widget de resumo."""
    db = SessionLocal()
    try:
        from classes import Transacao, Categoria
        
        # Query unindo transações e categorias para pegar nomes e cores
        query = db.query(
            Transacao.descricao,
            Transacao.valor,
            Transacao.data,
            Transacao.tipo,
            Categoria.nome.label("categoria")
        ).join(Categoria, Transacao.id_categoria == Categoria.id_categoria)\
         .filter(Transacao.id_usuario == id_usuario)\
         .order_by(Transacao.data.desc())\
         .limit(limite).all()
        
        # Converte para DataFrame para facilitar a formatação de data
        import pandas as pd
        df = pd.DataFrame(query)
        
        if not df.empty:
            df['data'] = df['data'].dt.strftime('%d/%m/%Y')
            return df.to_dict('records')
        return []
    except Exception as e:
        print(f"Erro ao buscar últimas movimentações: {e}")
        return []
    finally:
        db.close()
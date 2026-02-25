import pandas as pd
from database.config import SessionLocal
from datetime import datetime
from sqlalchemy import func
from classes.usuarios import Usuario
from classes.regras import RegraTag
from classes.contas import Conta
from classes.transacoes import Transacao
from classes.familias import Familia

# Lê um CSV e salva as transações no banco de dados.

def sugerir_tag_inteligente(descricao_csv, id_usuario):
    db = SessionLocal()
    desc_limpa = descricao_csv.upper()

    # 1. TENTA PELA TABELA DE REGRAS (Prioridade Máxima)
    # Verifica se alguma palavra-chave cadastrada na classe regras está contida na descrição do CSV
    regra = db.query(RegraTag).filter(func.instr(desc_limpa, RegraTag.palavra_chave) > 0, RegraTag.id_usuario == id_usuario).first()
    
    if regra:
        db.close()
        return regra.tag_destino

    # 2. TENTA PELO HISTÓRICO DE TRANSAÇÕES
    # Busca a tag mais frequente para descrições similares no passado
    historico = db.query(Transacao.tag).filter( Transacao.id_usuario == id_usuario,                    # <- busca na tabela "transacoes" se o usuário é o mesmo passado pelo argumento da função
    Transacao.descricao.ilike(f"%{descricao_csv[:10]}%"),                                              # <- na coluna descição, verifica se entre os 10 primeiros caracteres, algum bate com a descrição do csv 
    Transacao.tag != None).group_by(Transacao.tag).order_by(func.count(Transacao.tag).desc()).first()  # <- verifica se há alguma tag cadastrada, então pega todos os resultados e ordena qual aparece mais, retornando esse resultado como sugestão de tag

    db.close()
    
    if historico:
        return historico[0]

    return None # Se chegar aqui, o app precisará perguntar ao usuário

def detectar_mapeamento_universal(df):
    """Analisa o conteúdo das colunas para identificar Data, Valor e Descrição."""
    mapeamento = {'data': None, 'valor': None, 'descricao': None}
    
    for col in df.columns:
        # 1. Tenta identificar a DATA
        # Se conseguirmos converter a coluna para datetime, é a nossa candidata
        if mapeamento['data'] is None:
            try:
                pd.to_datetime(df[col].iloc[:5], dayfirst=True) # Testa as primeiras 5 linhas
                mapeamento['data'] = col
                continue
            except:
                pass

        # 2. Tenta identificar o VALOR (Numérico)
        # Procuramos por colunas que o Pandas já reconheceu como número
        if mapeamento['valor'] is None:
            if df[col].dtype in ['float64', 'int64']:
                mapeamento['valor'] = col
                continue
        
        # 3. Tenta identificar a DESCRIÇÃO
        # Se for texto (object) e ainda não for a data, provavelmente é a descrição
        if mapeamento['descricao'] is None:
            if df[col].dtype == 'object':
                mapeamento['descricao'] = col
    
    return mapeamento

def importar_extrato_csv(caminho_arquivo, id_conta):
    db = SessionLocal()

    df = pd.read_csv(caminho_arquivo)
    
    conta = db.query(Conta).filter_by(id_conta=id_conta).first()
    id_usuario = conta.id_usuario

    if not conta:
        print(f"Erro: Conta {id_conta} não encontrada!")
        db.close()
        return
    
    id_usuario = conta.id_usuario
    db.close()
    
    # O "Cérebro" detecta as colunas sozinho aqui
    mapa = detectar_mapeamento_universal(df)
    
    print(f"Iniciando importação de {len(df)} transações...")
    
    print(f"Colunas detectadas: Data->{mapa['data']}, Valor->{mapa['valor']}, Descrição->{mapa['descricao']}")


    for _, linha in df.iterrows():
        valor_original = float(linha[mapa['valor']])

        # LÓGICA DO TIPO: Se for negativo é despesa, se for positivo é crédito
        tipo_calculado = "despesa" if valor_original < 0 else "receita"
    
        # A classe Transacao espera valor positivo, o sinal a gente usa no 'tipo'
        valor_final = abs(valor_original) 

        # Chamada da função para descobrir as tags
        tag_sugerida = sugerir_tag_inteligente(str(linha[mapa['descricao']]), id_usuario)

        nova_t = Transacao(
            valor=valor_final,
            tipo=tipo_calculado,
            data=pd.to_datetime(linha[mapa['data']], dayfirst=True),
            descricao=str(linha[mapa['descricao']]),
            id_conta=id_conta,
            id_usuario=id_usuario,
            tag=tag_sugerida or "Geral",  # Preenche a tag
            categoria="Importado",        # Atributos obrigatórios
            subcategoria="Indefinido",    # Atributos obrigatórios
            local="N/A",                  # Atributos listados
            tipo_registro="comum"         # Atributos listados
        )
        nova_t.add_transacao()

    print("Importação concluída!")

importar_extrato_csv("meu_extrato_teste.csv", id_conta=1)
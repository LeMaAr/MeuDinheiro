import pandas as pd
from database.config import SessionLocal
from datetime import datetime
from sqlalchemy import func
from classes.usuarios import Usuario
from classes.regras import RegraTag
from classes.contas import Conta
from classes.transacoes import Transacao
from classes.familias import Familia
from classes.categorias import Categoria

# Lê um CSV e salva as transações no banco de dados.

def sugerir_tag_inteligente(descricao_csv, id_usuario):
    """Função para sugerir uma tag com base na descrição do CSV, utilizando regras pré-definidas e histórico de transações do usuário."""
    
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
    """Função para detectar automaticamente quais colunas do CSV correspondem a data, valor e descrição, 
    sem depender de nomes específicos. Ela tenta identificar a coluna de data convertendo para datetime, 
    a coluna  de valor verificando se é numérica, e a coluna de descrição procurando por texto."""
    
    mapeamento = {'data': None, 'valor': None, 'descricao': None} # dicionário para armazenar o mapeamento encontrado
    
    for col in df.columns: # percorre as colunas do DataFrame para tentar identificar cada uma das informações necessárias
        
        # 1. Tenta identificar a DATA convertendo as primeiras linhas para datetime
        if mapeamento['data'] is None: # se ainda não encontrou a coluna de data
            try:
                pd.to_datetime(df[col].iloc[:5], dayfirst=True) # tenta converter as primeiras 5 linhas da coluna para datetime, assumindo formato dia/mês/ano (dayfirst=True)
                mapeamento['data'] = col # se a conversão for bem-sucedida, armazena o nome da coluna no mapeamento
                continue # pula para a próxima coluna, já que essa foi identificada como data
            except:
                pass

        # 2. Tenta identificar o VALOR (Numérico)
        # Procura por colunas que o Pandas já reconheceu como número
        if mapeamento['valor'] is None: # se ainda não encontrou a coluna de valor
            if df[col].dtype in ['float64', 'int64']: # verifica se o tipo de dado da coluna é numérico
                mapeamento['valor'] = col # se for numérico, armazena o nome da coluna no mapeamento
                continue # pula para a próxima coluna, já que essa foi identificada como valor
        
        # 3. Tenta identificar a DESCRIÇÃO
        # Se for texto (object) e ainda não for a data, provavelmente é a descrição
        if mapeamento['descricao'] is None: # se ainda não encontrou a coluna de descrição
            if df[col].dtype == 'object': # verifica se o tipo de dado da coluna é texto (object)
                mapeamento['descricao'] = col # se for texto, armazena o nome da coluna no mapeamento
    
    return mapeamento # retorna o dicionário com os nomes das colunas identificadas para data, valor e descrição

def importar_extrato_csv(caminho_arquivo, id_conta):
    """ Função principal para importar um arquivo CSV de extrato bancário. Ela lê o arquivo, detecta as colunas de data, valor e descrição, 
    e salva as transações no banco de dados, evitando duplicatas."""

    db = SessionLocal()

    df = pd.read_csv(caminho_arquivo) # lê o arquivo CSV usando o Pandas, criando um DataFrame com os dados do extrato
    
    conta = db.query(Conta).filter_by(id_conta=id_conta).first() # busca a conta no banco de dados usando o id_conta fornecido como argumento da função
    id_usuario = conta.id_usuario # obtém o id do usuário associado à conta, para usar nas transações importadas

    mapa = detectar_mapeamento_universal(df) # chama a função para detectar quais colunas do CSV correspondem a data, valor e descrição, e armazena o resultado no dicionário "mapa"
    
    contador_novas = 0 # contador para transações novas importadas
    contador_duplicatas = 0 # contador para transações que foram detectadas como duplicatas e, portanto, não foram importadas

    if not conta: # se a conta não for encontrada no banco de dados, imprime uma mensagem de erro e encerra a função
        print(f"Erro: Conta {id_conta} não encontrada!")
        db.close()
        return
    
    id_usuario = conta.id_usuario # obtém o id do usuário associado à conta, para usar nas transações importadas
    
    # tenta encontrar uma categoria chamada "Importado" para o usuário, para usar como categoria padrão para as transações importadas. 
    # Isso ajuda a organizar as transações importadas em uma categoria específica, facilitando a identificação 
    # e possível reclassificação posterior pelo usuário.
    categoria_obj = db.query(Categoria).filter_by(nome="Importado", id_usuario=id_usuario).first() 

    # se a categoria "Importado" não for encontrada para o usuário, cria uma nova categoria com esse nome, cor neutra e ícone de download.
    if not categoria_obj: 
        categoria_obj = Categoria(
            nome="Importado", 
            id_usuario=id_usuario, 
            cor_hex="#808080", 
            icone="download"
        )
        categoria_obj.add_categoria()
        print(f"Categoria 'Importado' criada para o usuário {id_usuario}")

    # armazena o id da categoria "Importado" para usar nas transações importadas, 
    # garantindo que todas sejam associadas a essa categoria por padrão.
    id_cat_importada = categoria_obj.id_categoria 
    mapa = detectar_mapeamento_universal(df) # chama a função para detectar quais colunas do CSV correspondem a data, valor e descrição, e armazena o resultado no dicionário "mapa"
    
    print(f"Iniciando importação de {len(df)} transações...")
    
    for _, linha in df.iterrows(): # percorre cada linha do DataFrame usando iterrows(), que retorna o índice e a linha como uma série do Pandas. O "_" é usado para ignorar o índice, já que não precisamos dele nesse caso.
        
        data_proc = pd.to_datetime(linha[mapa['data']], dayfirst=True) # processa a data convertendo a string para um objeto datetime, assumindo formato dia/mês/ano (dayfirst=True)
        valor_proc = abs(float(linha[mapa['valor']])) # processa o valor convertendo para float e usando o valor absoluto, já que o tipo (despesa ou receita) será determinado pelo sinal do valor original
        desc_proc = str(linha[mapa['descricao']]) # processa a descrição convertendo para string, para garantir que seja do tipo correto ao comparar com o banco de dados
        valor_original = float(linha[mapa['valor']]) # mantém o valor original com sinal para determinar o tipo da transação (despesa ou receita)

        if detectar_duplicata(db, data_proc, valor_proc, desc_proc, id_usuario): # chama a função para detectar se a transação já existe 
            # no banco de dados, passando a data processada, valor processado, descrição processada e id do usuário como argumentos. 
            # Se a função retornar True, significa que é uma duplicata.
            
            contador_duplicatas += 1 # incrementa o contador de duplicatas, já que essa transação não será importada
            continue

        # LÓGICA DO TIPO: Se for negativo é despesa, se for positivo é crédito
        tipo_calculado = "despesa" if valor_original < 0 else "receita"
    
        # mantém o valor positivo, já que o tipo da transação (despesa ou receita) é determinado separadamente pela variável tipo_calculado. 
        # Isso garante que o valor seja armazenado de forma consistente no banco de dados, independentemente do sinal original no CSV.
        valor_final = abs(valor_original) 

        # chama a função para sugerir uma tag com base na descrição do CSV, passando a descrição processada e o id do usuário como argumentos.
        tag_sugerida = sugerir_tag_inteligente(str(linha[mapa['descricao']]), id_usuario) 

        # cria uma nova instância da classe Transacao usando os dados processados e calculados, incluindo o valor final, tipo calculado, 
        # data processada, descrição processada, id da conta, id do usuário, tag sugerida (ou "Geral" se nenhuma sugestão for encontrada), 
        # e outros atributos necessários para criar a transação no banco de dados.
        nova_t = Transacao(
            valor=valor_final,
            tipo=tipo_calculado,
            data=pd.to_datetime(linha[mapa['data']], dayfirst=True),
            descricao=str(linha[mapa['descricao']]),
            id_conta=id_conta,
            id_usuario=id_usuario,
            tag=tag_sugerida or "Geral",  # Preenche a tag
            id_categoria=id_cat_importada,  
            id_subcategoria=None,         # Subcategoria pode ser determinada posteriormente pelo usuário, ou por regras adicionais, mas inicialmente deixamos como None
            local="N/A",                  # O local geralmente não está presente em extratos bancários, então podemos preencher com "N/A" ou deixar como None, dependendo da estrutura da classe Transacao. Aqui optamos por "N/A" para indicar que a informação não está disponível.
            tipo_registro="comum"         # Definimos o tipo_registro como "comum" para indicar que essa transação é do tipo padrão, e não uma transação recorrente ou de outro tipo específico. Isso é importante para o mapeamento polimórfico definido na classe Transacao, onde o campo tipo_registro é usado para diferenciar entre diferentes tipos de transações.
        )
        
        # chama o método add_transacao() da nova transação para salvar a transação no banco de dados, e incrementa o contador de novas transações importadas.
        nova_t.add_transacao()
        contador_novas += 1
    
    db.close()
    print(f"Importação finalizada: {contador_novas} novas, {contador_duplicatas} duplicadas ignoradas.")

def detectar_duplicata(db, data, valor, descricao, id_usuario): 
    """função para detectar se a transação já existe no banco de dados, comparando data, valor, descrição e id do usuário. 
    Retorna True se encontrar uma transação similar, ou seja, é uma duplicata."""
    return db.query(Transacao).filter(
        Transacao.data == data,
        Transacao.valor == valor,
        Transacao.descricao == descricao,
        Transacao.id_usuario == id_usuario
    ).first() is not None


# if __name__ == "__main__":
#    importar_extrato_csv("Scripts_aux/meu_extrato_teste.csv", id_conta=1) # Importa o arquivo CSV para a conta com ID 1 (ajuste conforme necessário) 
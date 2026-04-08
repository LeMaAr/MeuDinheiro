import pandas as pd
from database.config import SessionLocal
from classes import Transacao, Categoria, Conta
from sqlalchemy import func
from datetime import datetime, timedelta

def calcular_intervalo(periodo, data_inicio_custom=None, data_fim_custom=None):
    """Retorna o intervalo escolhido pelo usuário."""
    hoje = datetime.now()

    if periodo == "hoje":
        # Considerando 00:00hs de hoje até as 23:59
        return hoje.replace(hour=0, minute=0, second=0), hoje
        # essa condicional pega o momento de agora, susbstituindo as horas, minutos e segundos e retornando 00:00:00
        # - esse será o primeiro valor retornado. O segundo valor é o exato momento da consulta,
        # que o sql vai usar para pesquisar as transações diárias. Então em uma consulta 
        # no dia 23/03/26 às 16:00, a função retornaria: 23/03/26 00:00:00, 23/03/26 16:00, período de busca das transações no sql

    elif periodo == "semanal":
        return hoje - timedelta(days=7), hoje
        # O timedelta cria um objeto com um período de tempo (7 dias, nesse caso) e subtrai a data de hoje por esse "bloco", de modo que 
        # as consultas percorrerão esse período. (então, ficaria 23/03 - 7 dias: 16/03 - mantendo o horário da consulta até o dia atual, que é a segunda saída da função )

    elif periodo == "mensal":
        return hoje.replace(day=1, hour=0, minute=0, second=0), hoje
    
    elif periodo == "bimestral":
        return hoje - timedelta(days=60), hoje
    
    elif periodo == "trimestral":
        return hoje - timedelta(days=90), hoje
    
    elif periodo == "semestral":
        return hoje - timedelta(days=180), hoje
    
    elif periodo == "anual":
        return hoje.replace(month=1,day=1,hour=0,minute=0,second=0), hoje
    
    elif periodo == "personalizado":
        return data_inicio_custom, data_fim_custom
    
    return None, None

def recuperar_despesas(id_usuario, periodo = "mensal", categoria_especifica=None, data_inicio_custom=None, data_fim_custom=None):
    # essa função será responsável por retornar as despesas do usuário por período (chamando a função calcular_intervalo) e categorias.
    
    # estabelece concexão com o DB
    db = SessionLocal()
    
    try:
        # pegando o período da consulta:
        inicio, fim = calcular_intervalo(periodo, data_inicio_custom, data_fim_custom)

        # construindo a query principal:
        query = db.query(Transacao.valor, Categoria.nome.label("Categoria"), Categoria.cor_hex, Categoria.icone).join(Categoria, Transacao.id_categoria == Categoria.id_categoria)  

        # filtro de usuário:
        query = query.filter(Transacao.id_usuario == id_usuario)

        # filtro de período:
        if inicio and fim:
            query = query.filter(Transacao.data.between(inicio,fim))

        # filtro de tipo:
        query = query.filter(Transacao.tipo == "despesa")

        # filtro para caso haja alguma categoria específica:
        if categoria_especifica:
            query = query.filter(Categoria.nome == categoria_especifica)

        # criação do dataframe para o tratamento dos dados:
        df = pd.DataFrame(query.all())

        if df.empty:
            return []
    
        # aqui nós agrupamos os valores por categoria e os somamos para ter um valor único por categoria no gráfico
        df_resumo = df.groupby(["Categoria", "cor_hex","icone"])['valor'].sum().reset_index()

        # pegamos os 6 maiores valores e os ordenamos
        df_resumo = df_resumo.sort_values(by='valor', ascending= False).head(6)

        # adicionamos os resultados a uma lista de dicionarios que será utilizada pelo Pandas
        return df_resumo.to_dict('records')
    
    except Exception as e:
        print (f"Erro ao buscar as despesas: {e}")
        return []
    
    finally:
        db.close()

def recuperar_saldo_total(id_usuario):
    # função responsável por somar o saldo em cada conta do usuário, mostrando o saldo total na tela de resumo.

    # estabelece concexão com o DB
    db = SessionLocal()

    try:
        # pesquisa no bd por todas as contas do usuário que não estão marcadas para serem ignoradas
        contas = db.query(Conta).filter(Conta.id_usuario == id_usuario, Conta.ignorar_patrimonio == False).all()

        # aqui nós iteramos o saldo atual (que é uma propriedade que criamos em conta) e somamos tudo 
        total = sum(c.saldo_atual for c in contas)

        return total if total else 0.0
    
    except Exception as e:
        print(f"Erro ao calcular saldo total: {e}")
        return 0.0

    finally:
        db.close()

def recuperar_resumo_mensal(id_usuario):
    # essa função deverá ser capaz de somar as movimentações do usuário no último mês (despesas e receitas) para mostrarmos na tela de resumo.

    # criando a conexão com o DB
    db = SessionLocal()

    hoje = datetime.now()

    try:
        # cria um atalho para o período mensal
        inicio, fim = hoje.replace(day=1, hour=0, minute=0, second=0), hoje
    
        # dividimos a pesquisa para cada tipo: "despesa" ou "receita". Vamos precisar dos dois valores para mostrar na tela inicial do app.
        
        # DESPESA
        # query principal, pegamos a tabela transação e filtramos por id de usuário, por tipo "despesa" e pelo período (mês corrente)
        total_despesas = db.query(func.sum(Transacao.valor))\
        .filter(Transacao.id_usuario == id_usuario)\
        .filter(Transacao.tipo == "Despesa")\
        .filter(Transacao.data.between(inicio,fim)).scalar()

        # RECEITA
        # mesma query da despesa, mas o filtro é por "receita"
        total_receitas = db.query(func.sum(Transacao.valor))\
        .filter(Transacao.id_usuario == id_usuario)\
        .filter(Transacao.tipo == "Receita")\
        .filter(Transacao.data.between(inicio,fim)).scalar()

        # a função retorna um dicionário com as somas das despesas e receitas ou 0.0 para o caso de não existirem transações no período.
        return {
            "despesas": total_despesas or 0.0,
            "receitas": total_receitas or 0.0
            }
    
    except Exception as e:
        print (f" Erro na recuperação dos dados: {e}")
        
        # Retorna o dicionário zerado para o app não travar
        return {"despesas": 0.0, "receitas": 0.0}

    finally:
        db.close()

def recuperar_ultimas_movimentacoes(id_usuario):
    # essa função vai ser responsável por recuperarmos as últimas transações do usuário para adicionarmos ao widget "últimas movimentações"

    # estabelecemos conexão com o DB:
    db = SessionLocal()

    try:

        # consulta principal no bd: pegamos os dados valor, descrição, data da tabela transação e os dados cor hex e nome da tabela categoria e os juntamos usando o id_categoria como referencial 
        query = db.query(Transacao.valor, Transacao.data, Transacao.descricao, Categoria.cor_hex, Categoria.nome).join(Categoria, Transacao.id_categoria == Categoria.id_categoria)

        # aí filtramos pelo usuário:
        query = query.filter(Transacao.id_usuario == id_usuario)

        # crimaos um dataframe para armazenar os resultados:
        df = pd.DataFrame(query.all())

        if df.empty:
            return []
        
        # pegamos as 08 últimas entradas:
        ultimas_entradas = df.sort_values(by='data', ascending=False).head(8)

        # Aqui nós limitamos a descrição para mostrar apenas 20 caracteres para não quebrar o layout da tabela
        ultimas_entradas['descricao'] = ultimas_entradas['descricao'].str.slice(0, 20)

        # retornamos um dict
        return ultimas_entradas.to_dict('records')
    
    except Exception as e:
        print (f"Erro ao recuperar os dados: {e}")
        return []
    
    finally:
        db.close()

def recuperar_agendamentos(id_usuario):
    # essa função vai buscar tudo o que houver agendado na conta do usuário e retornar para usarmos no widget "agendamentos".

    # estabelecendo concexão com o DB
    db = SessionLocal()
    hoje = datetime.now()

    try:
        # primeiro buscamos entre as tabelas transação e categoria os dados que vamos precisar
        agend_transacoes_categorias = db.query(
            Transacao.valor, 
            Transacao.data, 
            Transacao.descricao, 
            Categoria.nome.label('categoria'), 
            Categoria.cor_hex
            ).join(Categoria).filter(Transacao.id_usuario == id_usuario, # aqui filtramos a busca por usuário, se ocorre hoje ou no futuro e se não foi quitada.
                                     Transacao.data >= hoje,
                                     Transacao.quitada == False
                                     ).all()
        
        # criamos o dataframe para o pandas
        df_trans = pd.DataFrame(agend_transacoes_categorias)
        
        # depois vamos buscar na tabela conta os dados do cartão e cheque especial que tbm deverão aparecer:

        # primeiro vamos pesquisar na tabela contas todas as contas que pertencem ao usuário, 
        contas = db.query(Conta).filter(Conta.id_usuario == id_usuario).all()

        # Lógica para a fatura do cartão de crédito. Buscamos em Contas se há algum valor na fatura atual usando o filtro personalizado "fatura_atual_cartao"
        # se houver, adicionamos os dados à tupla eventos_automáticos
        eventos_automaticos = []
        
        for c in contas:
            if c.tipo_conta == "cartao" and c.vencimento_cartao:
                if c.fatura_atual_cartao > 0:
                    eventos_automaticos.append({
                        'valor': c.fatura_atual_cartao,
                        'data': c.vencimento_cartao,
                        'descricao': f"Fatura {c.nome_conta}",
                        'categoria': "Cartão",
                        'cor_hex': '#FF4B4B' # IMPORTANTE"," VERIFICAR COMO ISSO VAI FICAR NO LAYOUT.
                    })

        # logica para o cheque especial.
            if c.tipo_conta == "corrente" and c.uso_cheque_especial > 0:
                eventos_automaticos.append({
                    'valor': c.uso_cheque_especial,
                        'data': c.vencimento or hoje,
                        'descricao': f"Uso do Limite {c.nome_conta}",
                        'categoria': "Bancário",
                        'cor_hex': '#FF904B' # IMPORTANTE"," VERIFICAR COMO ISSO VAI FICAR NO LAYOUT.
                    })
        
        df_contas = pd.DataFrame (eventos_automaticos)


        # agora vamos unir os dados das pesquisas em uma linda tabela pandas pro nosso app poder usar:

        df_final = pd.concat([df_trans, df_contas], ignore_index= True)

        if not df_final.empty:
            df_final['data'] = pd.to_datetime(df_final['data'])
            df_final = df_final.sort_values(by='data', ascending=True)

            return df_final.to_dict('records')
        
        return []
    
    except Exception as e:
        print (f"Não foi possível recuperar os dados dos agendamentos: {e}")

    finally:
        db.close()

def rastreador_gatilhos(id_usuario):
    # o propósito dessa função é buscar os gatilhos de todas as contas a fim de passar essa informação para o widget de notificações

    # conexão com o DB
    db = SessionLocal()

    # variável para colocar os alertas
    todos_os_alertas = []

    try:
        # verifica a tabela contas e busca todas as contas associadas ao usuário.
        contas = db.query(Conta).filter(Conta.id_usuario == id_usuario).all()

        # em cada conta, aplica a função de verificação que criamos na classe contas.
        for conta in contas:
            alertas_contas = conta.verificar_gatilhos()
            # caso hajam alertas, nós estendemos a lista de alertas com os gatilhos encontrados em cada conta, de modo que no final do loop teremos uma lista completa de gatilhos.
            if alertas_contas:
                todos_os_alertas.extend(alertas_contas)  
        
        return todos_os_alertas if todos_os_alertas else []
    
    except Exception as e:
        print (f"Erro ao recuperar os alertas: {e}")
        return []
        
    finally:
        db.close()
from classes.transacoes import Transacao
from classes.regras import RegraTag
from classes.metas import Meta
from database.config import SessionLocal


def criar_movimentacao(valor, 
                       tipo, 
                       id_usuario, 
                       id_conta, 
                       descricao, 
                       data, 
                       local="", 
                       **kwargs
                       ):
    
    """ Essa função será responsável pela entrada de novas movimentações do usuário. Ela vai checar se a transação é uma duplicata,
    usando o método criado para isso na classe transações, depois ela vai categorizar a transação usando o método criado 
    na classe RegraTag. Caso a transação já exista, ela não chega a adicionar a nova movimentação no Banco de Dados"""

    db = SessionLocal()

    try:
        # 1. Gerar hash e verificar duplicidade
        hash_temp = Transacao.gerar_hash_estatico(valor, data, descricao, local)
        if db.query(Transacao).filter_by(hash_unico=hash_temp).first():
            print (f"Transação duplicada ignorada: {descricao}")
            return None
                
        # 2. Buscar RegraTag para categorizar
        id_cat = kwargs.get('id_categoria')
        id_subcat = kwargs.get('id_subcategoria')

        if not id_cat:
            regra = RegraTag.buscar_regra(f"{descricao} {local}", id_usuario)
            if regra:
                id_cat = regra.id_categoria
                id_subcat = regra.id_subcategoria

        # 3. Criar objeto Transacao e usar .salvar()
        nova_transacao = Transacao(
            valor=valor,
            tipo=tipo,
            id_usuario=id_usuario,
            id_conta=id_conta,
            descricao=descricao,
            data=data,
            local=local,
            hash_unico=hash_temp,
            id_categoria=id_cat,
            id_subcategoria=id_subcat,
            id_meta=kwargs.get('id_meta'),
            quitada=kwargs.get('quitada', True)
        )

        nova_transacao.salvar()
    
        return nova_transacao
 
    except Exception as e:
        print(f"Erro: {e}")
        return None

    finally:
        db.close()

def registrar_transferencia(id_usuario, 
                            id_origem, 
                            id_destino, 
                            valor, 
                            data, 
                            descricao="Transferência"
                            ):

    """ Essa função será responsável por registrar transferências entre contas de um mesmo usuário, evitando que o valor transferido 
    não suma no meio do processo de transferência. Ela criará uma transação de saída(despesa) na conta de origem e uma de 
    entrada (receita) na conta destino. """
    
    
    try:
        # registro da saída na conta de origem:
        saida = criar_movimentacao(valor=valor,
                                   tipo = "despesa",
                                   id_usuario=id_usuario,
                                   id_conta=id_origem,
                                   descricao=f"{descricao} (Saída)",
                                   data=data,
                                   local="Transferência Interna",
                                   quitada=True
                                   )
        if not saida:
            print ("Falha ao registrar a saída da transferência.")
            return False
        
        # registro da entrada na conta de destino: 
        entrada = criar_movimentacao(valor=valor,
                                     tipo = "receita",
                                     id_usuario=id_usuario,
                                     id_conta=id_destino,
                                     descricao=f"{descricao} (Entrada)",
                                     data=data,
                                     local="Transferência Interna",
                                     quitada=True
                                     )
        if not entrada:
            print ("Falha ao registrar a entrada da transferência.")
            return False

    except Exception as e:
        print(f"Erro ao realizar transferência: {e}")
        return False

def alterar_status_quitacao(id_transacao, status=True):
    """ Muda o status de 'quitada' da transação (usada para conciliação ou agendamentos)."""
    
    db = SessionLocal()
    
    try:
        transacao = db.query(Transacao).filter_by(id_transacao=id_transacao).first()
        if transacao:
            transacao.quitada = status
            transacao.salvar()
            return True
        return False
    finally:
        db.close()
  
def deletar_movimentacao(id_transacao):
    """ Remove uma transação do banco de dados. 
    O saldo da conta será recalculado automaticamente na próxima leitura pela @property saldo_atual de Contas."""

    db = SessionLocal()
    try:
        # Buscamos o objeto na sessão local
        transacao = db.query(Transacao).filter_by(id_transacao=id_transacao).first()
        
        if transacao:
            transacao.deletar()
            print(f"Transação {id_transacao} removida com sucesso.")
            return True
            
        print(f"Transação {id_transacao} não encontrada.")
        return False
        
    except Exception as e:
        print(f"Erro ao deletar movimentação: {e}")
        return False
    
    finally:
        db.close()

def processar_lote_movimentacoes(lista_dados):
    """ Recebe uma lista de dicionários e tenta criar as movimentações uma a uma.
    Retorna um resumo de sucesso e falhas. """

    sucesso = 0
    falhas = 0

    for dados in lista_dados:
        # Reutilizamos a função inteligente que você já criou!
        resultado = criar_movimentacao(**dados)
        
        if resultado:
            sucesso += 1
        else:
            falhas += 1
            
    print(f"📊 Processamento concluído: {sucesso} criadas, {falhas} ignoradas (duplicatas ou erros).")
    return {"sucesso": sucesso, "falhas": falhas}

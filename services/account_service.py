from classes.contas import Conta, SubtipoConta, TipoInstituicao, Conta_Corrente, Conta_Cartao
from classes.transacoes import Transacao
from database.config import SessionLocal

def cadastrar_conta(id_usuario, 
                    nome_conta, 
                    subtipo_conta, 
                    tipo_instituicao="outro", 
                    saldo_inicial=0, 
                    **kwargs
                    ):
    
    """ Função responsável pelo cadastro de novas contas para o usuário.
    Usa 'subtipo_conta' para (corrente, cartao, etc) e 'tipo_instituicao' para (banco, fintech, etc)."""
    
    try:
        # 1. Validação do Subtipo (corrente, cartao, etc)
        if isinstance(subtipo_conta, str):
            try:
                subtipo_conta = SubtipoConta(subtipo_conta.lower().strip())
            except ValueError:
                print(f"Erro: O subtipo '{subtipo_conta}' não é válido.")
                return None

        # 2. Validação da Instituição (banco, fintech, etc)
        if isinstance(tipo_instituicao, str):
            try:
                tipo_instituicao = TipoInstituicao(tipo_instituicao.lower().strip())
            except ValueError:
                tipo_instituicao = TipoInstituicao.outro
       
        # 3. Criação do Objeto
        #esse trecho serve para decidir qual tipo_conta deverá ser usado.
        subtipo_str = subtipo_conta.value

        if subtipo_str == "corrente":
            classe_para_instanciar = Conta_Corrente
        elif subtipo_str == "cartao":
            classe_para_instanciar = Conta_Cartao
        else:
            classe_para_instanciar = Conta

        nova_conta = classe_para_instanciar(
            id_usuario=id_usuario,
            nome_conta=nome_conta,
            subtipo_conta=subtipo_conta,
            tipo_instituicao=tipo_instituicao,
            saldo_inicial=saldo_inicial,            
            ignorar_patrimonio=kwargs.get('ignorar_patrimonio', False)
        )
        
        nova_conta.salvar()
        print(f"Conta '{nome_conta}' ({subtipo_conta.value}) cadastrada com sucesso!")
        return nova_conta
    
    except Exception as e:
        print(f"Erro ao cadastrar conta: {e}")
        return None

def editar_conta(id_conta, 
                 **dados_atualizados):
    # função responsável pela atualização das contas, receberá campos dinâmicos via kwargs.

    db = SessionLocal()

    try:
        conta = db.query(Conta).filter_by(id_conta=id_conta).first()
            
        if not conta:
            print (f" Conta {id_conta} não encontrada.")
            return False

        # mapeamos os campos que poderão ser modificados:
        campos_permitidos = [
            'nome_conta', 
            'subtipo_conta', 
            'tipo_instituicao', 
            'saldo_inicial', 
            'limite', 
            'vencimento_cartao',
            'fechamento_cartao',
            'cheque_especial',
            'vencimento',
            'ignorar_patrimonio',
            'cor_perfil',
            'limite_seguranca',
            'ativa',
        ]

        for campo, valor in dados_atualizados.items():
            if campo in campos_permitidos:
                if campo == 'subtipo_conta' and isinstance(valor, str):
                    valor = SubtipoConta(valor.lower().strip())

                if campo == 'tipo_instituicao' and isinstance(valor, str):
                    valor = TipoInstituicao(valor.lower().strip())

                setattr(conta, campo, valor)
        
        conta.salvar()

        print(f"Conta {conta.nome_conta} atualizada com sucesso!")
        return True
    
    except Exception as e:
        print (f"Erro ao tentar alterar a conta solicitada: {e}")
        return False
    
    finally:
        db.close()
 
def deletar_conta_e_historico(id_conta, 
                              confirmar_exclusao_historico=False
                              ):
    """Função responsável por deletar uma conta do registro. Ela deletará também todas as transações associadas
    àquela conta em particular.Evitando transações órfans no BD"""

    db =  SessionLocal()

    try:
        conta =  db.query(Conta).filter_by(id_conta=id_conta).first()

        if not conta:
            print(f"Conta{id_conta} não encontrada.")
            return False
        
        # checa se há transações associadas à conta:
        total_transacoes =  db.query(Transacao).filter_by(id_conta=id_conta).count()

        if total_transacoes > 0:
            if not confirmar_exclusao_historico:
                print(f"ATENÇÃO: Essa conta possui {total_transacoes} no histórico. Tem certeza que quer deletar a conta e todas as transações nela?")
                return {"status": "request_confirmation", "total": total_transacoes}
            
            # se confirmado, deletamos as transações primeiro:
            db.query(Transacao).filter_by(id_conta=id_conta).delete()
            print(f"{total_transacoes} removidas.")

        # deleta a conta:
        conta.deletar()
        db.commit()
        print(f"Conta{id_conta} e seu hisórico foram apagados.")
        return {"status":"success"}
    
    except Exception as e:
        db.rollback()
        print(f"Erro crítico ao deletar conta: {e}")
        return {"status": "error", "message": str(e)}
    
    finally:
        db.close()
    


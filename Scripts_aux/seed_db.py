import random
from faker import Faker
from database.config import SessionLocal
from classes.usuarios import Usuario
from classes.familias import Familia
from classes.convites_familia import ConviteFamilia
from classes.contas import Conta
from classes.transacoes import Transacao
from classes.categorias import Categoria, Subcategoria
from classes.regras import RegraTag
from classes.ativos import Ativo
from classes.indices import IndiceFinanceiro
from classes.metas import Meta
from datetime import date, timedelta
from utils.tools import gerar_cor

fake = Faker('pt_BR')

def gerar_massa_de_dados(qtd_familias = 4,
                         membros_por_familia = 3
                         ):
    
    db = SessionLocal()
    senha_teste = "senha123"

    try:
        print(f"Iniciando a geração de {qtd_familias} famílias...")

        #region --- Famílias e Usuários ---
        
        # criando primeiro as famílias para termos integridade referencial.
        for _ in range(qtd_familias):
            nova_familia = Familia(nome_familia=f" Família {fake.last_name()}")
            nova_familia.salvar()

            # criando os usuários que farão parte das famílias criadas
            usuarios_da_familia = []

            for i in range(membros_por_familia):
               
                novo_usuario = Usuario(
                    nome = fake.name(),
                    email = fake.email(),
                    senha_plana = senha_teste,
                    id_familia = nova_familia.id_familia,
                    admin_familia = (i == 0)
                )
                novo_usuario.salvar()
                usuarios_da_familia.append(novo_usuario)
        #endregion

            #region --- Categorias & Subcategorias---
            admin = usuarios_da_familia[0]

            cats_config = {
                "Alimentação": ["Mercado", "Restaurante", "Ifood"],
                "Transporte": ["Combustível", "Estacionamento", "Manutenção", "Seguro", "Ônibus", "Uber"],
                "Lazer": ["Cinema", "Viagem", "Streaming", "Games"],
                "Saúde": ["Convênio Médico", "Academia", "Farmácia"],
                "Moradia": ["Aluguel", "Condomínio", "Energia", "Internet", "Manutenção", "Água"],
                "Educação": ["Livros", "Escola das Crianças", "Material Escolar"]
            }

            # adicionando categorias
            for nome_cat, sub_nomes in cats_config.items():
                nova_cat = Categoria( nome = nome_cat,
                                     cor_hex = gerar_cor(),
                                     id_usuario = admin.id_usuario
                                     )
                nova_cat.salvar()

                # adicionando subcategorias
                for nome_sub in sub_nomes:
                    nova_sub = Subcategoria(nome = nome_sub,
                                            id_categoria = nova_cat.id_categoria,
                                            id_usuario = admin.id_usuario
                                            )
                    nova_sub.salvar()
            #endregion

            #region --- Contas ---
            for user in usuarios_da_familia:

                tipos_possiveis = ["corrente",
                                "cartao",
                                "poupanca",
                                "dinheiro",
                                "investimento",
                                "salario",
                                "outro"
                                ]
                tipo_escolhido = random.choice(tipos_possiveis)

                bancos_br = ["Itaú", "Bradesco", "Santander", "Nubank", "Inter", "Caixa", "Banco do Brasil", "C6"]

                parametros_conta = {
                    "nome_conta" : random.choice(bancos_br),
                    "id_usuario" : user.id_usuario,
                    "tipo_conta" : tipo_escolhido,
                    "saldo_inicial" : random.uniform(500, 10000)
                }

                if tipo_escolhido == "cartao":
                    parametros_conta["limite"] = random.uniform (1000, 20000)
                    parametros_conta["vencimento_cartao"] = random.randint(1,28)
                    parametros_conta["fechamento_cartao"] = random.randint(1,28)

                elif tipo_escolhido == "corrente":
                    parametros_conta["cheque_especial"] = random.uniform(500,5000)
                    parametros_conta["vencimento"] = random.randint(1,28)

                elif tipo_escolhido == "investimento":
                    parametros_conta["ignorar_patrimonio"] = False


                nova_conta = Conta(**parametros_conta)
                nova_conta.salvar()
                #endregion

                #region --- Transações ---               
                sub_ids = [s.id_subcategoria for s in db.query(Subcategoria).filter_by(id_usuario=admin.id_usuario).all()]

                # mensagem de aviso:
                print(f"📊 Gerando 1 ano de histórico para {user.nome}...")

                # adicionando um salário mensal
                for mes in range(12):
                    salario =  Transacao(
                        valor= random.uniform (4000, 18000),
                        tipo = "receita",
                        data = date.today() - timedelta(days=30*mes + random.randint(0,2)),
                        descricao = "Recebimento do Salário",
                        id_usuario = user.id_usuario,
                        id_conta = nova_conta.id_conta
                    )
                    salario.salvar()

                    # adiocionando despesas variadas (20 a 25 por mês)
                    for _ in range(random.randint(20,25)):
                        data_t = date.today() - timedelta(days = random.randint(0, 365))

                        t = Transacao(
                            valor = random.uniform (10,500),
                            tipo = "despesa",
                            data = data_t,
                            descricao = fake.sentence(nb_words=3),
                            id_usuario= user.id_usuario,
                            id_conta = nova_conta.id_conta,
                            id_subcategoria = random.choice(sub_ids) if sub_ids else None
                        )
                        t.salvar()

            print(f"✅ Família {nova_familia.nome_familia} populada!")

        print("\n🏆 Sucesso! O banco 'MeuDinheiro' está cheio de dados reais para análise.")

                #endregion
   
    except Exception as e:
        print(f"❌ Erro: {e}")
        raise e
    
    finally:
        db.close()

if __name__ == "__main__":
    gerar_massa_de_dados()






                


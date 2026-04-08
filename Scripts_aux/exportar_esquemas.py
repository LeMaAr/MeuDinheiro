import pandas as pd
from database.config import engine
from sqlalchemy import inspect

def exportar_esquemas():
    # essa função deverá ser capaz de exportar as tabelas do banco de dados para arquivos csv, que serão úteis para normalizar o Banco de Dados. 

    # cria um objeto inspector para inspecionar o banco de dados e obter informações sobre as tabelas e colunas existentes.
    inspector = inspect(engine) 


    try:
        # aqui utilizamos o método get_table_names() do inspector para obter uma lista com os nomes de todas as tabelas presentes no banco de dados. 
        tabelas = inspector.get_table_names()

        if not tabelas:
            print("Nenhuma tabela encontrada no banco de dados.")
            return
        
        
        # usamos um gerenciador de contexto (with) para criar um objeto ExcelWriter do pandas, que nos permite escrever múltiplos DataFrames em um único arquivo Excel. 
        # O nome do arquivo é "esquemas_bd.xlsx" e o engine utilizado é o 'openpyxl', que é uma biblioteca para ler e escrever arquivos Excel.
        with pd.ExcelWriter("esquemas_bd.xlsx", engine='openpyxl') as writer:
            
            # esse trecho itera sobre a lista de tabelas e pega as colunas de cada tabela usando o método get_columns() do inspector.
            for nome_tabela in tabelas:
                colunas = inspector.get_columns(nome_tabela)

                # UUsamos o método get_foreign_keys() para obter as chaves estrangeiras, caso elas existam, e armazenamos as informações em uma variável.
                fks = inspector.get_foreign_keys(nome_tabela) 
                colunas_com_fk = [fk['constrained_columns'][0] for fk in fks]

                # criamos uma váriável que receberá as informações necessárias para o processo de normalização do BD.
                lista_infos = []

                # iteramos sobre as colunas para pegar as informações que irão preencher a variável que criamos.
                for c in colunas:
                    lista_infos.append({
                        "nome_coluna": c["name"],
                        "tipo_dado": str(c["type"]),
                        "anulavel": "sim" if c["nullable"] else "não",
                        "chave_primaria": "sim" if c["primary_key"] else "não",
                        "chave_estrangeira": "sim" if c["name"] in colunas_com_fk else "não",
                        "valor_padrao": c["default"] if c["default"] else "nenhum"
                    })

                # criamos o objeto DataFrame a partir das informações que acabamos de coletar.
                df = pd.DataFrame(lista_infos)

                # salvamos o DF na aba correspondente.
                df.to_excel(writer, sheet_name=nome_tabela, index=False) 
        
        # imprimimos uma mensagem de conclusão do processo.
        print ("\n Sucesso! Os esquemas do BD foram gerados com sucesso.")

    except Exception as e:
        # caso haja algum erro, imprimimos uma mensagem de erro.
        print (f"\n Ocorreu um erro ao gerar os esquemas do BD: {e}")

# essa condicional garante que a função exportar_esquemas() só seja executada quando o script for executado diretamente, e não quando for importado como um módulo em outro script.
if __name__ == "__main__":
    exportar_esquemas()
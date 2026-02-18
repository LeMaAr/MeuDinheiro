MeuDinheiro - Gerenciador Financeiro Familiar

Este é um projeto de gerenciamento financeiro pessoal e familiar desenvolvido em Python. O objetivo principal é consolidar conhecimentos em Programação Orientada a Objetos (POO) e criar uma base sólida de dados para futuras análises em Data Science.

--- Funcionalidades Planejadas:

Com base no mapa de classes desenvolvido, o sistema conta com:

    Gestão de Transações: Registro detalhado de receitas e despesas com suporte a categorias, subcategorias, tags e geolocalização.

    Contas Multibanco: Suporte a diferentes tipos de conta (Corrente, Poupança, Cartão de Crédito e Carteira Física).

    Transações Recorrentes: Automação para despesas fixas com controle de ciclo e data de término.

    Ambiente Familiar: Sistema de usuários com hierarquia (Administrador da Família) para gestão compartilhada.

    Metas de Economia: Definição e acompanhamento de objetivos financeiros.


--- Tecnologias Utilizadas

    Python 3.12+: Linguagem base para toda a lógica de negócio.

    Streamlit: Interface de usuário moderna e interativa (em desenvolvimento).

    Pandas: Manipulação e análise de dados.

    SQLite(posteriormente o sistema migrará para o postgreSQL): Banco de dados relacional para persistência das informações.

    Git/GitHub: Controle de versão e documentação.


--- Estrutura do Projeto

A organização segue padrões de modularização para garantir escalabilidade:

    classes/: Contém os pacotes e módulos de POO (transacao.py, conta.py, etc).

    docs/: Documentação técnica, incluindo mockups de interface e diagramas de classe.

    database/: Scripts de criação e manutenção do banco de dados SQLite.
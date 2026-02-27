# Copilot / AI Agent Instructions for MeuDinheiro

Purpose: give an AI coding agent the minimal, actionable knowledge to be productive in this repo.

- **Big picture**: pure Python app (Python 3.12+) that models a family finance manager using SQLAlchemy ORM. Core domain models live under `classes/` and are persisted via `database/config.py` (SQLite by default). The DB schema is created by `setup_db.py`.

- **Key directories / files**:
  - `classes/` — SQLAlchemy model classes and business logic (examples: `contas.py`, `transacoes.py`, `usuarios.py`, `familias.py`).
  - `database/config.py` — defines `engine`, `SessionLocal`, and `Base` (DB URL: `sqlite:///database/meudinheiro.db`).
  - `setup_db.py` — runs `Base.metadata.create_all(bind=engine)` to create the SQLite DB file.
  - `importadorCSV.py` — CSV import helper (existing entrypoint for ingest tasks).
  - `requirements.txt` — install dependencies with `pip install -r requirements.txt`.

- **Architecture & patterns an agent must know**:
  - Models inherit from `Base` (SQLAlchemy declarative). Many model classes define instance methods that open their own sessions via `SessionLocal()` and call `add` / `merge` / `delete` / `commit` (see `classes/contas.py` and `classes/transacoes.py`). Do not refactor session management without running local checks.
  - Polymorphic inheritance is used for subtype tables via `__mapper_args__` (e.g. `Conta` -> `ContaCorrente` / `Cartao`; `Transacao` -> `TransacaoRecorrente`). When adding fields or migration-like changes, ensure mapping identities remain consistent.
  - `SessionLocal` is configured with `expire_on_commit=False` to keep object attributes accessible after commit; rely on this behavior when writing code that inspects objects post-commit.

- **Common workflows & commands**:
  - Install dependencies: `pip install -r requirements.txt`.
  - Create DB (SQLite file): `python setup_db.py` (creates `database/meudinheiro.db`).
  - Run one-off scripts: `python importadorCSV.py` or `python MeuDinheiro.py` (note: `MeuDinheiro.py` may be a UI/runner placeholder).

- **Conventions & code style specific to this repo**:
  - Portuguese identifiers and comments are used across code (e.g., `saldo_inicial`, `transacoes`). Preserve names in changes unless performing a deliberate, repo-wide rename.
  - Model methods implement persistence (e.g., `add_transacao()`, `mod_conta()`); changes should keep backwards-compatible method signatures.
  - Logging is mostly done with prints. If introducing structured logging, keep it additive and avoid removing printed messages used in simple scripts.

- **Integration points & external deps**:
  - Primary dependency: SQLAlchemy. Pandas and Streamlit are referenced in README (Streamlit UI is noted as in development). Database is local SQLite by default; migration tooling is not present.

- **Safe change checklist for agents**:
  1. Run `pip install -r requirements.txt`.
  2. Run `python setup_db.py` and verify `database/meudinheiro.db` appears.
  3. Run any modified script (e.g., `python importadorCSV.py`) to smoke-test runtime changes.
  4. When changing models, preserve `__tablename__`, primary key names, and `__mapper_args__` unless intentionally migrating schema.
  5. Avoid changing session-management patterns (SessionLocal usage) in one-off commits — instead add new helpers and adapt call sites incrementally.

- **Examples (how-to snippets an agent can use locally)**
  - Create DB:

    ```bash
    pip install -r requirements.txt
    python setup_db.py
    ```

  - Create and persist a `Transacao` from REPL or script:

    ```py
    from classes.transacoes import Transacao
    t = Transacao(tipo_registro='comum', valor=10.0, tipo='Despesa', categoria='Alimentação', id_conta=1, id_usuario=1)
    t.add_transacao()
    ```

- **Files to inspect when making domain changes**:
  - `classes/contas.py` (accounts + polymorphic types)
  - `classes/transacoes.py` (transaction models + recurring logic)
  - `database/config.py` (DB URL, `SessionLocal`, `Base`)
  - `setup_db.py` (schema creation)

If anything here is unclear or you'd like examples adjusted (e.g., add a migration guideline or Streamlit run instructions), tell me which area to expand.

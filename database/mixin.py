from database.config import SessionLocal

class CRUDMixin:
    """Essa classe servirá para centralizar as operações de banco de dados."""

    def salvar(self):
        db = SessionLocal()
        try:
            db.add(self)
            db.commit()
            db.refresh(self)
            return self
        except Exception as e:
            db.rollback()
            print(f"Erro ao salvar {self.__class__.__name__}: {e}")
            raise e
        finally:
            db.close()

    def modificar(self):
        db = SessionLocal()
        try:
            db.merge(self)
            db.commit()
            return self
        except Exception as e:
            db.rollback()
            print(f"Erro ao atualizar {self.__class__.__name__}: {e}")
            raise e
        finally:
            db.close()

    def deletar(self):
        db = SessionLocal()
        try:
            db.delete(self)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"Erro ao deletar {self.__class__.__name__}: {e}")
            raise e
        finally:
            db.close()
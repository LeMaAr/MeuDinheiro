from datetime import datetime
from typing import List, Optional
import uuid

# Definindo a classe transações.

class Transacao:

    def __init__(self, 
                 valor: float,
                 tipo: str,
                 categoria: str, 
                 subcategoria: str, 
                 idconta: int, 
                 tags: str, 
                 data: Optional[datetime] = None, 
                 descricao: Optional[str] = None, 
                 id: Optional[int] = None, # Deixando o ID como opcional por enquanto. Colocar números sequenciais quando o app estiver pronto.
                 local: str = ""
                 ):
        
        # atributos da classe: 
        if id is None:
            self.id = uuid.uuid4().int
        else:
            self.id = id
                        
        if data is None:
            self.data = datetime.now()
        else:
            self.data = data
        
        self.valor = valor
        self.tipo = tipo
        self.categoria = categoria
        self.subcategoria = subcategoria
        self.idconta = idconta
        self.tags = tags
        self.descricao = descricao
        self.local = local

    # métodos da classe:
    def add_transacao(self):
        
    
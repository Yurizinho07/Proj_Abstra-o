import math
from fastapi import HTTPException

class Produto:
    def __init__(self, id: int, name: str, price: float) -> None:
        self.id = id
        self.name = name
        self.price = price

    @staticmethod
    def validar_dados(name: str, price: float) -> None:
        if len(name.strip()) <= 4:
            raise HTTPException(status_code=400, detail="O nome do produto deve ter mais de 4 caracteres.")
        if not math.isfinite(price) or price <= 0:
            raise HTTPException(status_code=400, detail="O preço deve ser maior que zero.")

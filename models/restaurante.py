from fastapi import HTTPException
from models.usuarios import Usuario


class Restaurante(Usuario):
    def __init__(self, id: int, email: str, password: str, nome_restaurante: str, commission: float):
        super().__init__(id, email, password)
        self.id = id
        self.password = password
        self.nome_restaurante = nome_restaurante
        self.commission = commission
        self.products = []

    def validar_nome(nome_restaurante: str):
        if len(nome_restaurante) <= 5:
            raise HTTPException(
                status_code=400,
                detail="O nome do restaurante deve ter mais de 5 caracteres."
            )
    def validar_comissao(comissao: float):
        if comissao < 0:
            raise HTTPException(
                status_code=400,
                detail="A comissão não pode ser negativa."
            )


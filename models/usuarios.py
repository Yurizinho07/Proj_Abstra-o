import re
from fastapi import APIRouter, HTTPException

class Usuarios:
    def __init__(self, id: int, email: str, password: str):
        self.id = id
        self.email = email
        self.password = password

    def validar_email(email: str):
        padrao_email = r"^[a-zA-Z0-9]+@[a-zA-Z0-9]+\.[a-zA-Z]+$"
        if not re.match(padrao_email, email):
            raise HTTPException(
                status_code=400,
                detail="E-mail inválido."
            )

    def validar_senha(senha: str):
        tem_minuscula = any(letra.islower() for letra in senha)
        tem_maiuscula = any(letra.isupper() for letra in senha)
        tem_numero = any(letra.isdigit() for letra in senha)

        if len(senha) < 5 or not tem_minuscula or not tem_maiuscula or not tem_numero:
            raise HTTPException(
                status_code=400,
                detail="A senha deve ter pelo menos 5 caracteres, uma letra minúscula, uma maiúscula e um número."
            )

    def validar_comissao(comissao: float):
        if comissao < 0:
            raise HTTPException(
                status_code=400,
                detail="A comissão não pode ser negativa."
            )

    


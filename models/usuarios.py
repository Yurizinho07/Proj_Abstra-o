import re
import secrets
from fastapi import HTTPException

class Usuario:
    def __init__(self, id: int, email: str, password: str):
        self.id = id
        self.email = email
        self.password = password

    @staticmethod
    def validar_email(email: str) -> None:
        padrao_email = r"^[a-zA-Z0-9]+@[a-zA-Z0-9]+\.[a-zA-Z]+$"
        if not re.fullmatch(padrao_email, email):
            raise HTTPException(status_code=400, detail="E-mail inválido.")

    @staticmethod
    def validar_senha(senha: str) -> None:
        tem_minuscula = any(letra.islower() for letra in senha)
        tem_maiuscula = any(letra.isupper() for letra in senha)
        tem_numero = any(letra.isdigit() for letra in senha)
        if len(senha) < 5 or not tem_minuscula or not tem_maiuscula or not tem_numero:
            raise HTTPException(
                status_code=400,
                detail="A senha deve ter pelo menos 5 caracteres, uma letra minúscula, uma maiúscula e um número.",
            )

    @classmethod
    def validar_dados_acesso(cls, email: str, senha: str) -> None:
        cls.validar_email(email)
        cls.validar_senha(senha)
    @staticmethod
    def email_em_uso(email: str) -> bool:
        from dados import memoria
        usuarios = memoria.restaurantes + memoria.clientes
        return any(usuario.email == email for usuario in usuarios)

    @staticmethod
    def autenticar(email: str, senha: str) -> dict:
        from dados import memoria
        email = email.strip().lower()
        usuarios = memoria.restaurantes + memoria.clientes
        for usuario in usuarios:
            if usuario.email == email and usuario.password == senha:
                valor_token = secrets.token_hex(24)
                memoria.tokens.append({"id": memoria.proximo_id_token, "token": valor_token, "usuario": usuario})
                memoria.proximo_id_token += 1
                return {"token": valor_token}
        raise HTTPException(status_code=401, detail="Credenciais inválidas.")

Usuarios = Usuario

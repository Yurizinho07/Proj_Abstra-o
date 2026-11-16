import re
import secrets
from abc import ABC, abstractmethod

from fastapi import HTTPException

class Usuario(ABC):
    @abstractmethod
    def __init__(self, id: int, email: str, password: str) -> None:
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
    def autenticar(email: str, senha: str) -> dict:
        from dados import repositorio

        usuario = repositorio.buscar_usuario(email.lower(), senha)
        if usuario is None:
            raise HTTPException(status_code=401, detail="Credenciais inválidas.")
        token = secrets.token_hex(24)
        repositorio.substituir_token(usuario.id, token)
        return {"token": token}

    @staticmethod
    def obter_autenticado(token: str | None) -> "Usuario":
        from dados import repositorio

        usuario = repositorio.buscar_usuario_por_token(token) if token else None
        if usuario is None:
            raise HTTPException(status_code=401, detail="Token inválido.")
        return usuario

Usuarios = Usuario

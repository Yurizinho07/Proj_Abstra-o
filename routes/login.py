from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dados.memoria import token, proximo_id_token
from models.usuarios import Usuarios
import re

router = APIRouter()

class TokenRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def login(dados: TokenRequest):
    global proximo_id_token

    email = dados.email.lower()
    senha = dados.password

    if not re.match(email):
        raise HTTPException(
            status_code=400,
            detail="E-mail inválido."
        )

    for t in token:
        if t.email == email and t.password == senha:
            return {"token": t.token}

    raise HTTPException(
        status_code=401,
        detail="Credenciais inválidas."
    )


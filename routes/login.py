from fastapi import APIRouter
from pydantic import BaseModel
from models.usuarios import Usuario

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def login(dados: LoginRequest) -> dict:
    return Usuario.autenticar(dados.email, dados.password)

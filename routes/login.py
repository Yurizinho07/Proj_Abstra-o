from fastapi import APIRouter, Response
from pydantic import BaseModel
from models.usuarios import Usuario

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def login(dados: LoginRequest, response: Response) -> dict:
    resultado = Usuario.autenticar(dados.email, dados.password)
    response.headers["X-Auth-Token"] = resultado["token"]
    return resultado

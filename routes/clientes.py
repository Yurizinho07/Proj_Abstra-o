from fastapi import APIRouter
from pydantic import BaseModel
from models.cliente import Cliente

router = APIRouter()

class ClienteRequest(BaseModel):
    email: str
    password: str
    name: str

@router.post("/clients")
def criar_cliente(dados: ClienteRequest) -> dict:
    return Cliente.criar(dados.email, dados.password, dados.name)

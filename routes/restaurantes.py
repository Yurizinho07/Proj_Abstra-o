from fastapi import APIRouter, Header
from pydantic import BaseModel
from models.restaurante import Restaurante

router = APIRouter()


class RestauranteRequest(BaseModel):
    email: str
    password: str
    restaurant_name: str
    commission: float
class ProdutoRequest(BaseModel):
    name: str
    price: float
class ComissaoRequest(BaseModel):
    commission: float


@router.post("/restaurants")
def criar_restaurante(dados: RestauranteRequest) -> dict:
    return Restaurante.criar(dados.email, dados.password, dados.restaurant_name, dados.commission)

@router.post("/restaurants/products")
def criar_produto(dados: ProdutoRequest, auth_token: str | None = Header(default=None, convert_underscores=False)) -> dict:
    return Restaurante.adicionar_produto(auth_token, dados.name, dados.price)

@router.delete("/restaurants/products/{id}")
def remover_produto(id: int, auth_token: str | None = Header(default=None, convert_underscores=False)) -> dict:
    return Restaurante.remover_produto(auth_token, id)

@router.patch("/restaurants/")
def atualizar_comissao(dados: ComissaoRequest, auth_token: str | None = Header(default=None, convert_underscores=False)) -> dict:
    return Restaurante.atualizar_comissao(auth_token, dados.commission)

@router.get("/restaurants")
def listar_restaurantes(auth_token: str | None = Header(default=None, convert_underscores=False)) -> list:
    return Restaurante.listar(auth_token)

from fastapi import APIRouter, Header
from pydantic import BaseModel, StrictInt
from models.pedido import Pedido
from facades.pedido_facade import PedidoFacade

router = APIRouter()

class PedidoRequest(BaseModel):
    quantity: StrictInt

@router.post("/restaurant/{ID_RES}/{ID_PROD}/", include_in_schema=False)
@router.post("/restaurants/{ID_RES}/{ID_PROD}/")
def criar_pedido(
    ID_RES: int,
    ID_PROD: int,
    dados: PedidoRequest,
    auth_token: str | None = Header(default=None, alias="auth_token"),
) -> Pedido:
    quantidade = dados.quantity
    pedido = PedidoFacade.realizar_compra(
        token=auth_token,
        restaurante_id=ID_RES,
        produto_id=ID_PROD,
        quantidade=quantidade,
    )
    return pedido

@router.get("/orders/")
def listar_pedidos(
    auth_token: str | None = Header(default=None, convert_underscores=False),
) -> list[Pedido]:
    return PedidoFacade.listar_pedidos(auth_token)

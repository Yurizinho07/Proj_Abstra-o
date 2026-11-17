from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class Pedido:
    id: int
    client_id: int
    restaurant_id: int
    product_id: int
    quantity: int
    created_at: datetime

    @staticmethod
    def criar(token: str | None, restaurante_id: int, produto_id: int, quantidade: int) -> "Pedido":
        from facades.pedido_facade import PedidoFacade

        return PedidoFacade.realizar_compra(token, restaurante_id, produto_id, quantidade)

    @staticmethod
    def listar(token: str | None) -> list["Pedido"]:
        from facades.pedido_facade import PedidoFacade

        return PedidoFacade.listar_pedidos(token)

from fastapi import HTTPException
from models.cliente import Cliente
from models.pedido import Pedido
from models.usuarios import Usuario


class PedidoFacade:
    """Oferece uma interface única para autenticar, validar e persistir compras."""

    @staticmethod
    def realizar_compra(
        token: str | None, restaurante_id: int, produto_id: int, quantidade: int,
    ) -> Pedido:
        from dados import repositorio

        cliente = Usuario.obter_autenticado(token)
        if not isinstance(cliente, Cliente):
            raise HTTPException(status_code=403, detail="Apenas clientes podem realizar compras.")
        if quantidade <= 0:
            raise HTTPException(status_code=400, detail="A quantidade deve ser maior que zero.")
        if quantidade > 2**63 - 1:
            raise HTTPException(status_code=400, detail="A quantidade excede o limite suportado.")
        pedido = repositorio.registrar_pedido(cliente.id, restaurante_id, produto_id, quantidade)
        if pedido is None:
            raise HTTPException(status_code=404, detail="Produto não encontrado no menu deste restaurante.")
        return pedido

    @staticmethod
    def listar_pedidos(token: str | None) -> list[Pedido]:
        from dados import repositorio

        usuario = Usuario.obter_autenticado(token)
        return sorted(
            repositorio.listar_pedidos(usuario),
            key=lambda pedido: (pedido.created_at, pedido.id),
            reverse=True,
        )

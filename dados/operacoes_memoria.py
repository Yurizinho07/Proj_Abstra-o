from datetime import datetime, timezone
from itertools import count
from dados import memoria
from models.cliente import Cliente
from models.pedido import Pedido
from models.produto import Produto
from models.restaurante import Restaurante
from models.usuarios import Usuario

_pedidos: list[Pedido] = []
_ids_pedidos = count(1)

def cadastrar_cliente(email: str, senha: str, nome: str) -> Cliente | None:
    with memoria.lock_usuarios:
        if any(usuario.email == email for usuario in memoria.clientes + memoria.restaurantes):
            return None
        cliente = Cliente(memoria.proximo_id_usuario, email, senha, nome)
        memoria.clientes.append(cliente)
        memoria.proximo_id_usuario += 1
        return cliente

def cadastrar_restaurante(email: str, senha: str, nome: str, comissao: float) -> Restaurante | None:
    with memoria.lock_usuarios:
        if any(usuario.email == email for usuario in memoria.clientes + memoria.restaurantes):
            return None
        restaurante = Restaurante(memoria.proximo_id_usuario, email, senha, nome, comissao)
        memoria.restaurantes.append(restaurante)
        memoria.proximo_id_usuario += 1
        return restaurante

def buscar_usuario(email: str, senha: str) -> Usuario | None:
    with memoria.lock_usuarios:
        for usuario in memoria.clientes + memoria.restaurantes:
            if usuario.email == email and usuario.password == senha:
                return usuario
        return None

def substituir_token(usuario_id: int, token: str) -> None:
    with memoria.lock_usuarios:
        usuario = next(
            usuario for usuario in memoria.clientes + memoria.restaurantes
            if usuario.id == usuario_id
        )
        tokens = [item for item in memoria.tokens if item["usuario"].id != usuario_id]
        tokens.append({"id": memoria.proximo_id_token, "token": token, "usuario": usuario})
        memoria.tokens = tokens
        memoria.proximo_id_token += 1

def buscar_usuario_por_token(token: str) -> Usuario | None:
    with memoria.lock_usuarios:
        return next((item["usuario"] for item in memoria.tokens if item["token"] == token), None)

def adicionar_produto(restaurante_id: int, nome: str, preco: float) -> Produto | None:
    with memoria.lock_usuarios:
        produtos = next(restaurante for restaurante in memoria.restaurantes if restaurante.id == restaurante_id).products
        if any(produto.name.lower() == nome.lower() for produto in produtos):
            return None
        produto = Produto(memoria.proximo_id_produto, nome, preco)
        produtos.append(produto)
        memoria.proximo_id_produto += 1
        return produto

def remover_produto(restaurante_id: int, produto_id: int) -> bool:
    with memoria.lock_usuarios:
        produtos = next(restaurante for restaurante in memoria.restaurantes if restaurante.id == restaurante_id).products
        for produto in produtos:
            if produto.id == produto_id:
                produtos.remove(produto)
                return True
        return False

def atualizar_comissao(restaurante_id: int, comissao: float) -> None:
    with memoria.lock_usuarios:
        restaurante = next(restaurante for restaurante in memoria.restaurantes if restaurante.id == restaurante_id)
        restaurante.commission = comissao

def listar_restaurantes() -> list[Restaurante]:
    with memoria.lock_usuarios:
        restaurantes = []
        for registro in memoria.restaurantes:
            restaurante = Restaurante(
                registro.id, registro.email, registro.password,
                registro.nome_restaurante, registro.commission,
            )
            restaurante.products = registro.products.copy()
            restaurantes.append(restaurante)
        return restaurantes

def registrar_pedido(cliente_id: int, restaurante_id: int, produto_id: int, quantidade: int) -> Pedido | None:
    with memoria.lock_usuarios:
        restaurante = next((item for item in memoria.restaurantes if item.id == restaurante_id), None)
        if restaurante is None:
            return None
        for produto in restaurante.products:
            if produto.id == produto_id:
                pedido = Pedido(
                    next(_ids_pedidos), cliente_id, restaurante_id, produto_id,
                    quantidade, datetime.now(timezone.utc),
                )
                _pedidos.append(pedido)
                return pedido
        return None

def listar_pedidos(usuario: Usuario) -> list[Pedido]:
    with memoria.lock_usuarios:
        if isinstance(usuario, Restaurante):
            return [pedido for pedido in _pedidos if pedido.restaurant_id == usuario.id]
        return [pedido for pedido in _pedidos if pedido.client_id == usuario.id]

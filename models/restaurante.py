import math
from fastapi import HTTPException
from models.usuarios import Usuario

class Restaurante(Usuario):
    def __init__(self, id: int, email: str, password: str, nome_restaurante: str, commission: float):
        super().__init__(id, email, password)
        self.nome_restaurante = nome_restaurante
        self.commission = commission
        self.products = []

    @staticmethod
    def validar_nome(nome_restaurante: str) -> None:
        if len(nome_restaurante) <= 5:
            raise HTTPException(
                status_code=400,
                detail="O nome do restaurante deve ter mais de 5 caracteres."
            )
    @staticmethod
    def validar_comissao(comissao: float) -> None:
        if not math.isfinite(comissao) or not 0 <= comissao <= 100:
            raise HTTPException(
                status_code=400,
                detail="A comissão deve estar entre 0 e 100."
            )

    @classmethod
    def validar_dados(cls, email: str, senha: str, nome_restaurante: str, comissao: float) -> None:
        cls.validar_dados_acesso(email, senha)
        cls.validar_nome(nome_restaurante)
        cls.validar_comissao(comissao)
    @classmethod
    def criar(cls, email: str, senha: str, nome: str, comissao: float) -> dict:
        from dados import repositorio
        email = email.lower()
        nome = nome.strip()
        cls.validar_dados(email, senha, nome, comissao)
        restaurante = repositorio.cadastrar_restaurante(email, senha, nome, comissao)
        if restaurante is None:
            raise HTTPException(status_code=400, detail="E-mail já está em uso.")
        return {
            "id": restaurante.id,
            "email": restaurante.email,
            "restaurant_name": restaurante.nome_restaurante,
            "commission": restaurante.commission,
        }

    @classmethod
    def obter_autenticado(cls, token: str | None) -> "Restaurante":
        usuario = Usuario.obter_autenticado(token)
        if not isinstance(usuario, cls):
            raise HTTPException(status_code=401, detail="Token inválido ou usuário não é restaurante.")
        return usuario

    @classmethod
    def adicionar_produto(cls, token: str | None, nome: str, preco: float) -> dict:
        from dados import repositorio
        from models.produto import Produto
        restaurante = cls.obter_autenticado(token)
        nome = nome.strip()
        Produto.validar_dados(nome, preco)
        produto = repositorio.adicionar_produto(restaurante.id, nome, preco)
        if produto is None:
            raise HTTPException(status_code=400, detail="Já existe um produto com esse nome neste restaurante.")
        return {"id": produto.id, "name": produto.name, "price": produto.price}

    @classmethod
    def remover_produto(cls, token: str | None, produto_id: int) -> dict:
        from dados import repositorio

        restaurante = cls.obter_autenticado(token)
        if not repositorio.remover_produto(restaurante.id, produto_id):
            raise HTTPException(status_code=404, detail="Produto não encontrado no menu deste restaurante.")
        return {"mensagem": "Produto removido.", "id": produto_id}

    @classmethod
    def atualizar_comissao(cls, token: str | None, comissao: float) -> dict:
        from dados import repositorio

        restaurante = cls.obter_autenticado(token)
        cls.validar_comissao(comissao)
        repositorio.atualizar_comissao(restaurante.id, comissao)
        return {"id": restaurante.id, "commission": comissao}
    @classmethod
    def listar(cls, token: str | None) -> list:
        from dados import repositorio

        Usuario.obter_autenticado(token)
        ordenados = sorted(repositorio.listar_restaurantes(), key=lambda restaurante: (-restaurante.commission, restaurante.nome_restaurante.lower()))
        return [
            {
                "id": restaurante.id,
                "restaurant_name": restaurante.nome_restaurante,
                "commission": restaurante.commission,
                "products": [
                    {"id": produto.id, "name": produto.name, "price": produto.price}
                    for produto in restaurante.products
                ],
            }
            for restaurante in ordenados
        ]


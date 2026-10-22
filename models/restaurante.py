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
        if not math.isfinite(comissao) or comissao < 0:
            raise HTTPException(
                status_code=400,
                detail="A comissão não pode ser negativa."
            )

    @classmethod
    def validar_dados(cls, email: str, senha: str, nome_restaurante: str, comissao: float) -> None:
        cls.validar_dados_acesso(email, senha)
        cls.validar_nome(nome_restaurante)
        cls.validar_comissao(comissao)
    @classmethod
    def criar(cls, email: str, senha: str, nome: str, comissao: float) -> dict:
        from dados import memoria
        email = email.strip().lower()
        nome = nome.strip()
        cls.validar_dados(email, senha, nome, comissao)
        if cls.email_em_uso(email):
            raise HTTPException(status_code=400, detail="E-mail já está em uso.")
        restaurante = cls(memoria.proximo_id_restaurante, email, senha, nome, comissao)
        memoria.restaurantes.append(restaurante)
        memoria.proximo_id_restaurante += 1
        return {
            "id": restaurante.id,
            "email": restaurante.email,
            "restaurant_name": restaurante.nome_restaurante,
            "commission": restaurante.commission,
        }

    @classmethod
    def obter_autenticado(cls, token: str | None):
        from dados import memoria
        for item in memoria.tokens:
            if item["token"] == token and isinstance(item["usuario"], cls):
                return item["usuario"]
        raise HTTPException(status_code=401, detail="Token inválido ou usuário não é restaurante.")

    @classmethod
    def adicionar_produto(cls, token: str | None, nome: str, preco: float) -> dict:
        from dados import memoria
        from models.produto import Produto
        restaurante = cls.obter_autenticado(token)
        nome = nome.strip()
        Produto.validar_dados(nome, preco)
        if any(produto.name.lower() == nome.lower() for produto in restaurante.products):
            raise HTTPException(status_code=400, detail="Já existe um produto com esse nome neste restaurante.")
        produto = Produto(memoria.proximo_id_produto, nome, preco)
        restaurante.products.append(produto)
        memoria.proximo_id_produto += 1
        return {"id": produto.id, "name": produto.name, "price": produto.price}

    @classmethod
    def remover_produto(cls, token: str | None, produto_id: int) -> dict:
        restaurante = cls.obter_autenticado(token)
        for produto in restaurante.products:
            if produto.id == produto_id:
                restaurante.products.remove(produto)
                return {"mensagem": "Produto removido.", "id": produto_id}
        raise HTTPException(status_code=404, detail="Produto não encontrado no menu deste restaurante.")

    @classmethod
    def atualizar_comissao(cls, token: str | None, comissao: float) -> dict:
        restaurante = cls.obter_autenticado(token)
        cls.validar_comissao(comissao)
        restaurante.commission = comissao
        return {"id": restaurante.id, "commission": restaurante.commission}
    @classmethod
    def listar(cls, token: str | None) -> list:
        from dados import memoria
        if not any(item["token"] == token for item in memoria.tokens):
            raise HTTPException(status_code=401, detail="Token inválido.")
        ordenados = sorted(memoria.restaurantes, key=lambda restaurante: (-restaurante.commission, restaurante.nome_restaurante.lower()))
        return [
            {
                "id": restaurante.id,
                "email": restaurante.email,
                "restaurant_name": restaurante.nome_restaurante,
                "commission": restaurante.commission,
                "products": [
                    {"id": produto.id, "name": produto.name, "price": produto.price}
                    for produto in restaurante.products
                ],
            }
            for restaurante in ordenados
        ]


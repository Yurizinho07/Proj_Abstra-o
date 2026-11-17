from models.cliente import Cliente
from models.restaurante import Restaurante


class UsuarioFactory:
    """Centraliza a construção dos tipos de usuário (Simple Factory)."""

    @staticmethod
    def criar_cliente(id: int, email: str, senha: str, nome: str) -> Cliente:
        return Cliente(id, email, senha, nome)

    @staticmethod
    def criar_restaurante(
        id: int, email: str, senha: str, nome: str, comissao: float,
    ) -> Restaurante:
        return Restaurante(id, email, senha, nome, comissao)

    @staticmethod
    def criar(
        tipo: str, id: int, email: str, senha: str, nome: str,
        comissao: float | None = None,
    ) -> Cliente | Restaurante:
        if tipo == "cliente":
            return UsuarioFactory.criar_cliente(id, email, senha, nome)
        if tipo == "restaurante" and comissao is not None:
            return UsuarioFactory.criar_restaurante(id, email, senha, nome, comissao)
        raise ValueError("Tipo de usuário inválido ou comissão não informada.")

from fastapi import HTTPException
from models.usuarios import Usuario

class Cliente(Usuario):
    def __init__(self, id: int, email: str, password: str, name: str) -> None:
        super().__init__(id, email, password)
        self.name = name

    @staticmethod
    def validar_nome(name: str) -> None:
        if len(name) <= 5:
            raise HTTPException(status_code=400, detail="O nome do cliente deve ter mais de 5 caracteres.")

    @classmethod
    def validar_dados(cls, email: str, senha: str, name: str) -> None:
        cls.validar_dados_acesso(email, senha)
        cls.validar_nome(name)

    @classmethod
    def criar(cls, email: str, senha: str, nome: str) -> dict[str, int | str]:
        from dados import repositorio
        email = email.lower()
        nome = nome.strip()
        cls.validar_dados(email, senha, nome)
        cliente = repositorio.cadastrar_cliente(email, senha, nome)
        if cliente is None:
            raise HTTPException(status_code=400, detail="E-mail já está em uso.")
        return {"id": cliente.id, "email": cliente.email, "name": cliente.name}

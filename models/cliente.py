from fastapi import HTTPException
from models.usuarios import Usuario

class Cliente(Usuario):
    def __init__(self, id: int, email: str, password: str, name: str):
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
    def criar(cls, email: str, senha: str, nome: str) -> dict:
        from dados import memoria
        email = email.strip().lower()
        nome = nome.strip()
        cls.validar_dados(email, senha, nome)
        if cls.email_em_uso(email):
            raise HTTPException(status_code=400, detail="E-mail já está em uso.")
        cliente = cls(memoria.proximo_id_cliente, email, senha, nome)
        memoria.clientes.append(cliente)
        memoria.proximo_id_cliente += 1
        return {"id": cliente.id, "email": cliente.email, "name": cliente.name}

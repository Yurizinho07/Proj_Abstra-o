import hashlib
import secrets
import sqlite3
from contextlib import closing, contextmanager
from datetime import datetime, timezone
from functools import cache
from pathlib import Path
from typing import Iterator
from models.cliente import Cliente
from models.pedido import Pedido
from models.produto import Produto
from models.restaurante import Restaurante
from models.usuarios import Usuario

ARQUIVO_BANCO = Path(__file__).resolve().parent / "catalogo.db"

@cache
def inicializar_banco(arquivo: Path) -> None:
    with closing(sqlite3.connect(arquivo)) as banco:
        banco.executescript("""
            CREATE TABLE IF NOT EXISTS ids (
                id INTEGER PRIMARY KEY AUTOINCREMENT
            );

            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY,
                email TEXT NOT NULL UNIQUE,
                senha TEXT NOT NULL,
                nome TEXT NOT NULL,
                tipo TEXT NOT NULL CHECK (tipo IN ('cliente', 'restaurante')),
                comissao REAL CHECK (comissao BETWEEN 0 AND 100)
            );

            CREATE TABLE IF NOT EXISTS tokens (
                id INTEGER PRIMARY KEY,
                usuario_id INTEGER NOT NULL UNIQUE REFERENCES usuarios(id),
                valor TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY,
                restaurante_id INTEGER NOT NULL REFERENCES usuarios(id),
                nome TEXT NOT NULL,
                preco REAL NOT NULL CHECK (preco > 0),
                ativo INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0, 1))
            );

            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY,
                cliente_id INTEGER NOT NULL REFERENCES usuarios(id),
                produto_id INTEGER NOT NULL REFERENCES produtos(id),
                quantidade INTEGER NOT NULL CHECK (quantidade > 0),
                criado_em TEXT NOT NULL
            );
        """)


@contextmanager
def conectar(escrita: bool = False) -> Iterator[sqlite3.Connection]:
    inicializar_banco(ARQUIVO_BANCO)
    with closing(sqlite3.connect(ARQUIVO_BANCO)) as banco, banco:
        banco.row_factory = sqlite3.Row
        banco.execute("PRAGMA foreign_keys = ON")
        banco.execute("BEGIN IMMEDIATE" if escrita else "BEGIN")
        yield banco


def proximo_id(banco: sqlite3.Connection) -> int:
    return banco.execute("INSERT INTO ids DEFAULT VALUES").lastrowid


def hash_senha(senha: str, sal: bytes) -> str:
    return hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), sal, 600_000).hex()


def montar_usuario(registro: sqlite3.Row) -> Cliente | Restaurante:
    if registro["tipo"] == "cliente":
        return Cliente(registro["id"], registro["email"], registro["senha"], registro["nome"])
    return Restaurante(
        registro["id"], registro["email"], registro["senha"],
        registro["nome"], registro["comissao"],
    )

def cadastrar_usuario(
    email: str, senha: str, nome: str, tipo: str, comissao: float | None = None,
) -> sqlite3.Row | None:
    sal = secrets.token_bytes(16)
    senha_guardada = f"{sal.hex()}:{hash_senha(senha, sal)}"
    with conectar(escrita=True) as banco:
        if banco.execute("SELECT id FROM usuarios WHERE email = ?", (email,)).fetchone():
            return None
        usuario_id = proximo_id(banco)
        return banco.execute(
            """INSERT INTO usuarios (id, email, senha, nome, tipo, comissao)
               VALUES (?, ?, ?, ?, ?, ?) RETURNING *""",
            (usuario_id, email, senha_guardada, nome, tipo, comissao),
        ).fetchone()

def cadastrar_cliente(email: str, senha: str, nome: str) -> Cliente | None:
    registro = cadastrar_usuario(email, senha, nome, "cliente")
    if registro is None:
        return None
    return Cliente(registro["id"], email, registro["senha"], nome)

def cadastrar_restaurante(email: str, senha: str, nome: str, comissao: float) -> Restaurante | None:
    registro = cadastrar_usuario(email, senha, nome, "restaurante", comissao)
    if registro is None:
        return None
    return Restaurante(registro["id"], email, registro["senha"], nome, comissao)

def buscar_usuario(email: str, senha: str) -> Usuario | None:
    with conectar() as banco:
        registro = banco.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
    if registro is None:
        return None
    sal, senha_guardada = registro["senha"].split(":")
    if not secrets.compare_digest(hash_senha(senha, bytes.fromhex(sal)), senha_guardada):
        return None
    return montar_usuario(registro)

def substituir_token(usuario_id: int, token: str) -> None:
    with conectar(escrita=True) as banco:
        banco.execute("DELETE FROM tokens WHERE usuario_id = ?", (usuario_id,))
        banco.execute(
            "INSERT INTO tokens (id, usuario_id, valor) VALUES (?, ?, ?)",
            (proximo_id(banco), usuario_id, token),
        )

def buscar_usuario_por_token(token: str) -> Usuario | None:
    with conectar() as banco:
        registro = banco.execute(
            """SELECT usuarios.* FROM usuarios
               JOIN tokens ON tokens.usuario_id = usuarios.id
               WHERE tokens.valor = ?""",
            (token,),
        ).fetchone()
    return montar_usuario(registro) if registro else None

def adicionar_produto(restaurante_id: int, nome: str, preco: float) -> Produto | None:
    with conectar(escrita=True) as banco:
        produtos = banco.execute(
            "SELECT nome FROM produtos WHERE restaurante_id = ? AND ativo = 1",
            (restaurante_id,),
        )
        if any(produto["nome"].lower() == nome.lower() for produto in produtos):
            return None
        produto_id = proximo_id(banco)
        banco.execute(
            "INSERT INTO produtos (id, restaurante_id, nome, preco) VALUES (?, ?, ?, ?)",
            (produto_id, restaurante_id, nome, preco),
        )
        return Produto(produto_id, nome, preco)

def remover_produto(restaurante_id: int, produto_id: int) -> bool:
    with conectar(escrita=True) as banco:
        resultado = banco.execute(
            "UPDATE produtos SET ativo = 0 WHERE restaurante_id = ? AND id = ? AND ativo = 1",
            (restaurante_id, str(produto_id)),
        )
        return resultado.rowcount == 1

def atualizar_comissao(restaurante_id: int, comissao: float) -> None:
    with conectar(escrita=True) as banco:
        banco.execute("UPDATE usuarios SET comissao = ? WHERE id = ?", (comissao, restaurante_id))

def listar_restaurantes() -> list[Restaurante]:
    with conectar() as banco:
        restaurantes = {}
        for registro in banco.execute("SELECT * FROM usuarios WHERE tipo = 'restaurante'"):
            restaurante = Restaurante(
                registro["id"], registro["email"], registro["senha"],
                registro["nome"], registro["comissao"],
            )
            restaurantes[restaurante.id] = restaurante
        for registro in banco.execute("SELECT * FROM produtos WHERE ativo = 1 ORDER BY id"):
            produto = Produto(registro["id"], registro["nome"], registro["preco"])
            restaurantes[registro["restaurante_id"]].products.append(produto)
        return list(restaurantes.values())

def registrar_pedido(cliente_id: int, restaurante_id: int, produto_id: int, quantidade: int) -> Pedido | None:
    with conectar(escrita=True) as banco:
        produto = banco.execute(
            "SELECT id FROM produtos WHERE restaurante_id = ? AND id = ? AND ativo = 1",
            (str(restaurante_id), str(produto_id)),
        ).fetchone()
        if produto is None:
            return None
        pedido_id = proximo_id(banco)
        criado_em = datetime.now(timezone.utc)
        banco.execute(
            """INSERT INTO pedidos (id, cliente_id, produto_id, quantidade, criado_em)
               VALUES (?, ?, ?, ?, ?)""",
            (pedido_id, cliente_id, produto_id, quantidade, criado_em.isoformat()),
        )
        return Pedido(pedido_id, cliente_id, restaurante_id, produto_id, quantidade, criado_em)

def listar_pedidos(usuario: Usuario) -> list[Pedido]:
    consulta = """SELECT pedidos.*, produtos.restaurante_id
                  FROM pedidos JOIN produtos ON produtos.id = pedidos.produto_id"""
    if isinstance(usuario, Restaurante):
        consulta += " WHERE produtos.restaurante_id = ?"
    else:
        consulta += " WHERE pedidos.cliente_id = ?"
    with conectar() as banco:
        registros = banco.execute(consulta, (usuario.id,)).fetchall()
    return [
        Pedido(
            registro["id"], registro["cliente_id"], registro["restaurante_id"],
            registro["produto_id"], registro["quantidade"], 
            datetime.fromisoformat(registro["criado_em"]),
        )
        for registro in registros
    ]

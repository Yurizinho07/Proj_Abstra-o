from threading import Lock

restaurantes = []
clientes = []
tokens = []

lock_usuarios = Lock()
proximo_id_usuario = 1
proximo_id_produto = 1
proximo_id_token = 1

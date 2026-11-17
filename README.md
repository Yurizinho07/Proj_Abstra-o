Executar

Requer Python 3.12 ou superior.

Abre o PowerShell na pasta do projeto e roda os dois comandos abaixo.

```powershell
uv sync
uv run python -m uvicorn main:app --reload
```

A API roda em http://127.0.0.1:8000. Pra testar pelo navegador, abre o Swagger em http://127.0.0.1:8000/docs.

O uv gerencia o ambiente e as dependências definidos no `pyproject.toml` e no `uv.lock`. Para iniciar novamente, use o segundo comando. O Uvicorn executa o servidor FastAPI.

O SQLite já vem com o Python. Quando alguma rota usar o banco pela primeira vez, o projeto cria o arquivo `dados/catalogo.db` e as tabelas. Os dados ficam salvos mesmo se fechar e abrir o servidor de novo. Na hora de montar o ZIP da entrega, deixa de fora o arquivo `.db` e as pastas `.env` e `.venv`.

Rotas

| Método | Rota | Uso |
|---|---|---|
| POST | `/restaurants` | Cadastra restaurante |
| POST | `/clients` | Cadastra cliente |
| POST | `/login` | Gera token de acesso |
| POST | `/restaurants/products` | Adiciona produto do restaurante autenticado |
| DELETE | `/restaurants/products/{id}` | Remove produto do restaurante autenticado |
| PATCH | `/restaurants/` | Atualiza comissão do restaurante autenticado |
| GET | `/restaurants` | Lista restaurantes e produtos |
| GET | `/docs` | Abre o Swagger |
| POST | `/restaurants/{ID_RES}/{ID_PROD}/` | Registra uma compra para o cliente autenticado |
| GET | `/orders/` | Lista compras do cliente ou vendas do restaurante, mais recentes primeiro |

Como testar uma compra

1. Cadastra um restaurante e faz login com o e-mail e a senha dele. O token aparece no JSON e no header `X-Auth-Token` da resposta. Se fizer login de novo, pega o token novo, porque o anterior para de funcionar.
2. Adiciona um produto em `POST /restaurants/products` com um JSON tipo `{"name": "X-Bacon", "price": 25}`. No header `auth_token`, coloca o token do restaurante. Guarda os IDs que a API devolveu no cadastro do restaurante e do produto.
3. Cadastra um cliente com outro e-mail e faz login com essa conta. Se o ID do restaurante for `1` e o do produto for `3`, chama `POST /restaurants/1/3/` com `{"quantity": 2}` e o token do cliente no header `auth_token`. Troca esses IDs pelos teus. A grafia `restaurants` é a mesma do enunciado.
4. A resposta mostra o ID do pedido, os IDs do cliente, do restaurante e do produto, a quantidade e a data e hora em UTC. Em `GET /orders/`, o token do cliente mostra as compras dele e o token do restaurante mostra as vendas dele. Os pedidos mais recentes aparecem primeiro.

Regras do cadastro e do cardápio

O e-mail fica em minúsculas e só pode ser usado em uma conta. A senha precisa ter pelo menos cinco caracteres, com uma minúscula, uma maiúscula e um número. Nomes de cliente e restaurante precisam ter mais de cinco caracteres. Nome de produto precisa ter mais de quatro.Na lista, quem tem a maior comissão aparece primeiro. Se empatar, vai por ordem alfabética.

Como o código tá separado

`routes` recebe os dados da requisição. `models` tem as classes e as regras de cadastro, login, cardápio e pedido. `dados/sqlite.py` é onde ficam as consultas e as gravações no banco. Quando um produto sai do cardápio, as compras antigas dele continuam aparecendo no histórico.

Padrão Factory

`models/usuario_factory.py` implementa uma Simple Factory: a classe `UsuarioFactory` centraliza a construção de `Cliente` e `Restaurante`. O método `criar` escolhe a classe pelo tipo de usuário; `criar_cliente` e `criar_restaurante` atendem aos casos em que o tipo já é conhecido.

Os repositórios SQLite e em memória usam a fábrica no cadastro e na reconstrução dos usuários. As validações continuam nos modelos, e o banco continua responsável por IDs e persistência. A fábrica não modifica rotas, respostas, autenticação ou regras de negócio.

Padrão Facade

`facades/pedido_facade.py` implementa a classe `PedidoFacade`. As rotas de compra e histórico chamam essa fachada, que coordena autenticação, autorização, validação da quantidade e acesso ao repositório. O histórico continua em ordem do mais recente para o mais antigo.

Fluxo da compra: rota → `PedidoFacade.realizar_compra` → autenticação e validações → repositório → `Pedido`.

`Pedido` representa os dados da compra. Seus métodos `criar` e `listar` foram mantidos como delegações para a fachada, preservando chamadas existentes. As rotas, os headers, os campos das respostas e os códigos de erro permanecem os mesmos.

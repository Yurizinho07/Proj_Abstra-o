Executar

Requer Python 3.12 ou superior.

powershell
uv sync
uv run uvicorn main:app --reload

A API fica em http://127.0.0.1:8000 A documentação interativa fica em http://127.0.0.1:8000/docs

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

Nas rotas protegidas, envie o token no header auth_token. O login retorna o token no corpo da resposta. Para testar, cadastre um restaurante, faça login com o e-mail e senha e use o token nas rotas protegidas.
Os e-mails são armazenados em letras minúsculas e não podem se repetir entre clientes e restaurantes. Senhas precisam ter no mínimo cinco caracteres, uma letra minúscula, uma maiúscula e um número. Nomes de restaurante precisam ter mais de cinco caracteres/ nomes de produto, mais de quatro/ nomes de cliente, mais de cinco. A comissão pode ser zero ou maior. O produto precisa ter preço maior que zero. Na listagem, comissões maiores aparecem primeiro e os nomes desempatarão em ordem alfabética.
Usuario guarda os dados e as validações compartilhadas de ID, e-mail e senha, além da autenticação. Restaurante e Cliente herdam de Usuario e adicionam seus próprios dados, validações e operações. Produto guarda as validações de produto. As rotas só recebem os dados e chamam os métodos das classes; a lógica de cadastro e das operações fica nos modelos.



Modelo logico: Print na pasta

Modelo ER: Print na pasta
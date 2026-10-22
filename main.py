from fastapi import FastAPI
from routes.login import router as login_router
from routes.restaurantes import router as restaurantes_router
from routes.clientes import router as clientes_router

app = FastAPI(title="Catálogo de Restaurantes")

app.include_router(login_router)
app.include_router(restaurantes_router)
app.include_router(clientes_router)


@app.get("/")
def inicio():
    return {"mensagem": "API funcionando", "documentacao": "/docs", "como_disse_minha_ex": "cabou tudo"}

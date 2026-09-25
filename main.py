from fastapi import FastAPI
from routes.restaurantes import router as restaurantes_router

app = FastAPI()

app.include_router(restaurantes_router)


@app.get("/")
def inicio():
    return {"mensagem": "API funcionando"}
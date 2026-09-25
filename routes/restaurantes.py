from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dados.memoria import restaurantes, proximo_id_restaurante
from models.restaurante import Restaurante
from models.usuarios import Usuario

router = APIRouter()

class RestauranteRequest(BaseModel):
    email: str
    password: str
    restaurant_name: str
    commission: float

@router.post("/restaurants")
def criar_restaurante(dados: RestauranteRequest):
    global proximo_id_restaurante

    nome = dados.restaurant_name
    email = dados.email.lower()
    senha = dados.password
    comissao = dados.commission

    Usuario.validar_email(email)
    Usuario.validar_senha(senha)
    Restaurante.validar_nome(nome)
    Restaurante.validar_comissao(comissao)

    for restaurante in restaurantes:
        if restaurante.email == email:
            raise HTTPException(
                status_code=400,
                detail="E-mail já está em uso."
            )

    restaurante = Restaurante(
        proximo_id_restaurante,
        email,
        senha,
        nome,
        comissao
    )

    restaurantes.append(restaurante)
    proximo_id_restaurante += 1

    return {
        "id": restaurante.id,
        "email": restaurante.email,
        "restaurant_name": restaurante.nome_restaurante,
        "commission": restaurante.commission
    }
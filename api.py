from fastapi import FastAPI
from pydantic import BaseModel
import pymysql

app = FastAPI()


class Pedido(BaseModel):
    produto: str
    preco: float
    forma_pagamento: str


def conectar():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="lanchonete"
    )


@app.get("/")
def home():
    return {"mensagem": "API funcionando"}


@app.post("/pedido")
def criar_pedido(pedido: Pedido):

    conn = conectar()
    cursor = conn.cursor()

    sql = """
    INSERT INTO pedidos (produto, preco, forma_pagamento)
    VALUES (%s, %s, %s)
    """

    cursor.execute(
        sql,
        (pedido.produto, pedido.preco, pedido.forma_pagamento)
    )

    conn.commit()
    conn.close()

    return {"mensagem": "Pedido salvo"}
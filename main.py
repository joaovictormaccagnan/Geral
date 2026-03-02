from fastapi import FastAPI

app = FastAPI()

# Lista que funciona como "banco de dados"
produtos = []

@app.get("/")
def inicio():
    return {"mensagem": "API esta rodando 🚀🚀"}

@app.post("/produtos")
def criar_produto(nome: str, preco: float):
    produto = {
        "id": len(produtos) + 1,
        "nome": nome,
        "preco": preco
    }
    produtos.append(produto)
    return produto

@app.get("/produtos")
def listar_produtos():
    return produtos

@app.delete("/produtos/{produto_id}")
def deletar_produto(produto_id: int):
    for produto in produtos:
        if produto["id"] == produto_id:
            produtos.remove(produto)
            return {"mensagem": "Produto removido"}
    return {"erro": "Produto não encontrado"}

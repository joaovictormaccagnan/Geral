import requests


class Lanchonete:

    def __init__(self):

        self.cardapio = {
            '1': {'nome': 'Salgados', 'preco': 6},
            '2': {'nome': 'Pão de queijo', 'preco': 5},
            '3': {'nome': 'Batata chips', 'preco': 3},
            '4': {'nome': 'Paçoca grande', 'preco': 3},
            '5': {'nome': 'Paçoca pequena', 'preco': 2},
            '6': {'nome': 'Gomet', 'preco': 3},
            '7': {'nome': 'Moranguete', 'preco': 2},
            '8': {'nome': 'Suco (Garrafa)', 'preco': 3},
            '9': {'nome': 'Suco (Copo)', 'preco': 1},
            '10': {'nome': 'Chips', 'preco': 3},
            '11': {'nome': 'Pipoca doce', 'preco': 4},
        }

        self.pedido = []
        self.total = 0


    def enviar_para_api(self, produto, pagamento):

        url = "http://127.0.0.1:8000/pedido"

        dados = {
            "produto": produto["nome"],
            "preco": produto["preco"],
            "forma_pagamento": pagamento
        }

        requests.post(url, json=dados)


    def mostrar_cardapio(self):

        print("\n🍔 CARDÁPIO")

        for codigo, produto in self.cardapio.items():

            print(
                f"{codigo} - {produto['nome']}  R$ {produto['preco']}"
            )

        print("0 - Finalizar")


    def executar(self):

        print("🍔 MASONIZ")

        while True:

            self.mostrar_cardapio()

            opcao = input("Escolha o produto: ")

            if opcao == '0':
                break

            if opcao in self.cardapio:

                produto = self.cardapio[opcao]

                self.pedido.append(produto)

                self.total += produto["preco"]

                print(f"Adicionado: {produto['nome']}")

            else:
                print("Código inválido")

        print(f"\nTotal: R$ {self.total:.2f}")

        print("\nForma de pagamento")
        print("1 - Dinheiro")
        print("2 - Cartão")
        print("3 - Pix")

        opcao_pagamento = input("Escolha: ")

        if opcao_pagamento == "1":
            pagamento = "Dinheiro"
        elif opcao_pagamento == "2":
            pagamento = "Cartão"
        elif opcao_pagamento == "3":
            pagamento = "Pix"
        else:
            pagamento = "Desconhecido"

        for produto in self.pedido:
            self.enviar_para_api(produto, pagamento)

        print("✅ Pedido enviado para o sistema!")


if __name__ == "__main__":

    sistema = Lanchonete()
    sistema.executar()
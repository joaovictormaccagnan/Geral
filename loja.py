import requests


class Lanchonete:

    def __init__(self):

        self.cardapio = {
            '1': {'nome': 'Croissant', 'preco': 8},
            '2': {'nome': 'Pain au chocolat', 'preco': 9},
            '3': {'nome': 'Baguette com queijo e presunto', 'preco': 10},
            '4': {'nome': 'Quiche', 'preco': 12},
            '5': {'nome': 'Crêpe (doce ou salgado)', 'preco': 11},
            '6': {'nome': 'Café expresso', 'preco': 5},
            '7': {'nome': 'Café com leite', 'preco': 6},
            '8': {'nome': 'Cappuccino', 'preco': 8},
            '9': {'nome': 'Chocolate quente', 'preco': 7},
            '10': {'nome': 'Chá', 'preco': 4},
            '11': {'nome': 'Suco natural', 'preco': 7},
            '12': {'nome': 'Milkshake', 'preco': 10},
            '13': {'nome': 'Café gelado', 'preco': 9},
            '14': {'nome': 'Macaron', 'preco': 6},
            '15': {'nome': 'Madeleine', 'preco': 7},
            '16': {'nome': 'Èclair', 'preco': 9},
            '17': {'nome': 'Brownie', 'preco': 7},
            '18': {'nome': 'Cookie', 'preco': 5},
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

        print("\n☕ CARDÁPIO")

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
        print("Obrigado por comprar na MASONIZ!")


if __name__ == "__main__":

    sistema = Lanchonete()
    sistema.executar()
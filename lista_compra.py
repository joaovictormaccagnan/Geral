import os

lista = []


while True:
    opcao = input("[i]inserir [a]apagar [l]lista\n")
    if opcao == "i":
        valor = input("Valor: ")
        lista.append(valor)
        continue
    elif opcao == "a":
        if len(lista) == 0:
            print("Lista vazia")
        else:
            deletar = input("Digite o indice que deseja apagar: ")
            try:
                deletar = int(deletar)
                del lista[deletar]
            except:
                print("Digite um indice valido")
    elif opcao == "l":
        os.system("cls")
        if len(lista) == 0:
            print("Lista vazia")
        else:
            for indice, nome in enumerate(lista):
                print(indice, nome)
            
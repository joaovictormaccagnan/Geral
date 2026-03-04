def funcao(multiplicador):
    def multiplicar(numero):
        return numero * multiplicador
    return multiplicar
        

duplicar = funcao(2)
triplicar = funcao(3)
quadruplicar = funcao(4)
print(duplicar(2))
print(triplicar(3))
print(quadruplicar(4))
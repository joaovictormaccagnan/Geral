def funcao(multiplicador):
    def multiplicar(numero):
        return numero * multiplicador
    return multiplicar
        
duplicar = funcao(2)
triplicar = funcao(3)
quadruplicar = funcao(4)
print(duplicar(4))
print(triplicar(6))
print(quadruplicar(8))
"""
def funcao(2):"
    def multiplicar(4):
        return numero * multiplicar
    return multiplicar
"""
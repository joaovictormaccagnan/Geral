import random

nove_digitos = ""
for p in range(9):
    nove_digitos += str(random.randint(0, 9))



print("Alteração feita por: João V.")
indice = 10
adicao = 0
digito_1 = 0
for d in nove_digitos:
    adicao += int(d) * indice
    indice -= 1
digito_1 += (adicao * 10) % 11
digito_1 = digito_1 if digito_1 <= 9 else 0


indice = 11
digito_2 = 0
adicao_2 = 0
dez_digito = 0
dez_digito = nove_digitos + str(digito_1)

for n in dez_digito:
    adicao_2 += int(n) * indice
    indice -= 1
digito_2 += (adicao_2 * 10) % 11
digito_2 = digito_2 if digito_2 <= 9 else 0

cpf_gerado = nove_digitos + str(digito_1) + str(digito_2)
print(f"CPF Gerado: {cpf_gerado}") 
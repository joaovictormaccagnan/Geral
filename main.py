"""
Peça ao usuário um número inteiro positivo.
Gere todos os números de 1 até esse número.

Para cada número:
Se for múltiplo de 3, mostre Fizz
Se for múltiplo de 5, mostre Buzz
Se for múltiplo de 3 e 5, mostre FizzBuzz
Caso contrário, mostre o próprio número
Mostre tudo em ordem, um por linha.

Regras:
Use for e range.
Não use funções prontas de verificação de múltiplo além do operador %.
"""
numero = input("Digite um número: ")
fizz = 0
buzz = 0
fizzbuzz = 0
try:
    num_int = int(numero) 
    if num_int <= 0:
        exit()
except:
    print("Não é um número inteiro positivo")
    exit()
    
for i in range(1,num_int + 1):
    
    if i % 3 == 0 and i % 5 == 0:
        print("FizzBuzz")
        fizzbuzz += 1
    elif i % 3 == 0:
        print("Fizz")
        fizz += 1
    elif i % 5 == 0:
        print("Buzz")
        buzz += 1
    else:
        print(i)
    
print(f"fizz = {fizz}, buzz = {buzz}, fizzbuzz = {fizzbuzz}")
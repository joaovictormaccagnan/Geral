
numero = input("Digite um número: ")
fizz = 0
buzz = 0
fizzbuzz = 0
try:
    num_int = int(numero) 
    if num_int <= 0:
        raise ValueError
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
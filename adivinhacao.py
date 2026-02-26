import os
palavra_secreta = "perfume"
letra_correta = ''
letra_errada = ''
tentativas = 0
while True:
    letra_digitada = input("Digita uma letra: ").lower()
    tentativas += 1
    if len(letra_digitada) > 1:
        print("Digite apenas uma letra")
    
    elif letra_digitada in palavra_secreta:
        print("Você acertou uma letra")
        letra_correta += letra_digitada  
    elif letra_digitada in letra_errada:
        print("Você ja digitou essa letra")
    else:
        print("Nova letra")  
        letra_errada += letra_digitada
        continue
    nova_formula = ''
    for p in palavra_secreta:
        if p in letra_correta:
            nova_formula += p
        else:
            nova_formula += "*"
    print(nova_formula)
    if nova_formula == palavra_secreta:
        os.system("cls")
        print("PARABENS")
        print(f"Tentativas: {tentativas}x")
        print(f"Palavra secreta: {palavra_secreta}")
        break
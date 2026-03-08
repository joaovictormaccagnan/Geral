# adicionar o usuário no dicionário
# usar o nome como chave
# usar a idade como valor



def cadastrar_usuario(usuarios, nome, idade):
    if nome in usuarios:
        print("Usuário ja cadastrado")
    else:
        usuarios[nome] = idade
        with open("usuarios.txt", "a") as arquivo:
            arquivo.write(f"{nome}, {idade}\n")
    

def listar_usuarios(usuarios):
    for nome, idade in usuarios.items():
        print(f"{nome} - {idade}")



# verificar se o usuário existe no dicionário
# se existir → remover
# se não existir → mostrar "Usuário não encontrado"
def remover_usuario(usuarios, nome):
    if nome in usuarios:
        del usuarios[nome]
    else:
        print("Usuário não encontrado")
def editar_idade(usuarios, nome, nova_idade):
    if nome in usuarios:
        usuarios[nome] = nova_idade
    else:
        print("Usuário não encontrado")
usuarios = {}

while True:
    opcao = input("1-Cadastrar 2-Listar 3-Remover 4-Alterar idade 5-Sair: ")
    if opcao == "1":
        nome = input("Nome: ")
        
        try:
            idade = int(input("Idade: "))
        except:
            print("Digite apenas números na idade")
            continue
        cadastrar_usuario(usuarios, nome, idade)
    elif opcao == "2":
        listar_usuarios(usuarios)
    elif opcao == "3":
        nome = input("Digite o nome de usário que você deseja excluir: ")
        remover_usuario(usuarios, nome)
    elif opcao == "4":
        nome = input("Digite o nome de quem você quer alterar a idade: ")
        nova_idade = int(input("Digite a idade para alterar: "))
        editar_idade(usuarios, nome, nova_idade)
    elif opcao == "5":
        break

    else:
        print("Opção inválida")

    

    continuar = input("Continuar? (s/n)").lower()

    if continuar == "n":
        continue

print("Usuários cadastrados:")
listar_usuarios(usuarios)
print("Usuários cadastrados: ", len(usuarios))

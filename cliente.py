import socket
import threading

ip = "localhost"
porta = 40000

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

cliente.connect((ip, porta))

#salvo o email para usar depois 
email = None

#função para enviar os dados para o servidor 
#mais especificamente os dados do login
def login():
    #a variável email é global pois uso ela em vários locais
    global email
    #recebendo os dados
    email = input("Digite seu email: ")
    senha = input("Digite sua senha: ")
    #aqui eu crio uma string com os dados por ser mais 
    #fácil e compacto de enviar e manipular também
    dado = "login=" + email + "=" + senha
    #passar as informações para o servidor
    #envia a string codificada 
    cliente.send(dado.encode('utf-8'))
    #recebe do servidor uma confirmação se o email e a senha existem
    #serve para saber se o email ou a senha estão errados também
    retorno = cliente.recv(1024).decode('utf-8')
    #retorna a confirmação
    return retorno

#função para criar conta 
def criar_conta():
    #novamente guardo o email para usar depois
    global email 
    #recebendo os dados
    email = input("Digite um novo email: ")
    senha = input("Digite sua nova senha: ")
    #novamente monto uma string para enviar
    dado = "criarconta=" + email + "=" + senha
    #passar as informações para o servidor
    cliente.send(dado.encode('utf-8'))
    #servidor retorna a confirmação
    #se o email que o usuário quer utilizar já existir
    #ele retorna um aviso, informando que não foi possível criar a conta
    retorno = cliente.recv(1024).decode('utf-8')
    #retorna a confirmação
    return retorno

# mostrar as mensagens na tela
def mostra(mensagens):
    emails = mensagens.split(";")
    emails = list(emails)
    for email in range(len(emails)-1):
        dado = emails[email].split("&")
        dado = list(dado)
        if dado[0] == "nenhum":
            print('Nenhum email a ser mostrado.')
        else:
            print("-----",email,"-----")
            print("E-mail: ", dado[0])
            print("Assunto:", dado[1])
            print("Mensagem:", dado[2])

#função para enviar mensagem
def enviar_mensagem():
    #primeiramente recebe os dados
    destino = input("Digite o email do destinatario: ")
    titulo = input("Informe o titulo da mensagem: ")
    mensagem = input("Mensagem: ")
    #aqui eu monto a string para enviar para o servidor
    dado = "enviar=" + destino + "=" + titulo + "=" + mensagem + "=" + email 
    #envio a string para o servidor
    cliente.send(dado.encode('utf-8'))
    #novamente retorna uma mensagem de confirmação
    #caso o email esteja errado ele não envia a mensagem
    #apenas retorna a palavra enviado, mas só pra saber que funcionou
    retorno = cliente.recv(1024).decode('utf-8')
    #retorna a confirmação
    return retorno

#Essa função slicita ao servidor que o mesmo retorne as mensagens 
# que o usuário já recebeu
def consultar_mensagens_recebidas():
    #monta uma string para enviar como solicitação
    dado = "ler=recebidas=" + email
    #envia a string
    cliente.send(dado.encode('utf-8'))
    #retorna uma outra string com os emails
    #eu estipulei o tamanho só pra teste mesmo
    retorno = cliente.recv(2048).decode()
    #aí aqui chama a função pra mostrar
    mostra(retorno)

# Essa é igual a de cima
def consultar_mensagens_enviadas():

    dado = "ler=enviadas=" + email
    cliente.send(dado.encode('utf-8'))
    retorno = cliente.recv(2048).decode()
    mostra(retorno)

# função para excluir mensagem
def excluir_mensagem():
    print("\n\nDeseja excluir:\n  1 - Enviada\n  2 - Recebida\n")
    selecao = int(input())

    if selecao == 1:
        consultar_mensagens_enviadas()
        print("Digite o numero da mensagem a ser excluida:")
        indice = input()
        dado = "excluir=enviadas=" + indice + "=" + email
        cliente.send(dado.encode('utf-8'))
        retorno = cliente.recv(2048).decode()
        print(retorno)

    elif selecao == 2:
        consultar_mensagens_recebidas()
        print("Digite o numero da mensagem a ser excluida:")
        indice = input()
        dado = "excluir=recebidas=" + indice + "=" + email
        cliente.send(dado.encode('utf-8'))
        retorno = cliente.recv(2048).decode()
        print(retorno)

    else: 
        print("-----opcao invalida-----")


# serve para encerrar a conexão quando o usuário clica para sair lá embaixo
def desconectar():
    cliente.send("desconectar=".encode('utf-8'))

# Essa função é para o login, quando o usuário inicia o programa
def verificacao():
    #escolha do usuário
    # loop para as opções diponíveis (Logar, criar conta, sair)
    while True:
        #mostra as opções
        print("\n\n1 - Fazer login\n2 - Criar conta\n3 - Sair\n\n")
        #recebe do usuário a opção
        escolha = int(input())
        # nessa condição ele escolheu fazer o login
        if escolha == 1: #login
            #aí se retornar TRUE é porque deu certo
            #os dados estavam corretos e coincidiram
            #com os que estavam no servidor, caso contrário
            #ele mostra o que estava errado, senha ou email
            resposta = login()
            if resposta == "True":
                print("\n\n\n ----login efetuado com sucesso----\n\n\n")
                return True

            else: print(resposta)
        #essa condição é para criar a conta, então
        #se o usuário escolher um email que já existe 
        #ele não deixa criar a conta
        elif escolha == 2: #criar conta
            resposta = criar_conta()
            if resposta == "True":
                print("\n\n\n ----conta criada com sucesso----\n\n\n")
                return True

            else: print(resposta)
        #aqui encerra
        elif escolha == 3: #sair
            desconectar()
            return False
        #trata erros
        else: print("\n\n\n ----comando invalido----\n\n\n")

# Essa função é para depois que faz o login
# Vai mostrar o menú de opções disponíveis
def menu():
    while True:
        print("\n\n\n1 - Enviadas\n2 - Recebidas\n3 - Enviar mensagem\n4 - Excluir mensagem\n5 - Sair\n\n")
        escolha = int(input())
        # chama a função de consultar as mensagens enviadas
        if escolha == 1:
            consultar_mensagens_enviadas()
        # chama a função de consultar as mensagens recebidas
        elif escolha == 2:
            consultar_mensagens_recebidas()
        # chama a função de enviar mensagem
        elif escolha == 3:
            retorno = enviar_mensagem()
        # excluiria uma mensagem se eu tivesse feito kk
        elif escolha == 4:
            excluir_mensagem()
        # encerra a conexão
        elif escolha == 5:
            print("encerrando conexao")
            break
        # tratamento de erro
        else: print("\n\n -----opcao invalida-----\n\n")

# Função principal
def main():
    # Se o login ou criar conta deram certo ele entra aqui
    if verificacao():
        # executa a thread
        thread2 = threading.Thread(target=menu)
        thread2.start()
    # caso o login tenha dado errado ou o usuário saiu antes de
    # acessar o email dele, aí cai no else e encerra
    else:
        print("encerrando conexao")

main()
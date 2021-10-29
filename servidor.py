import socket
import threading

ip = ""
porta = 40000

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind((ip, porta))

# Classe para guardar os dados dos usuários
# **não sei se pode usar POO**
class CaixaDeMensagens:
    def __init__(self):
        self.lista_de_emails = []
        self.emails_recebidos = []
        self.emails_enviados = []
        self.identificador = None
        self.endereco = None

#criei dicionários para armazenar os emails e senhas
usuarios = {}
# e também para cada email eu terei um objeto com os dados dele
mensagens = {}

# função para criar a conta, recebe como parâmetros 
# senha, email, o ip e a porta 
def criar_conta(email, senha, cliente, endereco):
    #uso os dicionários como globais para poder guardar os dados
    global usuarios, mensagens
    # aqui verifica se o email que o usuário quer usar 
    # já está no dicionário de emails, caso já esteja
    # aí ele retorna a mensgem dizendo para escolher outro
    if email in usuarios:
        return "email ja existe, escolha outro"
    #caso não esteja, é porque dá pra usar
    else:
        #aí guardo os dados nos dicionários e retorno true
        usuarios[email] = senha
        mensagens[email] = CaixaDeMensagens()
        mensagens[email].identificador = cliente
        mensagens[email].endereco = endereco
        return "True"

# Função para o login, recebe o email e a senha
def login(email, senha):
    #uso os dicionários como globais para acessar os dados
    global usuarios, mensagens
    # verifica se o email não está no dicionário de usuários
    # se não estiver, aí retorna que o email está errado
    if email not in usuarios: 
        return "email incorreto"
    #caso esteja 
    else:
        # aqui eu fiz um loop pra encontrar o usuário e ver se 
        # a senha está errada, olhando agora percebo que é 
        # completamente desnecessário, já que com o email
        # poderia acessar diretamente, mas melhor não mexer 
        # já que está funcionando né
        for i in usuarios:
            if i == email and usuarios[i] == senha:
                return "True"
        # caso a senha não corresponda aí ele retorna a mensagem ali
        return "senha incorreta"

# Essa função retorna uma string com todas as mensagens que o usuário quiser
def ler(tipo, email):
    global mensagens
    # como parâmetros eu passo o email que é a chave que vou
    # precisar para acessar o objeto da caixa de mensagens
    # Aí eu verifico se a string começa com recebidas,
    # se sim eu compacto todas as mensagens recebidas em uma
    # string e envio para o cliente, e o mesmo ocorre para enviadas
    if tipo == "recebidas":
        lista = mensagens[email].emails_recebidos
        tudo = [str(email[0])+"&"+str(email[1])+"&"+str(email[2])+";" for email in lista]
        # a string palavra será enviada para o cliente com os delimitadores
        if len(mensagens[email].emails_recebidos) > 0:
            palavra = ""
            for i in tudo:
                palavra += i
        else: palavra = "nenhum&email&encontrado;"

    elif tipo == "enviadas":
        lista = mensagens[email].emails_enviados
        tudo = [str(email[0])+"&"+str(email[1])+"&"+str(email[2])+";" for email in lista]
        # a string palavra será enviada para o cliente com os delimitadores
        if len(mensagens[email].emails_enviados) > 0:
            palavra = ""
            for i in tudo:
                palavra += i
        else: palavra = "nenhum&email&encontrado;"
    # esse é para mostrar todas as mensagens juntas, mas não fiz ainda, lá no cliente
    else:
        lista = mensagens[email].lista_de_emails
        tudo = [str(email[0])+"&"+str(email[1])+"&"+str(email[2])+";" for email in lista]

    return palavra

# Função para enviar as mensagens, recebe como parâmetros
# o destino que é o email do cliente que vai receber a mensagem,
# o título, o texto e o email de quem enviou 
def enviar_mensagem(destino, titulo, texto, email):
    # dicionário de mensagens para poder guardar os dados
    global mensagens
    # se o email de destino não existir ele envia o aviso diretamente
    # para a caixa de mensagens do remetente
    if destino not in mensagens:
        mensagens[email].emails_recebidos.append([destino, "Erro no envio", "Email não encontrado"])
        mensagens[email].lista_de_emails.append([destino, "Erro no envio", "Email não encontrado"])

    else:
        # aí quando o email existe eu adiciono os dados nas listas
        mensagens[destino].emails_recebidos.append([email, titulo, texto])
        mensagens[destino].lista_de_emails.append([email, titulo, texto])
        mensagens[email].emails_enviados.append([email, titulo, texto])
        mensagens[email].lista_de_emails.append([email, titulo, texto])

    # aí retorna que foi enviado, mas não seria necessário
    return "enviado"

def excluir(tipo, indice, email):

    global mensagens
    if tipo == "enviadas":
        if indice >= len(mensagens[email].emails_enviados) or indice < 0:
            return "Mensagem nao existe"
        else:
            del(mensagens[email].emails_enviados[indice])
            return "email excluido"
    else:
        if indice >= len(mensagens[email].emails_recebidos) or indice < 0:
            return "Mensagem nao existe"
        else:
            del(mensagens[email].emails_recebidos[indice])
            return "email excluido"

# função que cria a comunicação com cada cliente, com o auxílio das
# threads
def cliente_socket(cliente, porta):
    #inicia
    print("pronto para receber dados")
    while True:
        # Fica esperando o cliente enviar algum dado
        resposta = cliente.recv(2048).decode('utf-8')
        # Assim que ele envia, as condições verificarão o que ele precisa
        if resposta:
            # se ele quiser fazer login, aí entra nesse, lembrando que o que 
            # é recebido do usuário é uma string e no início dessa string que eu
            # coloco o que ele quer
            if resposta.startswith("login="):
                # aqui separa os dados de acordo com o delimitador
                _ , email, senha = resposta.split("=")
                # aí chama a função de login ali de cima 
                retorno = login(email, senha)
                # e aí envia a requisição para o cliente
                cliente.send(retorno.encode('utf-8'))   
            #se quiser criar a conta será o mesmo processo de fazer login
            elif resposta.startswith("criarconta="):
                _ , email, senha = resposta.split("=")
                retorno = criar_conta(email, senha, cliente, porta)
                cliente.send(retorno.encode('utf-8'))
            #encerra a conexão
            elif resposta.startswith("desconectar="):
                cliente.close()
                break
            # da mesma forma que as anteriores, envia a mensagem, nesse caso
            elif resposta.startswith("enviar="):
                _ , destino, titulo, texto, email = resposta.split("=")
                retorno = enviar_mensagem(destino, titulo, texto, email)
                cliente.send(retorno.encode('utf-8'))
            # se quiser ler as mensagens também faz o mesmo processo
            elif resposta.startswith("ler="):
                _ , tipo, email = resposta.split("=")
                retorno = ler(tipo, email)
                cliente.send(retorno.encode('utf-8'))
            # condição para excluir mensagem 
            elif resposta.startswith("excluir="):
                _ , tipo, indice, email = resposta.split("=")
                retorno = excluir(tipo, int(indice), email)
                cliente.send(retorno.encode('utf-8'))

    cliente.close()

# Função principal
def main():
    # esperando novos usuários
    print("Aguardando conexao...")
    servidor.listen()
    # se aparecer algum, aí aceita as conexões e inicia as threads, que no caso do servidor é uma por cliente
    while True:
        clientee, porta_cliente = servidor.accept()
        print("conectado com um novo cliente")
        thread = threading.Thread(target=cliente_socket, args=(clientee, porta_cliente))
        thread.start()
        print(f"conexoes ativas: {threading.activeCount() - 1}")

main()

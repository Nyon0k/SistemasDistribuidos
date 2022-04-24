#Cliente

def validadorCliente(s_msg):
    palavras = []
    try:
        arq = open(s_msg, 'r')
        for linha in arq:
            for palavra in linha.split():
                palavras.append(palavra)
        palavras.sort()
        print(palavras)
        arq.close()
        return True
    except:
        print('CLIENT_ERROR -- Arquivo não encontrado!')
        return False

import socket
HOST = '192.168.68.104'
PORTA = 5000

#criar o descritor de socket
sock = socket.socket() #AF_INET, SOCK_STREAM
#estabelecer conexao
sock.connect((HOST, PORTA))
#enviar mensagem de hello
print('Digite o nome do arquivo ou digite "echodown" para terminar:')
while True:
    s_msg = bytes(input(), encoding = 'utf-8')
    sock.send(s_msg)
    #receber resposta do lado passivo
    msg = sock.recv(1024)
    if not msg:
        sock.close()
        break
    #encerrar a conexao e desliga o servidor
    if msg == b'dropserver':
        sock.close()
        break
    #encerrar a conexao
    if msg == b'SERVER_ERROR':
        print('SERVER_ERROR -- Arquivo não encontrado na base de dados!')
        sock.close()
        break
    if s_msg == b'echodown':
        sock.close()
        break
    print(str(msg, encoding = 'utf-8'))
    
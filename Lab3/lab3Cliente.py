#Cliente

import socket
HOST = '192.168.68.105'
PORTA = 5001

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
    if s_msg == b'echodown':
        sock.close()
        break
    #encerrar a conexao
    if msg == b'SERVER_ERROR':
        print('SERVER_ERROR -- Arquivo não encontrado na base de dados!')
        sock.close()
        break
    print(str(msg, encoding = 'utf-8'))
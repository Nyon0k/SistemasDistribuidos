#Lado ativo
import socket
HOST = '192.168.68.104'
PORTA = 5000
#criar o descritor de socket
sock = socket.socket() #AF_INET, SOCK_STREAM
#estabelecer conexao
sock.connect((HOST, PORTA))
#enviar mensagem de hello
while True:
    s_msg = bytes(input(), encoding = 'utf-8')
    sock.send(s_msg)
    #receber resposta do lado passivo
    msg =  sock.recv(1024)
    print(str(msg, encoding = 'utf-8'))
    #encerrar a conexao
    if s_msg == b'echodown':
        sock.close()
        break
#Lado ativo
import socket
HOST = '192.168.68.104'
PORTA = 5000
#criar o descritor de socket
sock = socket.socket() #AF_INET, SOCK_STREAM
#estabelecer conexao
sock.connect((HOST, PORTA))
#enviar mensagem de hello
sock.send(b'Ola, sou o lado ativo')
#receber resposta do lado passivo
msg =  sock.recv(1024)
print(str(msg, encoding = 'utf-8'))
#encerrar a conexao
sock.close()
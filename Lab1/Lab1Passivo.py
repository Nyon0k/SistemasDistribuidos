#Lado passivo
import socket
HOST = '' #interface padrao de comunicacao da maquina
PORTA = 5000 #identifica o processo na maquina

#criar o descritor socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Internet e TCP
#vincular o endereco e porta
sock.bind((HOST, PORTA))
#colocar-se em modo de espera
sock.listen(1) #argumento indica a qtde de conexoes pendentes
#aceitar conexao
novoSock, endereco = sock.accept()
print('Conectado com: ' + str(endereco))
while True:
  #esperar por mensagem do lado ativo
  msg = novoSock.recv(1024) #argumento indica qtde maxima de bytes
  if not msg:
    break
  else:
    print(str(msg, encoding = 'utf-8'))
    novoSock.send(msg)
#fechar o descritor de socket da conexao
novoSock.close()
#fechar o descritor de socket principal
sock.close()
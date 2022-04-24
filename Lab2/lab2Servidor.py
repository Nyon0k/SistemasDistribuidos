#Servidor
import collections
import re

#validador de arquivo existente
def validadorServidor(msg):
    palavras = []
    try:
        arq = open(msg, 'r')
        for linha in arq:
            for palavra in linha.split():
                palavras.append(palavra)
        return True
    except:
        print('SERVER_ERROR -- Arquivo não encontrado na base de dados!')
        return False

#processa os dados para retorno adequado ao cliente
def processamentoResposta(msg):
    palavras = []
    mf5_aux = []
    mf5_final = ''
    arq = open(msg, 'r')
    for linha in arq:
        for palavra in linha.split():
            palavras.append(palavra)
    arq.close()
    mais_frequentes = collections.Counter(palavras)
    mf5 = mais_frequentes.most_common(5)
    for parte in mf5:
        mf5_aux.append(parte[0])
    mf5_aux.sort()
    for p in mf5_aux:
        mf5_final = mf5_final + ' ' + p
    print(str(mf5_final))
    return mf5_final

import socket
HOST = '192.168.68.104' #interface padrao de comunicacao da maquina
PORTA = 5000 #identifica o processo na maquina

#criar o descritor socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Internet e TCP
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#vincular o endereco e porta
sock.bind((HOST, PORTA))
#colocar-se em modo de espera
sock.listen(1) #argumento indica a qtde de conexoes pendentes
while True:
    mem_msg = ''
    sock.listen(1)
    #aceitar conexao
    novoSock, endereco = sock.accept()
    print('Conectado com: ' + str(endereco))
    while True:
      #esperar por mensagem do lado ativo
      msg = novoSock.recv(1024) #argumento indica qtde maxima de bytes
      #desliga o servidor
      if msg == b'dropserver':
        mem_msg = str(msg, encoding = 'utf-8')
        print(mem_msg)
        novoSock.send(msg)
        break
      if not msg:
        break
      if validadorServidor(str(msg, encoding = 'utf-8')) == False:
        novoSock.send(b'SERVER_ERROR')
        break
      else:
        response = processamentoResposta(str(msg, encoding = 'utf-8'))
        print(response)
        novoSock.send(bytes(response, encoding = 'utf-8'))
    #fechar o descritor de socket da conexao
    novoSock.close()
    print(str(mem_msg))
    if str(msg, encoding = 'utf-8') == 'dropserver':
      break
#fechar o descritor de socket principal
sock.close()
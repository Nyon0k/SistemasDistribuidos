#Servidor
import collections
import re
import socket
import sys
import multiprocessing
import select


HOST = '192.168.68.105' #interface padrao de comunicacao da maquina
PORTA = 5001 #identifica o processo na maquina
mem_msg = ''

#define a lista de I/O de interesse (jah inclui a entrada padrao)
entradas = [sys.stdin]
#armazena historico de conexoes
conexoes = {}

#cria socket de servidor e o coloca em modo espera por conexoes
def iniciaServidor():
    #cria o socket 
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Internet(IPv4 + TCP)
    #vincula a localizacao do servidor
    sock.bind((HOST, PORTA))
    #coloca-se em modo de espera por conexoes
    sock.listen(5)
    #configura o socket para o modo nao-bloqueante
    sock.setblocking(False)
    #inclui o socket principal na lista de entradas de interesse
    entradas.append(sock)
    return sock

#aceita pedido de conexao com um cliente
def aceitaConexao(sock):
    #estabelece conexao com o proximo cliente
    cliente_sock, endereco = sock.accept()
    #registra a nova conexao
    conexoes[cliente_sock] = endereco
    return cliente_sock, endereco

def atendeRequisicoes(cliente_sock, endereco, mem_msg):
    while True:
        #esperar por mensagem do lado ativo
        msg = cliente_sock.recv(1024) #argumento indica qtde maxima de bytes
        if not msg:
            print(str(endereco) + '-> encerrou')
            return
        #desliga o servidor
        if msg == b'dropserver':
            mem_msg = str(msg, encoding = 'utf-8')
            print(mem_msg)
            cliente_sock.send(msg)
            print(str(endereco) + '-> encerrou')
            return
        if validadorServidor(str(msg, encoding = 'utf-8')) == False:
            cliente_sock.send(b'SERVER_ERROR')
            print(str(endereco) + '-> encerrou')
            return
        else:
            response = processamentoResposta(str(msg, encoding = 'utf-8'))
            print(response)
            cliente_sock.send(bytes(response, encoding = 'utf-8'))
        print(str(mem_msg))
        if str(msg, encoding = 'utf-8') == 'dropserver':
            return

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

clientes = [] #armazena os processos criados para fazer join
sock = iniciaServidor()
print("Servidor iniciado\nAguardando conexao...")
while True:
    mem_msg = ''
    #espera pelas entradas interessadas
    leitura, escrita, excecao = select.select(entradas, [], [])
    #tratar todas as entradas prontas
    for pronto in leitura:
        if pronto == sock: #pedido novo de conexao
            cliente_sock, endereco = aceitaConexao(sock)
            print('Conectado com: ' + str(endereco))
            #cria novo processo para atender o cliente
            cliente = multiprocessing.Process(target = atendeRequisicoes, args = (cliente_sock, endereco, mem_msg))
            cliente.start()
            clientes.append(cliente) #armazena a referencia da thread para usar com join()
        elif pronto == sys.stdin: #entrada padrao
            cmd = input()
            if cmd == 'fim': #solicitacao de finalizacao do servidor
                for c in clientes: #aguarda todos os processos terminarem
                    c.join()
                sock.close()
                sys.exit()
            elif cmd == 'hist':
                print(str(conexoes.values()))
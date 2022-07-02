import numbers
import random
import multiprocessing
from sys import flags
import time
from tracemalloc import stop

import rpyc 
from rpyc.utils.server import ThreadedServer

SERVIDOR = '172.24.21.48'

nodes = []
nodes_up = []

# Cria réplicas
def criaNodes():
    nodes.append((1, 9001, True, ((SERVIDOR, 9002), (SERVIDOR, 9003), (SERVIDOR, 9004)))) #A
    nodes.append((2, 9002, False, ((SERVIDOR, 9001), (SERVIDOR, 9003), (SERVIDOR, 9004)))) #B
    nodes.append((3, 9003, False, ((SERVIDOR, 9001), (SERVIDOR, 9002), (SERVIDOR, 9004)))) #C
    nodes.append((4, 9004, False, ((SERVIDOR, 9001), (SERVIDOR, 9002), (SERVIDOR, 9003)))) #D

def iniciaNodes():
	for _ in range(4):
		nodes_up.append(multiprocessing.Process(target = iniciaServer, args = nodes[_]))
		nodes_up[_].start()

def finalizaNodes():
    for _ in range(4):
        nodes_up[_].join()

##### Host #####

#Ver documentação em: https://rpyc.readthedocs.io/en/latest/

# Servidor de echo usando RPC 
from pickle import TRUE

# classe que implementa o servico de echo
class Echo(rpyc.Service):
    def __init__(self, num, vizinhos, porta, bastao):
        self.num = num
        self.vizinhos = vizinhos
        self.porta = porta
        self.bastao = bastao
        self.x = 0
        self.historico_x = [(0, 0)]

	# executa quando uma conexao eh criada
    def on_connect(self, conn):
        #print('<' + 'connect, ' + str(self.porta) + ', ' + str(SERVIDOR) + '>')
        pass

	# executa quando uma conexao eh fechada
    def on_disconnect(self, conn):
        #print('<' + 'disconnet, ' + str(self.porta) + ', ' + str(SERVIDOR) + '>')
        pass

    def exposed_mostraReplicas(self):
        print('## Seu nó ##')
        print(self.num, self.porta, self.x, self.bastao)
        print('## Vizinhos ##')
        for viz in self.vizinhos:
            print(viz[1]-9000, viz[1])
        print('----------')

    def exposed_lerX(self, pai = 0):
        if pai == 1:
            print('Id: ' + str(self.num) + ', Valor de X: ' + str(self.x))
            return
        print('Id: ' + str(self.num) + ', Valor de X: ' + str(self.x))
        for vizinho in self.vizinhos:
            conn = rpyc.connect(vizinho[0], vizinho[1])
            conn.root.exposed_lerX(1)
            conn.close()
        return

    def exposed_historicoX(self, pai = 0):
        if pai == 1:
            print('Id: ' + str(self.num) + ', Historico de X: ' + str(self.historico_x))
            return
        print('Id: ' + str(self.num) + ', Historico de X: ' + str(self.historico_x))
        for vizinho in self.vizinhos:
            conn = rpyc.connect(vizinho[0], vizinho[1])
            conn.root.exposed_historicoX(1)
            conn.close()
        return

    def exposed_alteraValor(self, nvx):
        if self.bastao == True:
            self.x = int(nvx)
            self.historico_x.append((self.num, self.x))
            self.exposed_atualizaValorEmReplicas(self.x)
            return
        else:
            self.exposed_pegaBastao()
            self.exposed_alteraValor(nvx)

    def exposed_pegaBastao(self, pai = 0):
        if pai == 1:
            if self.bastao == True:
                self.bastao = False
            return
        for vizinho in self.vizinhos:
            conn = rpyc.connect(vizinho[0], vizinho[1])
            conn.root.exposed_pegaBastao(1)
            conn.close()
        self.bastao = True
        return

    def exposed_atualizaValorEmReplicas(self, nvx, pai = 0):
        if pai == 1:
            self.x = nvx
            return
        for vizinho in self.vizinhos:
            conn = rpyc.connect(vizinho[0], vizinho[1])
            conn.root.exposed_atualizaValorEmReplicas(nvx, 1)
            conn.close()
        return

def iniciaServer(num, porta, bastao, vizinhos):
	srv = ThreadedServer(Echo(num, vizinhos, porta, bastao), port = porta)
	srv.start()

##### Client #####

def iniciaConexao(PORTA_CLIENT):
    conn = rpyc.connect(SERVIDOR, int(PORTA_CLIENT))
    return conn

def fazRequisicoes(conn, escolha):
    if escolha == 0:
        conn.root.exposed_mostraReplicas()
    if escolha == 1:
        conn.root.exposed_lerX()
    if escolha == 2:
        conn.root.exposed_historicoX()
    if escolha == 3:
        print('Digite o valor do X:')
        novo_x = input()
        conn.root.exposed_alteraValor(novo_x)


def main():
    # Inicializa Grafo
    criaNodes()
    # Inicializa Nós
    iniciaNodes()

    flag = True
    while flag == True:
        print('Digite um ID entre [1, 4] para continuar ou [5] para sair:')
        id = int(input())
        if id == 5:
            print('----- Programa Encerrado -----')
            finalizaNodes()
            break
        PORTA_CLIENT = 9000 + id
        print('Porta: ' + str(PORTA_CLIENT) + ', Id: ' + str(id))
        conn = iniciaConexao(PORTA_CLIENT)
        print('--- Menu de Nó ---')
        print('0 - MostrarReplicas')
        print('1 - Ler X')
        print('2 - Ler historicoX')
        print('3 - Alterar X')
        print('4 - Finalizar')
        print('------------')
        while True:
            escolha = input()
            if int(escolha) == 4:
                break
            fazRequisicoes(conn, int(escolha))

# executa o cliente e host
if __name__ == "__main__":
	main()
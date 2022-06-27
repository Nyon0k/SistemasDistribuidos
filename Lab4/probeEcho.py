import numbers
import random
import multiprocessing
import time
from tracemalloc import stop

import rpyc 
from rpyc.utils.server import ThreadedServer

SERVIDOR = '172.21.187.196'

nodes = []
nodes_up = []

# Utilizando o grafo passado no slide da eleição de líder
def criaNodes():
	nodes.append((1, 9001, ((SERVIDOR, 9002), (SERVIDOR, 9010)))) #A
	nodes.append((2, 9002, ((SERVIDOR, 9001), (SERVIDOR, 9003), (SERVIDOR, 9007)))) #B
	nodes.append((3, 9003, ((SERVIDOR, 9002), (SERVIDOR, 9004), (SERVIDOR, 9005)))) #C
	nodes.append((4, 9004, ((SERVIDOR, 9003), (SERVIDOR, 9005), (SERVIDOR, 9006)))) #D
	nodes.append((5, 9005, ((SERVIDOR, 9003), (SERVIDOR, 9004), (SERVIDOR, 9006), (SERVIDOR, 9007)))) #E
	nodes.append((6, 9006, ((SERVIDOR, 9004), (SERVIDOR, 9005), (SERVIDOR, 9009)))) #F
	nodes.append((7, 9007, ((SERVIDOR, 9002), (SERVIDOR, 9005), (SERVIDOR, 9008), (SERVIDOR, 9010)))) #G
	nodes.append((8, 9008, ((SERVIDOR, 9007), (SERVIDOR, 9009)))) #H
	nodes.append((9, 9009, ((SERVIDOR, 9006), (SERVIDOR, 9008)))) #I
	nodes.append((10, 9010, ((SERVIDOR, 9001), (SERVIDOR, 9007)))) #J

def iniciaNodes():
	for _ in range(10):
		nodes_up.append(multiprocessing.Process(target = iniciaServer, args = nodes[_]))
		nodes_up[_].start()

def finalizaNodes():
	for _ in range(10):
		nodes_up[_].join()

##### Host #####

#Ver documentação em: https://rpyc.readthedocs.io/en/latest/

# Servidor de echo usando RPC 
from pickle import TRUE

# classe que implementa o servico de echo
class Echo(rpyc.Service):
	def __init__(self, num, vizinhos, porta):
		self.num = num
		self.vizinhos = vizinhos
		self.porta = porta
		self.probed = False
		self.res = [self.num]

	# executa quando uma conexao eh criada
	def on_connect(self, conn):
		pass

	# executa quando uma conexao eh fechada
	def on_disconnect(self, conn):
		pass

	# executa uma nova eleição
	def exposed_election(self, mostraRes):
		# Recursão de chamadas
		def recursao(res):
			self.res.append(res)
			if len(self.res) == len(self.vizinhos)+1:
				maior = 0
				for num in self.res:
					if num == 'probed':
						pass
					elif maior <= num:
						maior = num
				print('Vertice ' + str(self.num) + ': Resultado final => ' + str(maior))
				mostraRes(maior)
		
		if self.probed == True:
			mostraRes('probed')
			return

		self.probed = True

		for vizinho in self.vizinhos:
			print('Atual: ' + str(self.porta - 9000) + ' -> Vizinho: ' + str(vizinho[1] - 9000))
			conn = rpyc.connect(*vizinho)
			conn.root.election(recursao)
			conn.close()

def iniciaServer(num, porta, vizinhos):
	srv = ThreadedServer(Echo(num, vizinhos, porta), port = porta)
	srv.start()

##### Client #####

def iniciaConexao(PORTA_CLIENT):
	'''Conecta-se ao servidor.
	Saida: retorna a conexao criada.'''
	conn = rpyc.connect(SERVIDOR, int(PORTA_CLIENT))
	return conn

def fazRequisicoes(conn):
	'''Faz requisicoes ao servidor e exibe o resultado.
	Entrada: conexao estabelecida com o servidor'''
	# chama método de eleição de líder
	conn.root.exposed_election(mostraRes)

def mostraRes(res):
	if str(res) == None:
		print(f'res: {res}')

def geraPorta():
	p = random.randint(9001, 9010)
	return p

def main():
	# Inicializa Grafo
	criaNodes()
	# Inicializa Nós
	iniciaNodes()

	# Gera porta random para começar
	PORTA_CLIENT = geraPorta()
	print(PORTA_CLIENT-9000)
	conn = iniciaConexao(PORTA_CLIENT)
	fazRequisicoes(conn)

	# Finaliza Nós
	finalizaNodes()

# executa o cliente e host
if __name__ == "__main__":
	main()
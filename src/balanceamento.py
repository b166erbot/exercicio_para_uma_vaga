"""Módulo onde tratará o balanceamento."""

from sys import argv
from typing import Iterable, Union


class Usuario:
    """Classe que representa o usuário final."""

    def __init__(self, ttask):
        """Método de inicialização."""
        self.ttask = ttask

    def consumir(self):
        """Método que simula a execução das tarefas do usuário."""
        self.ttask -= 1


class Servidor:
    """Classe que representa o servidor."""

    umax = 1
    ttask = 1

    def __init__(self):
        """Método de inicialização."""
        self.users = [Usuario(self.ttask)]
        self.tick = 0

    def __repr__(self) -> str:
        """Método que retorna o número de usuários ativos no server."""
        quantidade = f"{len(self.users)}"
        self.tick += 1
        self._remover_automaticamente()
        return quantidade

    def add(self):
        """Método que adiciona um Usuario no servidor."""
        if len(self.users) < self.umax:
            self.users.append(Usuario(self.ttask))

    def _remover_automaticamente(self):
        """Método que remove os usuários caso não haja mais tarefas."""
        for usuario in self.users:
            usuario.consumir()
        self.users = list(filter(lambda x: x.ttask > 0, self.users))


class Gerenciador:
    """Classe que gerencia os servidores."""

    tick = 0

    def __init__(self):
        """Método de inicialização."""
        self.servers = []

    def __repr__(self) -> str:
        """Método que retorna o número de pessoas ativas no server."""
        string_formatada = f"{','.join(map(repr, self.servers))}" or '0'
        removidos = self._remover_automaticamente()
        self._somar_tick(removidos)
        return string_formatada

    def _server_com_espaco(self) -> Union[Servidor, None]:
        """Método que retorna um server com espaço ou None."""
        filtro = filter(lambda x: len(x.users) < x.umax, self.servers)
        return next(filtro, None)

    def adicionar_usuario(self):
        """Método que adiciona um novo usuário em um server novo ou antigo."""
        servidor = self._server_com_espaco()
        if servidor:
            servidor.add()
        else:
            self.servers.append(Servidor())

    def _remover_automaticamente(self) -> set:
        """Método que remove os servidores que não contém mais usuários."""
        servers = filter(lambda server: len(server.users) > 0, self.servers)
        servers = list(servers)
        removidos = set(self.servers) - set(servers)
        self.servers = servers
        return removidos

    def _somar_tick(self, servers_removidos: Iterable):
        """Método que soma todos os ticks."""
        self.tick += sum([server.tick for server in servers_removidos])

    def finalizar(self):
        """Método que mantém o servidor rodando se tiver usuários ativos."""
        while self.servers:
            print(self)
        print(self, self.tick, sep='\n')


def ler_arquivo(nome: str) -> Iterable:
    """Função que lê um arquivo e retorna um gerador."""
    with open(nome) as arquivo:
        dados = map(lambda x: int(x.strip()), arquivo.readlines())
    return dados


def balanceamento(arquivo: str):
    """Função que gerencia e balanceia as pessoas nos servidores."""
    dados = ler_arquivo(arquivo)
    Servidor.ttask, Servidor.umax = next(dados), next(dados)
    gerenciador = Gerenciador()
    for usuários in dados:
        for usuário in range(usuários):
            gerenciador.adicionar_usuario()
        print(gerenciador)
    gerenciador.finalizar()


def main():
    """Função principal que irá rodar o código."""
    for arquivo in argv[1:]:
        print()
        balanceamento(arquivo)

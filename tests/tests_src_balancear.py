from typing import Iterable
from unittest import TestCase
from unittest.mock import MagicMock, mock_open, patch

from src.balanceamento import (Gerenciador, Servidor, Usuario, balanceamento,
                               ler_arquivo, main)


class FuncaoLerArquivo(TestCase):
    def setUp(self):
        with patch('builtins.open', mock_open(read_data='1\n1\n')) as mocked:
            self.resultado = ler_arquivo(mocked)

    def test_ler_arquivo_retornando_objeto_iterador(self):
        self.assertIsInstance(self.resultado, Iterable)

    def test_retornando_somente_inteiros_dentro_do_iteravel(self):
        self.assertTrue(all(isinstance(x, int) for x in self.resultado))


class ClasseServidor(TestCase):
    Servidor.ttask = 1
    Servidor.umax = 2

    # @classmethod  # não funciona como o esperado.
    # def setUpClass(cls):
    #     Servidor.ttask = 1
    #     Servidor.umax = 2

    def setUp(self):
        self.server = Servidor()

    def test_repr_retornando_1_como_string(self):
        self.assertEqual(repr(self.server), '1')

    def test_repr_retornando_2_caso_dunder_iadd_seja_chamado(self):
        self.server.add()
        self.assertEqual(repr(self.server), '2')

    def test_removendo_um_usuario_caso_estejam_abaixo_de_1(self):
        self.server._remover_automaticamente()
        self.assertEqual(repr(self.server), '0')

    def test_removendo_dois_usuarios_caso_estejam_abaixo_de_1(self):
        self.server.add()
        self.server._remover_automaticamente()
        self.assertEqual(repr(self.server), '0')

    def test_usuario_nao_sendo_removido_caso_ttask_seja_maior_que_1(self):
        self.server.users[0].ttask = 2
        self.assertEqual(repr(self.server), '1')

    def test_remover_nao_gerando_erro_caso_server_nao_contenha_usuarios(self):
        self.server.users.pop()
        self.server._remover_automaticamente()
        self.assertEqual(repr(self.server), '0')

    def test_consumir_sendo_chamado_dentro_do_remover_automaticamente(self):
        mock = MagicMock()
        self.server.users[0].consumir = mock
        self.server._remover_automaticamente()
        mock.assert_any_call()

    def test_testando_umax(self):
        Servidor.umax = 4
        self.geren = Gerenciador()
        for x in range(10):
            self.geren.adicionar_usuario()
        self.assertEqual(repr(self.geren), '4,4,2')
        Servidor.umax = 1


class ClasseUsuario(TestCase):
    def setUp(self):
        self.user = Usuario(2)

    def test_ttask_igual_a_1_caso_seja_chamado_o_metodo_consumir(self):
        self.user.consumir()
        self.assertEqual(self.user.ttask, 1)

    def test_ttask_igual_a_0_caso_seja_chamado_o_metodo_consumir_2_vezes(self):
        self.user.consumir()
        self.user.consumir()
        self.assertEqual(self.user.ttask, 0)


class ClasseGerenciador(TestCase):
    def setUp(self):
        self.geren = Gerenciador()
        self.geren.adicionar_usuario()

    def test_repr_retornando_1(self):
        self.assertEqual(repr(self.geren), '1')

    def test_repr_retornando_2(self):
        self.geren.adicionar_usuario()
        self.assertEqual(repr(self.geren), '2')

    def test_repr_retornando_2_1(self):
        self.geren.adicionar_usuario()
        self.geren.adicionar_usuario()
        self.assertEqual(repr(self.geren), '2,1')

    def test_repr_retornando_2_2(self):
        for x in range(3):
            self.geren.adicionar_usuario()
        self.assertEqual(repr(self.geren), '2,2')

    def test_repr_retornando_2_2_1(self):
        for x in range(4):
            self.geren.adicionar_usuario()
        self.assertEqual(repr(self.geren), '2,2,1')

    def test_repr_chamando_metodo_remover_automaticamente(self):
        for x in range(4):
            self.geren.adicionar_usuario()
        repr(self.geren)
        self.assertEqual(len(self.geren.servers), 0)

    def test_remover_automaticamente_removendo_servers_sem_usuarios(self):
        self.geren.servers.append(Servidor())
        self.geren.servers.append(Servidor())
        server = self.geren.servers[1]
        self.geren.servers[1].users.pop()
        retorno = self.geren._remover_automaticamente().pop()
        self.assertEqual(len(self.geren.servers), 2)
        self.assertIs(retorno, server)

    def test_metodo_SCE_retornando_servidor_caso_o_mesmo_contenha_vaga(self):
        self.assertIsInstance(self.geren._server_com_espaco(), Servidor)

    def test_metodo_SCE_retornando_None_caso_nao_haja_servidores(self):
        self.geren.servers.pop()
        self.assertIsNone(self.geren._server_com_espaco())

    def test_adicionar_usuario_adicionando_no_unico_server_disponivel(self):
        self.geren.servers = []
        for x in range(4):
            server = Servidor()
            server.add()
            self.geren.servers.append(server)
        server = Servidor()
        self.geren.servers.insert(1, server)
        self.geren.adicionar_usuario()
        self.assertEqual(len(server.users), 2)

    def test_adicionar_usuario_adicionando_um_novo_server_com_um_usuario(self):
        self.geren.servers[0].add()
        self.geren.adicionar_usuario()
        self.assertEqual(len(self.geren.servers), 2)

    def test_somar_tick_acrecentando_os_tick_dos_servers_removidos(self):
        servidores = []
        for x in range(5):
            server = Servidor()
            server.tick = 1
            servidores.append(server)
        self.geren._somar_tick(set(servidores))
        self.assertEqual(self.geren.tick, 5)

    def test_repr_retornando_0_caso_nao_haja_servers_disponiveis(self):
        self.geren = Gerenciador()
        self.assertEqual(repr(self.geren), '0')

    # @patch('src.balanceamento.print')
    # @patch('src.balanceamento.Gerenciador')
    # def test_finalizar_rodando_enquanto_conter_servers(self, geren, pprint):
    #     geren.servers.side_effect = [1, 1]
    #     self.assertEqual(pprint.call_count, 3)


class FuncaoBalanceamento(TestCase):
    @patch('src.balanceamento.Gerenciador')
    @patch('src.balanceamento.print')
    @patch('src.balanceamento.ler_arquivo')
    def test_ler_arquivo_sendo_chamado(self, mock, *_):
        balanceamento('nome_de_um_arquivo')
        self.assertEqual(mock.call_count, 1)

    @patch('src.balanceamento.ler_arquivo')
    @patch('src.balanceamento.print')
    @patch('src.balanceamento.Gerenciador')
    def test_gerenciador_sendo_instanciado(self, mock, *_):
        balanceamento('nome_de_um_arquivo')
        self.assertEqual(mock.call_count, 1)

    @patch('src.balanceamento.ler_arquivo', return_value=iter([0, 0, 2, 3]))
    @patch('src.balanceamento.print')
    @patch('src.balanceamento.Gerenciador')
    def test_gerenciador_sendo_chamado_5_vezes(self, geren, *_):
        balanceamento('nome_de_um_arquivo')
        vezes_chamado = geren.return_value.adicionar_usuario.call_count
        self.assertEqual(vezes_chamado, 5)

    @patch('src.balanceamento.ler_arquivo', return_value=iter([0, 0, 2, 1]))
    @patch('src.balanceamento.print')
    @patch('src.balanceamento.Gerenciador')
    def test_gerenciador_sendo_chamado_3_vezes(self, geren, *_):
        balanceamento('nome_de_um_arquivo')
        vezes_chamado = geren.return_value.adicionar_usuario.call_count
        self.assertEqual(vezes_chamado, 3)


class FuncaoMain(TestCase):
    @patch('src.balanceamento.print')
    @patch('src.balanceamento.argv')
    @patch('src.balanceamento.balanceamento')
    def test_funcao_rodando_em_mais_de_um_arquivo(self, mocked, argv, *_):
        argv.__getitem__.return_value = [1, 2, 3]
        main()
        self.assertEqual(mocked.call_count, 3)

    @patch('src.balanceamento.print')
    @patch('src.balanceamento.argv')
    @patch('src.balanceamento.balanceamento')
    def test_funcao_rodando_com_somente_um_arquivo(self, mocked, argv, *_):
        argv.__getitem__.return_value = [1]
        main()
        self.assertEqual(mocked.call_count, 1)

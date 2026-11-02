import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from dados import Cadastro
from modelo import Perfil, Musico, HabilidadeMusical, Busca


class TestTimbre(unittest.TestCase):
    def setUp(self):
        self.c = Cadastro()
        self.m = self.c.criarMusico("Alex", "Porto Alegre", 20, ["rock"], [("guitarra", 2)])
        self.b = self.c.criarBanda("Horizonte", "Porto Alegre", "rock")
        self.vid = self.c.criarVaga(self.b.id, "guitarra", 2, "Sábados")
        self.v = self.c.vagas[self.vid]

    def test_vaga_compativel_e_nivel_igual_ao_minimo(self):
        self.assertEqual(Busca("Porto Alegre", "guitarra", "rock").executar(self.m, [self.v]), [self.v])

    def test_nivel_insuficiente(self):
        self.v.atualizarRequisitos("guitarra", 3, "Sábados")
        self.assertEqual(Busca("").executar(self.m, [self.v]), [])

    def test_instrumento_diferente(self):
        self.v.atualizarRequisitos("bateria", 1, "")
        self.assertFalse(self.v.compativelCom(self.m))

    def test_encerrar_e_reabrir(self):
        self.v.encerrar()
        self.assertFalse(self.v.compativelCom(self.m))
        self.v.reabrir()
        self.assertTrue(self.v.compativelCom(self.m))

    def test_filtros_independentes(self):
        for busca in [Busca("Curitiba"), Busca("", "bateria"), Busca("", genero="jazz")]:
            with self.subTest(filtros=vars(busca)):
                self.assertEqual(busca.executar(self.m, [self.v]), [])

    def test_acentos_espacos_e_maiusculas(self):
        self.b.atualizarDados("Horizonte", "São Paulo")
        self.assertEqual(Busca("  SAO PAULO  ", " GUITARRA ", " ROCK ").executar(self.m, [self.v]), [self.v])

    def test_validacao_de_niveis_e_idade(self):
        for nivel in (0, 4, True, "2"):
            with self.subTest(nivel=nivel), self.assertRaises(ValueError):
                HabilidadeMusical("guitarra", nivel)
            with self.assertRaises(ValueError):
                self.v.atualizarRequisitos("guitarra", nivel, "")
        with self.assertRaises(ValueError):
            self.c.criarMusico("Bia", "Curitiba", -1, [], [("baixo", 1)])

    def test_atualizacao_invalida_preserva_cadastro(self):
        with self.assertRaises(ValueError):
            self.c.atualizarMusico(self.m.id, "Outro", "Curitiba", 21, [], [("baixo", 8)])
        self.assertIs(self.c.musicos[self.m.id], self.m)
        with self.assertRaises(ValueError):
            self.c.atualizarBanda(self.b.id, "Outra", "Curitiba", " ")
        self.assertEqual(self.b.nome, "Horizonte")

    def test_criacao_invalida_nao_cadastra(self):
        for nome, habilidades in [(" ", [("baixo", 1)]), ("Bia", []), ("Bia", [("baixo", 0)])]:
            with self.assertRaises(ValueError):
                self.c.criarMusico(nome, "Curitiba", 20, [], habilidades)
        self.assertEqual(len(self.c.musicos), 1)

    def test_multiplas_habilidades_e_duplicidade(self):
        self.m.adicionarHabilidade(HabilidadeMusical("baixo", 3))
        self.v.atualizarRequisitos("baixo", 3, "")
        self.assertTrue(self.v.compativelCom(self.m))
        with self.assertRaises(ValueError):
            self.m.adicionarHabilidade(HabilidadeMusical(" BAIXO ", 1))

    def test_atualizar_musico_preserva_associacao(self):
        self.b.adicionarIntegrante(self.m)
        novo = self.c.atualizarMusico(self.m.id, "Alex", "Curitiba", 21, ["jazz"], [("baixo", 3)])
        self.assertIs(self.b.integrantes[0], novo)
        self.assertEqual(novo.habilidades[0].instrumento, "baixo")

    def test_excluir_musico_remove_vinculos(self):
        self.b.adicionarIntegrante(self.m)
        self.b.adicionarIntegrante(self.m)
        self.assertEqual(len(self.b.integrantes), 1)
        self.c.excluirMusico(self.m.id)
        self.assertEqual(self.b.integrantes, ())
        self.assertNotIn(self.m.id, self.c.musicos)

    def test_excluir_banda_remove_vagas_sem_afetar_outras(self):
        outra = self.c.criarBanda("Outra", "Curitiba", "jazz")
        outro_id = self.c.criarVaga(outra.id, "baixo", 1, "")
        self.c.excluirBanda(self.b.id)
        self.assertNotIn(self.b.id, self.c.bandas)
        self.assertNotIn(self.vid, self.c.vagas)
        self.assertIn(outro_id, self.c.vagas)
        self.assertIn(self.m.id, self.c.musicos)

    def test_excluir_vaga_atualiza_banda(self):
        self.c.excluirVaga(self.vid)
        self.assertEqual(self.b.vagas, ())
        self.assertNotIn(self.vid, self.c.vagas)

    def test_atualizar_banda_reflete_na_busca(self):
        self.c.atualizarBanda(self.b.id, "Novo nome", "Curitiba", "jazz")
        self.assertEqual(Busca("Curitiba", genero="jazz").executar(self.m, [self.v]), [self.v])
        self.assertEqual(self.v.banda.nome, "Novo nome")

    def test_abstracao_e_polimorfismo(self):
        with self.assertRaises(TypeError):
            Perfil(10, "Nome", "Cidade")
        self.assertTrue(self.m.resumirPerfil().startswith("Músico:"))
        self.assertTrue(self.b.resumirPerfil().startswith("Banda:"))

    def test_json_preserva_dados_estados_e_associacoes(self):
        self.b.adicionarIntegrante(self.m)
        self.v.encerrar()
        with TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "dados.json"
            self.c.salvar(arquivo)
            recuperado = Cadastro.carregar(arquivo)
            self.assertEqual(recuperado.musicos[self.m.id].nome, "Alex")
            self.assertIs(recuperado.bandas[self.b.id].integrantes[0], recuperado.musicos[self.m.id])
            self.assertIs(recuperado.vagas[self.vid].banda, recuperado.bandas[self.b.id])
            self.assertIs(recuperado.bandas[self.b.id].vagas[0], recuperado.vagas[self.vid])
            self.assertFalse(recuperado.vagas[self.vid].aberta)
            self.assertEqual(recuperado.proximo_id, self.c.proximo_id)
            self.assertFalse(arquivo.with_suffix(".json.tmp").exists())

    def test_arquivo_ausente_inicia_vazio_e_corrompido_e_preservado(self):
        with TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "dados.json"
            self.assertEqual(Cadastro.carregar(arquivo).musicos, {})
            arquivo.write_text("{invalido", encoding="utf-8")
            with self.assertRaises(json.JSONDecodeError):
                Cadastro.carregar(arquivo)
            self.assertEqual(arquivo.read_text(encoding="utf-8"), "{invalido")

    def test_nao_reutiliza_id_apos_exclusao(self):
        self.c.excluirVaga(self.vid)
        novo_id = self.c.criarVaga(self.b.id, "baixo", 1, "")
        self.assertGreater(novo_id, self.vid)


if __name__ == "__main__":
    unittest.main()

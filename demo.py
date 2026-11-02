"""Demonstra as regras sem abrir a interface ou alterar os dados do usuário."""
from pathlib import Path
from tempfile import TemporaryDirectory
from dados import Cadastro
from modelo import Busca


def main():
    cadastro = Cadastro()
    m = cadastro.criarMusico("Alex", "Porto Alegre", 20, ["rock"], [("guitarra", 2)])
    b = cadastro.criarBanda("Horizonte", "Porto Alegre", "rock")
    b.adicionarIntegrante(m)
    id = cadastro.criarVaga(b.id, "guitarra", 2, "Disponibilidade aos sábados")
    busca = Busca("Porto Alegre", "guitarra", "rock")
    print(m.resumirPerfil())
    print(b.resumirPerfil())
    print("Busca inicial:", len(busca.executar(m, cadastro.vagas.values())), "vaga(s)")
    cadastro.vagas[id].encerrar()
    print("Após encerrar:", len(busca.executar(m, cadastro.vagas.values())), "vaga(s)")
    cadastro.vagas[id].reabrir()
    print("Após reabrir:", len(busca.executar(m, cadastro.vagas.values())), "vaga(s)")
    with TemporaryDirectory() as pasta:
        arquivo = Path(pasta) / "timbre.json"
        cadastro.salvar(arquivo)
        recuperado = Cadastro.carregar(arquivo)
        print("JSON recuperado:", len(recuperado.musicos), "músico(s),", len(recuperado.bandas),
              "banda(s),", len(recuperado.vagas), "vaga(s)")


if __name__ == "__main__":
    main()

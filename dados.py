"""CRUD em memória e persistência JSON local; apenas biblioteca padrão."""
import json
import os
from pathlib import Path
from modelo import Musico, Banda, HabilidadeMusical, Vaga


class Cadastro:
    def __init__(self):
        self.musicos = {}
        self.bandas = {}
        self.vagas = {}
        self.proximo_id = 1

    def _id(self):
        id = self.proximo_id
        self.proximo_id += 1
        return id

    def criarMusico(self, nome, cidade, idade, generos, habilidades):
        if not habilidades:
            raise ValueError("Informe pelo menos uma habilidade musical.")
        m = Musico(self.proximo_id, nome, cidade, idade, generos)
        for instrumento, nivel in habilidades:
            m.adicionarHabilidade(HabilidadeMusical(instrumento, nivel))
        self.musicos[self._id()] = m
        return m

    def atualizarMusico(self, id, nome, cidade, idade, generos, habilidades):
        if not habilidades:
            raise ValueError("Informe pelo menos uma habilidade musical.")
        # Valida todos os campos antes de substituir o cadastro.
        novo = Musico(id, nome, cidade, idade, generos)
        for instrumento, nivel in habilidades:
            novo.adicionarHabilidade(HabilidadeMusical(instrumento, nivel))
        antigo = self.musicos[id]
        for banda in self.bandas.values():
            if antigo in banda.integrantes:
                banda.removerIntegrante(antigo)
                banda.adicionarIntegrante(novo)
        self.musicos[id] = novo
        return novo

    def excluirMusico(self, id):
        musico = self.musicos.pop(id)
        for banda in self.bandas.values():
            banda.removerIntegrante(musico)

    def criarBanda(self, nome, cidade, estilo):
        banda = Banda(self.proximo_id, nome, cidade, estilo)
        self.bandas[self._id()] = banda
        return banda

    def atualizarBanda(self, id, nome, cidade, estilo):
        Banda(id, nome, cidade, estilo)  # Validação antes de alterar a instância associada às vagas.
        banda = self.bandas[id]
        banda.atualizarDados(nome, cidade)
        banda.atualizarBanda(estilo)

    def excluirBanda(self, id):
        for vid in [vid for vid, v in self.vagas.items() if v.banda.id == id]:
            self.excluirVaga(vid)
        del self.bandas[id]

    def criarVaga(self, banda_id, instrumento, nivel, requisitos):
        vaga = Vaga(self.bandas[banda_id], instrumento, nivel, requisitos)
        id = self._id()
        self.vagas[id] = vaga
        vaga.banda.publicarVaga(vaga)
        return id

    def atualizarVaga(self, id, instrumento, nivel, requisitos):
        self.vagas[id].atualizarRequisitos(instrumento, nivel, requisitos)

    def excluirVaga(self, id):
        vaga = self.vagas.pop(id)
        vaga.banda.removerVaga(vaga)

    def salvar(self, arquivo):
        arquivo = Path(arquivo)
        arquivo.parent.mkdir(parents=True, exist_ok=True)
        dados = {
            "versao": 1, "proximo_id": self.proximo_id,
            "musicos": [{"id": m.id, "nome": m.nome, "cidade": m.cidade,
                         "idade": m.idade, "generos": m.generos,
                         "habilidades": [[h.instrumento, h.nivel] for h in m.habilidades]}
                        for m in self.musicos.values()],
            "bandas": [{"id": b.id, "nome": b.nome, "cidade": b.cidade,
                        "estilo": b.estilo, "integrantes": [m.id for m in b.integrantes]}
                       for b in self.bandas.values()],
            "vagas": [{"id": id, "banda_id": v.banda.id, "instrumento": v.instrumento,
                       "nivel": v.nivelMinimo, "requisitos": v.requisitos, "aberta": v.aberta}
                      for id, v in self.vagas.items()]}
        temporario = arquivo.with_suffix(arquivo.suffix + ".tmp")
        try:
            temporario.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
            os.replace(temporario, arquivo)
        finally:
            temporario.unlink(missing_ok=True)

    @classmethod
    def carregar(cls, arquivo):
        arquivo = Path(arquivo)
        cadastro = cls()
        if not arquivo.exists():
            return cadastro
        dados = json.loads(arquivo.read_text(encoding="utf-8"))
        if dados["versao"] != 1:
            raise ValueError("Versão do arquivo de dados incompatível.")
        usados = set()

        def registrar(id):
            if type(id) is not int or id < 1 or id in usados:
                raise ValueError("Identificador inválido ou repetido no arquivo.")
            usados.add(id)

        for item in dados["musicos"]:
            registrar(item["id"])
            m = Musico(item["id"], item["nome"], item["cidade"], item["idade"], item["generos"])
            if not item["habilidades"]:
                raise ValueError("Músico sem habilidade no arquivo.")
            for instrumento, nivel in item["habilidades"]:
                m.adicionarHabilidade(HabilidadeMusical(instrumento, nivel))
            cadastro.musicos[m.id] = m
        for item in dados["bandas"]:
            registrar(item["id"])
            b = Banda(item["id"], item["nome"], item["cidade"], item["estilo"])
            for mid in item["integrantes"]:
                b.adicionarIntegrante(cadastro.musicos[mid])
            cadastro.bandas[b.id] = b
        for item in dados["vagas"]:
            registrar(item["id"])
            v = Vaga(cadastro.bandas[item["banda_id"]], item["instrumento"], item["nivel"], item["requisitos"])
            if type(item["aberta"]) is not bool:
                raise ValueError("Estado de vaga inválido no arquivo.")
            if not item["aberta"]:
                v.encerrar()
            cadastro.vagas[item["id"]] = v
            v.banda.publicarVaga(v)
        proximo = dados["proximo_id"]
        if type(proximo) is not int or proximo <= max(usados, default=0):
            raise ValueError("Sequência de identificadores inválida no arquivo.")
        cadastro.proximo_id = proximo
        return cadastro

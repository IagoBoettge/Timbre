"""Classes de domínio do Timbre, a partir do UML do Grupo 16."""
from abc import ABC, abstractmethod
import unicodedata


def texto(valor, campo):
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"{campo} deve ser preenchido.")
    return valor.strip()


def chave(valor):
    return "".join(c for c in unicodedata.normalize("NFD", valor.strip().casefold())
                   if unicodedata.category(c) != "Mn")


def inteiro(valor, campo, minimo=0):
    if type(valor) is not int or valor < minimo:
        raise ValueError(f"{campo} deve ser um inteiro maior ou igual a {minimo}.")
    return valor


class Perfil(ABC):
    def __init__(self, id, nome, cidade):
        self._id = inteiro(id, "Identificador", 1)
        self.atualizarDados(nome, cidade)

    @property
    def id(self):
        return self._id

    @property
    def nome(self):
        return self._nome

    @property
    def cidade(self):
        return self._cidade

    def _validarDados(self, nome, cidade):
        texto(nome, "Nome")
        texto(cidade, "Cidade")
        return True

    def atualizarDados(self, nome, cidade):
        self._validarDados(nome, cidade)
        self._nome, self._cidade = nome.strip(), cidade.strip()

    @abstractmethod
    def resumirPerfil(self):
        pass


class HabilidadeMusical:
    def __init__(self, instrumento, nivel):
        self.__instrumento = texto(instrumento, "Instrumento")
        self.atualizarNivel(nivel)

    @property
    def instrumento(self):
        return self.__instrumento

    @property
    def nivel(self):
        return self.__nivel

    def atualizarNivel(self, nivel):
        if type(nivel) is not int or nivel not in (1, 2, 3):
            raise ValueError("Nível deve ser 1, 2 ou 3.")
        self.__nivel = nivel


class Musico(Perfil):
    def __init__(self, id, nome, cidade, idade, generos):
        super().__init__(id, nome, cidade)
        self.__habilidades = []
        self.atualizarPreferencias(idade, generos)

    @property
    def idade(self):
        return self.__idade

    @property
    def generos(self):
        return tuple(self.__generos)

    @property
    def habilidades(self):
        return tuple(self.__habilidades)

    def atualizarPreferencias(self, idade, generos):
        idade = inteiro(idade, "Idade")
        if not isinstance(generos, (list, tuple)):
            raise ValueError("Gêneros devem ser uma lista.")
        novos = [texto(g, "Gênero") for g in generos]
        self.__idade, self.__generos = idade, novos

    def adicionarHabilidade(self, habilidade):
        if not isinstance(habilidade, HabilidadeMusical):
            raise ValueError("Habilidade inválida.")
        if any(chave(h.instrumento) == chave(habilidade.instrumento)
               for h in self.__habilidades):
            raise ValueError("Este instrumento já está cadastrado no perfil.")
        self.__habilidades.append(habilidade)

    def resumirPerfil(self):
        return f"Músico: {self.nome} | {self.cidade} | {self.idade} anos"


class Banda(Perfil):
    def __init__(self, id, nome, cidade, estilo):
        super().__init__(id, nome, cidade)
        self.__integrantes = []
        self.__vagas = []
        self.atualizarBanda(estilo)

    @property
    def estilo(self):
        return self.__estilo

    @property
    def integrantes(self):
        return tuple(self.__integrantes)

    @property
    def vagas(self):
        return tuple(self.__vagas)

    def atualizarBanda(self, estilo):
        self.__estilo = texto(estilo, "Estilo")

    def adicionarIntegrante(self, musico):
        if not isinstance(musico, Musico):
            raise ValueError("Integrante inválido.")
        if musico not in self.__integrantes:
            self.__integrantes.append(musico)

    def removerIntegrante(self, musico):
        if musico in self.__integrantes:
            self.__integrantes.remove(musico)

    def publicarVaga(self, vaga):
        if not isinstance(vaga, Vaga) or vaga.banda is not self:
            raise ValueError("A vaga deve pertencer a esta banda.")
        if vaga not in self.__vagas:
            self.__vagas.append(vaga)

    def removerVaga(self, vaga):
        if vaga in self.__vagas:
            self.__vagas.remove(vaga)

    def resumirPerfil(self):
        return f"Banda: {self.nome} | {self.cidade} | {self.estilo}"


class Vaga:
    def __init__(self, banda, instrumento, nivelMinimo, requisitos):
        if not isinstance(banda, Banda):
            raise ValueError("Banda inválida.")
        self.__banda = banda
        self.__aberta = True
        self.atualizarRequisitos(instrumento, nivelMinimo, requisitos)

    @property
    def banda(self):
        return self.__banda

    @property
    def instrumento(self):
        return self.__instrumento

    @property
    def nivelMinimo(self):
        return self.__nivelMinimo

    @property
    def requisitos(self):
        return self.__requisitos

    @property
    def aberta(self):
        return self.__aberta

    def __validarNivel(self, nivel):
        if type(nivel) is not int or nivel not in (1, 2, 3):
            raise ValueError("Nível mínimo deve ser 1, 2 ou 3.")
        return True

    def atualizarRequisitos(self, instrumento, nivel, requisitos):
        instrumento = texto(instrumento, "Instrumento")
        self.__validarNivel(nivel)
        if not isinstance(requisitos, str):
            raise ValueError("Requisitos devem ser um texto.")
        self.__instrumento, self.__nivelMinimo = instrumento, nivel
        self.__requisitos = requisitos.strip()

    def encerrar(self):
        self.__aberta = False

    def reabrir(self):
        self.__aberta = True

    def compativelCom(self, musico):
        return self.aberta and any(
            chave(h.instrumento) == chave(self.instrumento) and h.nivel >= self.nivelMinimo
            for h in musico.habilidades)


class Busca:
    def __init__(self, cidade, instrumento=None, genero=None):
        self.cidade = cidade.strip()
        self.instrumento = instrumento.strip() if instrumento else None
        self.genero = genero.strip() if genero else None

    def atendeFiltros(self, vaga):
        return (not self.cidade or chave(vaga.banda.cidade) == chave(self.cidade)) and (
            not self.instrumento or chave(vaga.instrumento) == chave(self.instrumento)) and (
            not self.genero or chave(vaga.banda.estilo) == chave(self.genero))

    def executar(self, musico, vagas):
        return [v for v in vagas if v.compativelCom(musico) and self.atendeFiltros(v)]

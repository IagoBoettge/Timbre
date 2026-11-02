"""Interface Tkinter. Execute: python app.py."""
from copy import deepcopy
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from dados import Cadastro
from modelo import Busca

ARQUIVO = Path(__file__).resolve().parent / "data" / "timbre.json"


class Aplicacao:
    def __init__(self, janela, cadastro):
        self.janela, self.cadastro = janela, cadastro
        self.tabelas, self.campos = {}, {}
        janela.title("Timbre — músicos e bandas locais")
        janela.geometry("1080x740")
        ttk.Label(janela, text="Timbre | Grupo 16", font=("Segoe UI", 18, "bold")).pack(pady=12)
        ttk.Label(janela, text="Níveis: 1 iniciante · 2 intermediário · 3 avançado").pack()
        abas = ttk.Notebook(janela)
        abas.pack(fill="both", expand=True, padx=15, pady=12)
        definicoes = {
            "Músicos": [("nome", "Nome"), ("cidade", "Cidade"), ("idade", "Idade"),
                        ("generos", "Gêneros separados por vírgula"),
                        ("habilidades", "Habilidades: guitarra:2;bateria:1")],
            "Bandas": [("nome", "Nome"), ("cidade", "Cidade"), ("estilo", "Estilo musical")],
            "Vagas": [("banda_id", "ID da banda"), ("instrumento", "Instrumento"),
                      ("nivel", "Nível mínimo"), ("requisitos", "Requisitos (opcional)")]}
        for tipo, definicao in definicoes.items():
            frame = ttk.Frame(abas, padding=10)
            abas.add(frame, text=tipo)
            self.campos[tipo] = {}
            for linha, (campo, rotulo) in enumerate(definicao):
                ttk.Label(frame, text=rotulo).grid(row=linha, column=0, sticky="w", padx=4, pady=5)
                variavel = tk.StringVar()
                self.campos[tipo][campo] = variavel
                ttk.Entry(frame, textvariable=variavel, width=65).grid(row=linha, column=1, sticky="ew")
            barra = ttk.Frame(frame)
            barra.grid(row=len(definicao), column=0, columnspan=2, sticky="w", pady=12)
            for rotulo, acao in [("Criar", "criar"), ("Atualizar selecionado", "atualizar"),
                                 ("Excluir selecionado", "excluir"), ("Limpar campos", "limpar")]:
                ttk.Button(barra, text=rotulo, command=lambda t=tipo, a=acao: self.acao(t, a)).pack(side="left", padx=3)
            if tipo == "Vagas":
                ttk.Button(barra, text="Encerrar / Reabrir", command=lambda: self.acao("Vagas", "alternar")).pack(side="left", padx=3)
            tabela = self.tabela(frame, ("id", "descricao", "detalhes"))
            tabela.grid(row=len(definicao) + 1, column=0, columnspan=2, sticky="nsew")
            tabela.bind("<<TreeviewSelect>>", lambda e, t=tipo: self.preencher(t))
            self.tabelas[tipo] = tabela
            frame.columnconfigure(1, weight=1)
            frame.rowconfigure(len(definicao) + 1, weight=1)

        vinculos = ttk.Frame(abas, padding=15)
        abas.add(vinculos, text="Integrantes")
        self.vinculos = {}
        for linha, (campo, rotulo) in enumerate([("banda", "ID da banda"), ("musico", "ID do músico")]):
            ttk.Label(vinculos, text=rotulo).grid(row=linha, column=0, sticky="w", pady=8)
            self.vinculos[campo] = tk.StringVar()
            ttk.Entry(vinculos, textvariable=self.vinculos[campo]).grid(row=linha, column=1)
        ttk.Button(vinculos, text="Adicionar integrante", command=lambda: self.vincular(True)).grid(row=2, column=0, pady=10)
        ttk.Button(vinculos, text="Remover integrante", command=lambda: self.vincular(False)).grid(row=2, column=1)
        self.lista_integrantes = self.tabela(vinculos, ("banda", "integrantes"))
        self.lista_integrantes.grid(row=3, column=0, columnspan=2, sticky="nsew")
        vinculos.columnconfigure(1, weight=1)
        vinculos.rowconfigure(3, weight=1)

        busca = ttk.Frame(abas, padding=15)
        abas.add(busca, text="Buscar oportunidades")
        self.filtros = {}
        for linha, (campo, rotulo) in enumerate([("musico", "ID do músico"), ("cidade", "Cidade (opcional)"),
                                               ("instrumento", "Instrumento (opcional)"), ("genero", "Gênero (opcional)")]):
            ttk.Label(busca, text=rotulo).grid(row=linha, column=0, sticky="w", pady=6)
            self.filtros[campo] = tk.StringVar()
            ttk.Entry(busca, textvariable=self.filtros[campo], width=60).grid(row=linha, column=1, sticky="ew")
        ttk.Button(busca, text="Buscar vagas compatíveis", command=self.buscar).grid(row=4, column=0, columnspan=2, pady=10)
        self.resultados = self.tabela(busca, ("banda", "cidade", "estilo", "instrumento", "nivel", "requisitos"))
        self.resultados.grid(row=5, column=0, columnspan=2, sticky="nsew")
        busca.columnconfigure(1, weight=1)
        busca.rowconfigure(5, weight=1)
        self.status = tk.StringVar(value="Cadastros gravados localmente após cada alteração.")
        ttk.Label(janela, textvariable=self.status).pack(pady=6)
        self.atualizarListas()

    def tabela(self, pai, colunas):
        tabela = ttk.Treeview(pai, columns=colunas, show="headings", selectmode="browse", height=10)
        for coluna in colunas:
            tabela.heading(coluna, text=coluna.capitalize())
            tabela.column(coluna, width=65 if coluna in ("id", "nivel") else 170, minwidth=45)
        return tabela

    def selecionado(self, tipo):
        selecao = self.tabelas[tipo].selection()
        if not selecao:
            raise ValueError("Selecione um registro na lista.")
        return int(selecao[0])

    def preencher(self, tipo):
        if not self.tabelas[tipo].selection():
            return
        id = self.selecionado(tipo)
        if tipo == "Músicos":
            m = self.cadastro.musicos[id]
            dados = dict(nome=m.nome, cidade=m.cidade, idade=m.idade, generos=", ".join(m.generos),
                         habilidades=";".join(f"{h.instrumento}:{h.nivel}" for h in m.habilidades))
        elif tipo == "Bandas":
            b = self.cadastro.bandas[id]
            dados = dict(nome=b.nome, cidade=b.cidade, estilo=b.estilo)
        else:
            v = self.cadastro.vagas[id]
            dados = dict(banda_id=v.banda.id, instrumento=v.instrumento, nivel=v.nivelMinimo, requisitos=v.requisitos)
        for campo, valor in dados.items():
            self.campos[tipo][campo].set(valor)

    def atualizarListas(self):
        for tabela in [*self.tabelas.values(), self.lista_integrantes, self.resultados]:
            tabela.delete(*tabela.get_children())
        for id, m in self.cadastro.musicos.items():
            self.tabelas["Músicos"].insert("", "end", iid=str(id), values=(id, m.resumirPerfil(),
                "; ".join(f"{h.instrumento} (nível {h.nivel})" for h in m.habilidades)))
        for id, b in self.cadastro.bandas.items():
            self.tabelas["Bandas"].insert("", "end", iid=str(id), values=(id, b.resumirPerfil(), f"{len(b.integrantes)} integrante(s)"))
            self.lista_integrantes.insert("", "end", values=(f"{id} — {b.nome}", ", ".join(f"{m.id} — {m.nome}" for m in b.integrantes)))
        for id, v in self.cadastro.vagas.items():
            self.tabelas["Vagas"].insert("", "end", iid=str(id), values=(id,
                f"{v.banda.nome}: {v.instrumento} (mínimo {v.nivelMinimo})",
                f"{'Aberta' if v.aberta else 'Encerrada'} | {v.requisitos}"))

    def gravar(self, operacao):
        anterior = deepcopy(self.cadastro)
        try:
            operacao()
            self.cadastro.salvar(ARQUIVO)
        except (ValueError, KeyError, OSError) as erro:
            self.cadastro = anterior
            mensagem = "Identificador não encontrado." if isinstance(erro, KeyError) else str(erro)
            messagebox.showerror("Não foi possível concluir", mensagem)
            return
        self.atualizarListas()
        self.status.set("Alteração salva. Execute novamente a busca para atualizar os resultados.")

    def acao(self, tipo, acao):
        if acao == "limpar":
            for variavel in self.campos[tipo].values():
                variavel.set("")
            self.tabelas[tipo].selection_remove(*self.tabelas[tipo].selection())
            return
        try:
            id = self.selecionado(tipo) if acao != "criar" else None
        except ValueError as erro:
            messagebox.showerror("Seleção necessária", str(erro))
            return
        if acao == "excluir" and not messagebox.askyesno("Excluir registro", "Confirmar exclusão? Excluir uma banda também remove suas vagas."):
            return

        def operacao():
            if acao == "excluir":
                {"Músicos": self.cadastro.excluirMusico, "Bandas": self.cadastro.excluirBanda,
                 "Vagas": self.cadastro.excluirVaga}[tipo](id)
                return
            if acao == "alternar":
                vaga = self.cadastro.vagas[id]
                vaga.encerrar() if vaga.aberta else vaga.reabrir()
                return
            d = {k: v.get() for k, v in self.campos[tipo].items()}
            if tipo == "Músicos":
                habilidades = []
                for item in d["habilidades"].split(";"):
                    partes = item.rsplit(":", 1)
                    if len(partes) != 2:
                        raise ValueError("Informe habilidades como guitarra:2;bateria:1.")
                    habilidades.append((partes[0], int(partes[1])))
                args = (d["nome"], d["cidade"], int(d["idade"]),
                        [g.strip() for g in d["generos"].split(",") if g.strip()], habilidades)
                self.cadastro.criarMusico(*args) if id is None else self.cadastro.atualizarMusico(id, *args)
            elif tipo == "Bandas":
                args = (d["nome"], d["cidade"], d["estilo"])
                self.cadastro.criarBanda(*args) if id is None else self.cadastro.atualizarBanda(id, *args)
            else:
                args = (d["instrumento"], int(d["nivel"]), d["requisitos"])
                if id is None:
                    self.cadastro.criarVaga(int(d["banda_id"]), *args)
                else:
                    if int(d["banda_id"]) != self.cadastro.vagas[id].banda.id:
                        raise ValueError("Para mudar a banda de uma vaga, exclua-a e crie uma nova.")
                    self.cadastro.atualizarVaga(id, *args)
        self.gravar(operacao)

    def vincular(self, adicionar):
        def operacao():
            banda = self.cadastro.bandas[int(self.vinculos["banda"].get())]
            musico = self.cadastro.musicos[int(self.vinculos["musico"].get())]
            banda.adicionarIntegrante(musico) if adicionar else banda.removerIntegrante(musico)
        self.gravar(operacao)

    def buscar(self):
        self.resultados.delete(*self.resultados.get_children())
        try:
            m = self.cadastro.musicos[int(self.filtros["musico"].get())]
            busca = Busca(self.filtros["cidade"].get(), self.filtros["instrumento"].get(), self.filtros["genero"].get())
            vagas = busca.executar(m, self.cadastro.vagas.values())
        except (ValueError, KeyError):
            messagebox.showerror("Busca", "Informe um ID de músico válido, disponível na aba Músicos.")
            return
        for v in vagas:
            self.resultados.insert("", "end", values=(v.banda.nome, v.banda.cidade, v.banda.estilo,
                v.instrumento, v.nivelMinimo, v.requisitos))
        self.status.set(f"{len(vagas)} oportunidade(s) encontrada(s).")


def main():
    janela = tk.Tk()
    janela.withdraw()
    try:
        cadastro = Cadastro.carregar(ARQUIVO)
    except (OSError, ValueError, KeyError, TypeError) as erro:
        messagebox.showerror("Arquivo de dados inválido", f"O arquivo foi preservado. Verifique {ARQUIVO}\n\n{erro}")
        janela.destroy()
        return
    Aplicacao(janela, cadastro)
    janela.deiconify()
    janela.mainloop()


if __name__ == "__main__":
    main()

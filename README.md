# Timbre — Projeto Completo (Etapas 1, 2 e 3)

**Grupo 16:** Iago Boettge · Marcus Vinicius Rodrigues de Jesus · Samuel Almeida Giacomelli · Fernanda Silva Bettanin  
**Repositório Remoto:** [https://github.com/IagoBoettge/Timbre](https://github.com/IagoBoettge/Timbre)

Aplicação em Python + Tkinter para conectar músicos e bandas locais por vagas compatíveis.

## Documentação para Entrega (05/11)

- **Documento Consolidado (Etapas 1, 2 e 3 + Diagramas UML + CRUD + Prints + Testes):**
  - Word (`.docx`): [`Entrega-Final-Documentacao-Timbre-Grupo16.docx`](Entrega-Final-Documentacao-Timbre-Grupo16.docx) / [`TIMBRE.docx`](TIMBRE.docx)
  - PDF (`.pdf`): [`Entrega-Final-Documentacao-Timbre-Grupo16.pdf`](Entrega-Final-Documentacao-Timbre-Grupo16.pdf)
  - Markdown: [`README (1).md`](README%20(1).md) / [`doc/README.md`](doc/README.md)
- **Documentos Individuais das Etapas:**
  - Etapa 1 (Proposta): [`Etapa-1-Proposta.pdf`](Etapa-1-Proposta.pdf)
  - Etapa 2 (Modelagem UML e Dicionário): [`Diagrama UML - Grupo 16.docx`](Diagrama%20UML%20-%20Grupo%2016.docx) / [`Etapa-2-UML.pdf`](Etapa-2-UML.pdf) / [`Etapa-2-UML.png`](Etapa-2-UML.png)
  - Etapa 3 (Diagrama UML Atualizado): [`Etapa-3-UML-Atualizado.png`](Etapa-3-UML-Atualizado.png)

## Executar

Use Python 3.10 ou superior com Tkinter disponível (verificado em Python 3.12.14 com Tk 8.6). Nenhum pacote de terceiros é necessário.

```bash
python3 app.py
```

No Windows, utilize `python app.py` ou `py app.py`.

A aplicação grava os cadastros em `data/timbre.json`, ao lado do código, após cada alteração.

## Como usar

1. Na aba **Músicos**, informe nome, cidade, idade, gêneros separados por vírgula e habilidades no formato `guitarra:2;bateria:1`. Clique em **Criar**. Os níveis são `1` (iniciante), `2` (intermediário) e `3` (avançado).
2. Na aba **Bandas**, cadastre nome, cidade e estilo. Observe o ID gerado na lista.
3. Na aba **Vagas**, informe o ID da banda, instrumento, nível mínimo e requisitos. Clique em **Criar**.
4. Em **Buscar oportunidades**, informe o ID do músico e os filtros desejados. Filtros vazios permitem qualquer cidade, instrumento ou gênero; compatibilidade de instrumento/nível e vaga aberta são sempre exigidas.
5. Selecione um registro nas listas para carregar os campos e atualizar ou excluir. A aba **Integrantes** permite vincular e remover músicos de uma banda usando os IDs.

Excluir uma banda também exclui suas vagas. Excluir um músico remove seus vínculos com as bandas. Encerrar/reabrir uma vaga altera somente seu estado.

## Demonstração e Testes

```bash
python3 demo.py
python3 -m unittest discover -s . -p "test_*.py" -v
```

A demonstração usa dados fictícios e arquivo temporário; não altera os cadastros da interface. Todos os **19 testes automatizados** passaram (`OK`).

## Arquivos de Código

- `modelo.py`: classes de domínio (`Perfil`, `HabilidadeMusical`, `Musico`, `Banda`, `Vaga`, `Busca`), herança, polimorfismo, encapsulamento e regras de compatibilidade.
- `dados.py`: classe `Cadastro` (CRUD em memória, integridade de vínculos e persistência JSON atômica).
- `app.py`: classe `Aplicacao` (interface gráfica Tkinter com 5 abas).
- `demo.py`: roteiro de demonstração pelo terminal.
- `test_timbre.py`: suíte de 19 testes unitários automatizados (`unittest`).

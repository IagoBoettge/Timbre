# Timbre — base funcional para a Etapa 3

Projeto do Grupo 16: conectar músicos e bandas locais por vagas compatíveis.

Esta é uma implementação inicial produzida a partir da proposta e do UML recebidos. Está disponível neste pacote local e ainda precisa ser integrada ao repositório da equipe: https://github.com/IagoBoettge/Timbre.

## Executar

Use Python 3.10 ou superior com Tkinter disponível. A versão verificada neste ambiente foi Python 3.12.14, com Tk 8.6. Nenhum pacote de terceiros é necessário.

Na pasta que contém este arquivo:

```text
python app.py
```

No Windows, se o comando disponível for o lançador `py`, use `py app.py`.

A aplicação grava os cadastros em `data/timbre.json`, ao lado do código, após cada alteração. Não execute duas instâncias simultaneamente sobre o mesmo arquivo. Se o arquivo estiver inválido, a inicialização mostra uma mensagem e o preserva; faça uma cópia antes de corrigir os dados.

## Como usar

1. Na aba **Músicos**, informe nome, cidade, idade, gêneros separados por vírgula e habilidades no formato `guitarra:2;bateria:1`. Clique em **Criar**. Os níveis são 1 (iniciante), 2 (intermediário) e 3 (avançado).
2. Na aba **Bandas**, cadastre nome, cidade e estilo. Observe o ID gerado na lista.
3. Na aba **Vagas**, informe o ID da banda, instrumento, nível mínimo e requisitos. Clique em **Criar**.
4. Em **Buscar oportunidades**, informe o ID do músico e os filtros desejados. Filtros vazios permitem qualquer cidade, instrumento ou gênero; compatibilidade de instrumento/nível e vaga aberta são sempre exigidas.
5. Selecione um registro nas listas para carregar os campos e atualizar ou excluir. A aba **Integrantes** permite vincular e remover músicos de uma banda usando os IDs.

Excluir uma banda também exclui suas vagas. Excluir um músico remove seus vínculos com as bandas. Encerrar/reabrir uma vaga altera somente seu estado.

## Demonstração e testes

```text
python demo.py
python -m unittest discover -s tests -v
```

A demonstração usa dados fictícios e arquivo temporário; não altera os cadastros da interface. Os 19 testes automatizados passaram. A interface foi importada sem erro; sua interação visual ainda precisa ser revisada.

## Arquivos

- `modelo.py`: classes de domínio, herança, polimorfismo e regras de compatibilidade.
- `dados.py`: CRUD, relações e persistência JSON.
- `app.py`: interface Tkinter.
- `demo.py`: demonstração pelo terminal.
- `tests/test_timbre.py`: testes automatizados.
- [doc/README.md](doc/README.md): documentação atualizada da Etapa 3, anexos e resultados.

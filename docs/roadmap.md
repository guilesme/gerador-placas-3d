# Roadmap

Este roadmap organiza a evolucao do projeto em fases pequenas e recuperaveis.

## Fase 0 - Governanca e Baseline

Objetivo: documentar o processo antes de alterar comportamento.

Tarefas:

- criar documentacao de governanca;
- criar rastreador de bugs/fixes;
- criar estrategia de testes;
- criar changelog inicial;
- decidir se os relatorios externos entram no repositorio;
- criar tag `v0.1.0` como baseline funcional.

Status: em planejamento.

## Fase 1 - Estabilidade e Seguranca Basica

Objetivo: corrigir bugs de baixo risco sem mudar o produto.

Itens:

- `BUG-001`: escapar texto no preview HTML;
- `BUG-002`: usar `BLENDER_PATH`;
- `BUG-003`: remover progress bar falsa;
- `BUG-004`: melhorar tratamento de excecoes;
- `BUG-005`: separar validacao entre errors e warnings;
- `BUG-007`: corrigir fallback de output.

Release alvo: `v0.1.1`.

## Fase 2 - Testabilidade

Objetivo: criar cobertura minima para evitar regressao.

Itens:

- extrair validacao para modulo puro;
- criar `requirements-dev.txt`;
- adicionar `pytest`;
- testar validacao;
- testar escape HTML/XML;
- testar estrutura do exportador 3MF com mocks.

Release alvo: `v0.1.2`.

## Fase 3 - Documentacao Publica e GitHub

Objetivo: melhorar a apresentacao do projeto.

Itens:

- revisar `README.md`;
- corrigir encoding/mojibake;
- adicionar screenshots;
- adicionar badges;
- adicionar secao de troubleshooting;
- adicionar exemplos de entrada/saida;
- criar GitHub Releases.

Release alvo: `v0.1.3`.

## Fase 4 - Configurabilidade

Objetivo: tornar o projeto reutilizavel sem editar codigo.

Itens:

- `IMP-001`: nome do condominio configuravel;
- configurar texto de rodape;
- configurar cores/material slots;
- configurar limites de fonte;
- separar especificacao atual de especificacao futura.
- padronizar filamentos, cores e vinculo automatico do texto ao material correto no Bambu Studio.

Release alvo: `v0.2.0`.

## Fase 5 - Qualidade do 3MF e UX

Objetivo: melhorar confiabilidade do arquivo gerado e experiencia do usuario.

Itens:

- validar `.3mf` gerado automaticamente;
- melhorar mensagens de erro do Blender;
- adicionar logs baixaveis;
- adicionar preview mais fiel;
- avaliar render preview estatico via Blender;
- documentar compatibilidade com Bambu Studio.

Release alvo: `v0.3.0`.

## Fase 6 - Produto Maduro

Objetivo: preparar `v1.0.0`.

Itens:

- fluxo de build Docker validado;
- suite minima de testes;
- release checklist estavel;
- README completo;
- tags e changelog consistentes;
- bugs criticos zerados;
- guia de contribuicao atualizado;
- screenshots e exemplos reais.

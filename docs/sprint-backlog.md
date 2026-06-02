# Backlog de Proximas Sprints

Este documento consolida as pendencias de desenvolvimento que devem ser puxadas nas proximas sprints. Ele complementa o [rastreador de bugs e fixes](bug-and-fix-tracker.md) e o [roadmap](roadmap.md), mantendo foco em ordem pratica de execucao.

Estado atual em 2026-06-02:

- branch atual `codex/imp-001-rodape-configuravel` sincronizada com o GitHub;
- sem issues abertas no GitHub;
- sem pull requests abertos no GitHub;
- suite local `python -m unittest discover -s tests -v` passando com 18 testes;
- nenhuma pendencia critica aberta no rastreador.

## Sprint 1 - Fechamento do Fluxo Bambu

Objetivo: reduzir o ajuste manual no Bambu Studio e tentar levar `IMP-003` de `Fixed` para `Verified`.

Itens:

- `IMP-005`: investigar preenchimento automatico dos filamentos no Bambu Studio;
- comparar um `.3mf` gerado pela aplicacao com um `.3mf` salvo pelo Bambu Studio apos selecao manual correta dos filamentos;
- identificar arquivos extras, chaves de `Metadata/model_settings.config`, presets internos, referencias de AMS ou metadados de projeto usados pelo Bambu Studio;
- decidir se o preenchimento automatico completo e viavel ou se o ajuste manual deve permanecer documentado como comportamento aceito;
- atualizar `IMP-003` para `Verified` somente se o arquivo abrir no Bambu Studio com os dois filamentos selecionados corretamente.

Validacao esperada:

- gerar `.3mf` no Docker;
- abrir no Bambu Studio;
- confirmar dois filamentos listados;
- confirmar base no material 1 e texto no material 2;
- confirmar se os filamentos PETG marrom/branco aparecem selecionados sem intervencao manual;
- registrar resultado em `docs/verification-log.md`.

## Sprint 2 - Performance e Pequena Manutencao

Objetivo: melhorar performance sem alterar comportamento visual da placa.

Itens:

- `IMP-002`: avaliar busca binaria em `calculate_font_size()`;
- medir se a otimizacao traz ganho real no fluxo atual;
- manter compatibilidade com os limites de texto existentes;
- adicionar ou ajustar testes unitarios para evitar regressao de tamanho/validacao.

Validacao esperada:

- `python -m py_compile src/web/app.py src/web/validation.py src/web/plate_service.py src/blender/generator.py src/blender/threemf_exporter.py`;
- `python -m unittest discover -s tests -v`;
- geracao real no Docker apenas se a mudanca tocar o calculo usado pelo Blender.

## Sprint 3 - Documentacao Publica e Release

Objetivo: deixar o projeto mais apresentavel e recuperavel no GitHub.

Itens:

- adicionar screenshots reais da UI e, se possivel, exemplo visual da placa gerada;
- adicionar badges relevantes ao `README.md`;
- adicionar secao de troubleshooting para Docker, Blender, Bambu Studio e permissoes locais;
- adicionar exemplos de entrada/saida;
- criar GitHub Release para o estado estavel mais recente;
- revisar se o roadmap curto do `README.md` continua alinhado ao estado real.

Validacao esperada:

- revisar links internos da documentacao;
- conferir se o README representa corretamente o fluxo oficial via Docker;
- garantir que o changelog e a tag/release contem a mesma historia.

## Sprint 4 - Qualidade 3MF e UX

Objetivo: melhorar confiabilidade do arquivo gerado e experiencia operacional.

Itens:

- validar automaticamente a estrutura do `.3mf` gerado quando possivel;
- melhorar mensagens de erro do Blender quando houver falha de geracao;
- avaliar logs baixaveis pela interface;
- avaliar preview mais fiel da placa;
- avaliar render estatico via Blender como preview opcional;
- documentar compatibilidade conhecida com Bambu Studio.

Validacao esperada:

- testes unitarios para novas funcoes puras;
- geracao real pelo Docker;
- abertura manual no Bambu Studio quando a mudanca afetar metadados ou geometria.

## Criterios de Priorizacao

Priorizar primeiro:

- itens que reduzem retrabalho manual no Bambu Studio;
- itens que tornam o fluxo de impressao mais previsivel;
- documentacao que evita duvida operacional recorrente;
- melhorias pequenas com validacao automatizada clara.

Evitar puxar na mesma sprint:

- mudancas no exportador 3MF e mudancas grandes de UI;
- alteracoes de geometria e alteracoes de metadados Bambu sem validacao manual;
- refatores amplos sem ganho direto para o fluxo atual.

## Rotina ao Iniciar uma Sprint

1. Criar branch com prefixo `codex/` e nome do item principal.
2. Mudar o item correspondente em `docs/bug-and-fix-tracker.md` para `In Progress`.
3. Implementar a menor mudanca verificavel.
4. Rodar testes locais.
5. Registrar validacoes em `docs/verification-log.md`.
6. Atualizar `CHANGELOG.md`.
7. Mudar o item para `Fixed` ou `Verified`, conforme o nivel real de validacao.

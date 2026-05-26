# Governanca de Desenvolvimento

Este documento define como o projeto deve evoluir sem perder estabilidade, rastreabilidade e clareza para manutencao.

## Principios

1. O estado funcional atual deve ser preservado como baseline.
2. Toda mudanca relevante deve ter um motivo rastreavel: bug, melhoria, feature ou manutencao.
3. Bugs e fixes devem ter identificadores estaveis, por exemplo `BUG-001` e `FIX-001`.
4. Mudancas pequenas devem ser preferidas a grandes reescritas.
5. Releases devem ser recuperaveis por tags Git.
6. Testes devem crescer junto com o risco da mudanca.
7. Documentacao deve ser atualizada junto com a alteracao, nao depois.

## Fluxo de Trabalho

### 1. Baseline

O estado atual, que funciona para o uso principal, deve virar uma tag:

```bash
git tag -a v0.1.0 -m "Baseline funcional inicial"
git push origin v0.1.0
```

Essa tag permite voltar ao ponto estavel caso uma melhoria quebre o fluxo.

### 2. Branches

Usar branches curtas e descritivas:

```text
fix/bug-001-preview-html-escape
fix/bug-002-blender-path
feat/configurable-footer
chore/docs-governance
test/smoke-exporter
```

Evitar trabalhar diretamente em `main`, exceto para ajustes muito pequenos de documentacao e somente quando nao houver risco.

### 3. Commits

Usar Conventional Commits:

```text
fix: corrige uso de BLENDER_PATH no subprocesso
feat: adiciona nome do condominio configuravel
test: adiciona smoke tests do exportador 3MF
docs: documenta estrategia de releases
chore: atualiza .gitignore
refactor: extrai validacao de texto para modulo puro
```

Quando o commit resolver um item rastreado, mencionar o ID:

```text
fix: escapa texto do preview HTML

Resolve: BUG-001
```

### 4. Pull Requests

Mesmo em projeto pessoal, PRs ajudam a visibilidade no GitHub. Cada PR deve conter:

- objetivo da mudanca;
- bugs/fixes relacionados;
- screenshots ou exemplos quando houver UI;
- testes executados;
- risco de regressao;
- plano de rollback.

### 5. Revisao Antes de Merge

Antes de mergear na `main`:

- `python -m py_compile` deve passar;
- smoke tests devem passar quando existirem;
- se mexer em geracao 3D, gerar pelo menos uma placa de teste;
- se mexer em UI, validar a tela manualmente;
- atualizar `CHANGELOG.md`;
- atualizar `docs/bug-and-fix-tracker.md` quando aplicavel.

## Politica de Estabilidade

### `main`

`main` deve representar o estado utilizavel do projeto.

### Tags

Cada versao estavel deve ter tag:

```text
v0.1.0
v0.1.1
v0.2.0
v1.0.0
```

### Rollback

Se uma versao nova quebrar o fluxo atual:

```bash
git switch main
git checkout v0.1.0
```

Ou criar uma branch a partir da tag estavel:

```bash
git switch -c hotfix/restore-from-v0.1.0 v0.1.0
```

## Tipos de Mudanca

| Tipo | Exemplo | Versao |
|---|---|---|
| Patch | bug fix, ajuste de erro, doc pequena | `0.1.0` -> `0.1.1` |
| Minor | nova feature compativel | `0.1.0` -> `0.2.0` |
| Major | quebra de fluxo ou interface | `0.x` -> `1.0.0` quando estabilizar |

## Definicao de Pronto

Uma tarefa so deve ser considerada pronta quando:

- o codigo/documentacao foi atualizado;
- o item foi marcado no rastreador;
- os testes definidos foram executados;
- o changelog foi atualizado;
- existe uma forma clara de rollback;
- o comportamento esperado foi documentado.


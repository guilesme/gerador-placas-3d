# Visibilidade no GitHub

Este documento lista melhorias para apresentar o projeto como um repositorio profissional, confiavel e facil de entender.

## Objetivo

Mostrar que o projeto:

- resolve um problema real;
- tem arquitetura clara;
- possui processo de manutencao;
- tem versionamento e changelog;
- tem testes ou plano claro de testes;
- pode evoluir sem quebrar o uso atual.

## README Publico

O `README.md` deve ser a vitrine principal.

Estrutura recomendada:

1. Nome do projeto e descricao em uma frase.
2. Screenshot ou GIF curto da interface.
3. Exemplo de placa gerada.
4. Funcionalidades principais.
5. Stack tecnica.
6. Como rodar com Docker.
7. Como gerar uma placa.
8. Estrutura do projeto.
9. Roadmap resumido.
10. Status de qualidade.
11. Licenca.

## Badges

Adicionar badges quando houver suporte real:

```markdown
![Python](https://img.shields.io/badge/python-3.10-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.30-red)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-brightgreen)
```

Quando CI existir:

```markdown
![Tests](https://github.com/<owner>/<repo>/actions/workflows/tests.yml/badge.svg)
```

## Screenshots e Midia

Criar uma pasta:

```text
docs/assets/
```

Sugestoes:

- screenshot da UI inicial;
- screenshot com texto preenchido;
- screenshot do download gerado;
- imagem do `.3mf` aberto no Bambu Studio;
- foto de uma placa impressa, quando houver.

## Templates do GitHub

Criar futuramente:

```text
.github/
  ISSUE_TEMPLATE/
    bug_report.md
    feature_request.md
  pull_request_template.md
```

### Bug Report

Campos recomendados:

- descricao;
- passos para reproduzir;
- comportamento esperado;
- comportamento atual;
- ambiente;
- logs;
- arquivo `.3mf` de exemplo, se aplicavel;
- versao/tag.

### Pull Request

Campos recomendados:

- resumo;
- bug/feature relacionada;
- tipo de mudanca;
- testes executados;
- screenshots;
- risco de regressao;
- plano de rollback.

## GitHub Actions

Criar workflow inicial quando os testes existirem:

```text
.github/workflows/tests.yml
```

Primeira etapa simples:

- checkout;
- setup Python 3.10;
- instalar dependencias;
- rodar `python -m py_compile`;
- rodar `python -m unittest discover -s tests -v`.

Blender pode ficar fora do CI inicialmente por ser pesado. Depois pode virar job opcional ou workflow manual.

## Releases

Cada release deve conter:

- resumo da versao;
- lista de bugs corrigidos;
- testes executados;
- riscos conhecidos;
- instrucoes de rollback;
- link para `CHANGELOG.md`;
- anexos ou screenshots quando fizer sentido.

## Topicos do Repositorio

Adicionar topicos no GitHub:

```text
python
streamlit
blender
3d-printing
3mf
bambu-lab
docker
automation
```

## O Que Evitar

- README desatualizado;
- releases sem changelog;
- commits grandes demais;
- fixes sem referencia a bug;
- documentacao prometendo testes que ainda nao existem;
- esconder bugs conhecidos em vez de registra-los com clareza.

## Prioridade Recomendada

1. Corrigir encoding/mojibake dos documentos existentes.
2. Reescrever README com screenshots.
3. Criar changelog e tag baseline.
4. Adicionar templates de issue e PR.
5. Criar CI basico com `py_compile`.
6. Adicionar testes unitarios e badge de CI.

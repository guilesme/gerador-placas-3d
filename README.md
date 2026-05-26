# Gerador de Placas 3D

Aplicacao em Python, Streamlit e Blender para gerar placas de sinalizacao 3D em formato `.3mf`, prontas para fluxo de impressao no Bambu Studio com suporte a multi-material/AMS.

O projeto nasceu para automatizar placas do Condominio Astro, mas esta sendo organizado para evoluir como uma ferramenta reutilizavel, versionada e bem documentada.

## Status

- Versao em desenvolvimento: `0.1.1-dev`
- Baseline funcional preservada: `v0.1.0`
- Branch de estabilidade atual: `codex/v0.1.1-stability`
- Testes automatizados iniciais: `unittest`
- CI planejado/adicionado: GitHub Actions para compilacao Python e testes unitarios

## Funcionalidades

- Interface web simples com Streamlit.
- Geracao procedural de placa 3D via Blender headless.
- Exportacao `.3mf` com estrutura compativel com Bambu Studio.
- Separacao de objetos para uso de dois materiais: base e texto.
- Texto principal com suporte a multiplas linhas.
- Ajuste de tamanho de fonte e alinhamento.
- Rodape fixo da placa.
- Area de output local para download do arquivo gerado.

## Stack

- Python 3.10
- Streamlit 1.30
- Blender 4.0.2
- Docker / Docker Compose
- Formato 3MF

## Como Rodar com Docker

```bash
docker compose up --build
```

Depois acesse:

```text
http://localhost:8501
```

## Como Rodar Localmente

Instale as dependencias Python:

```bash
python -m pip install -r requirements.txt
```

Garanta que o Blender esta instalado e acessivel pelo `PATH`, ou defina:

```bash
BLENDER_PATH=/caminho/para/blender
```

Execute:

```bash
streamlit run src/web/app.py
```

## Testes

Validacao de sintaxe:

```bash
python -m py_compile src/web/app.py src/web/validation.py src/blender/generator.py src/blender/threemf_exporter.py
```

Testes automatizados:

```bash
python -m unittest discover -s tests -v
```

Observacao: os testes atuais nao exigem Blender. A geracao real de `.3mf` ainda deve ser validada manualmente ou em ambiente com Blender instalado.

## Estrutura

```text
assets/
  fonts/
    Roboto-Bold.ttf
src/
  blender/
    generator.py
    threemf_exporter.py
  web/
    app.py
    validation.py
tests/
docs/
output/
```

## Documentacao

A documentacao tecnica e de manutencao fica em [docs/README.md](docs/README.md).

Pontos principais:

- [Governanca de Desenvolvimento](docs/development-governance.md)
- [Versionamento e Releases](docs/versioning-and-releases.md)
- [Rastreador de Bugs e Fixes](docs/bug-and-fix-tracker.md)
- [Estrategia de Testes](docs/testing-strategy.md)
- [Roadmap](docs/roadmap.md)
- [Checklist de Release](docs/release-checklist.md)

## Versionamento

O projeto usa tags Git para preservar estados estaveis.

Baseline atual:

```text
v0.1.0
```

Proxima versao planejada:

```text
v0.1.1
```

## Roadmap Curto

- Finalizar fixes de estabilidade de `v0.1.1`.
- Validar fluxo real com Blender.
- Melhorar README com screenshots.
- Corrigir divergencias entre `spec.md` e implementacao.
- Tornar nome do condominio e rodape configuraveis.
- Expandir testes do exportador 3MF.

## Licenca

Este projeto esta licenciado sob a licenca MIT. Veja [LICENSE](LICENSE).

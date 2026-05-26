# Contribuindo para o Gerador de Placas 3D

Obrigado pelo interesse em contribuir.

Este projeto usa um fluxo simples, mas com rastreabilidade: bugs, melhorias, testes e releases devem ficar documentados.

## Fluxo Recomendado

1. Abra ou identifique um item em [docs/bug-and-fix-tracker.md](docs/bug-and-fix-tracker.md).
2. Crie uma branch curta e descritiva.
3. Implemente a mudança com escopo pequeno.
4. Rode os testes.
5. Atualize documentação e changelog quando necessário.
6. Abra um Pull Request.

## Branches

Use nomes como:

```text
fix/bug-001-preview-html
feat/configurable-footer
test/exporter-smoke
docs/readme-screenshots
```

## Commits

Use Conventional Commits:

```text
fix: corrige escape do preview HTML
feat: adiciona nome do condominio configuravel
test: adiciona testes do exportador 3MF
docs: atualiza estrategia de releases
```

Quando possível, referencie o item rastreado:

```text
Resolve: BUG-001
```

## Testes

Antes de abrir PR, rode:

```bash
python -m py_compile src/web/app.py src/web/validation.py src/web/plate_service.py src/blender/generator.py src/blender/threemf_exporter.py
python -m unittest discover -s tests -v
```

Se a mudança envolver Docker:

```bash
docker compose config --quiet
```

Se a mudança envolver geração 3D, valide manualmente:

- gerar uma placa;
- baixar o `.3mf`;
- abrir/importar no Bambu Studio quando possível.

## Pull Requests

Todo PR deve informar:

- objetivo;
- bug/feature relacionada;
- testes executados;
- risco de regressão;
- plano de rollback;
- screenshots quando houver mudança visual.

## Documentação

Atualize estes arquivos quando aplicável:

- [CHANGELOG.md](CHANGELOG.md)
- [docs/bug-and-fix-tracker.md](docs/bug-and-fix-tracker.md)
- [docs/verification-log.md](docs/verification-log.md)
- [spec.md](spec.md)

## Código

- Preserve o comportamento funcional atual, exceto quando a mudança for intencional.
- Prefira alterações pequenas e testáveis.
- Não misture refatoração grande com bug fix pequeno.
- Para lógica testável, prefira módulos puros fora da UI Streamlit.


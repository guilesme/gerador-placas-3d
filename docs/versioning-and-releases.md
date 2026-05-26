# Versionamento e Releases

Este projeto deve usar Semantic Versioning adaptado ao seu estagio atual.

Formato:

```text
MAJOR.MINOR.PATCH
```

Exemplo:

```text
v0.1.0
v0.1.1
v0.2.0
v1.0.0
```

## Estrategia Recomendada

### `v0.1.0` - Baseline funcional

Representa o estado atual da aplicacao: funcional para gerar placas 3D no fluxo conhecido.

Essa versao nao precisa significar "codigo perfeito"; significa "ponto estavel conhecido".

### `v0.1.x` - Correcoes sem mudar o produto

Usar para:

- corrigir bugs;
- melhorar mensagens de erro;
- adicionar testes;
- corrigir documentacao;
- melhorar seguranca sem alterar UX principal.

Exemplos:

```text
v0.1.1: corrige BLENDER_PATH e progress bar falsa
v0.1.2: adiciona smoke tests e valida rollback
```

### `v0.2.0` - Melhorias de produto

Usar para features pequenas e compativeis:

- nome do condominio configuravel;
- configuracao de rodape;
- melhorias de preview;
- opcoes adicionais de alinhamento;
- presets de placa.

### `v1.0.0` - Versao publica madura

Usar quando:

- fluxo principal estiver coberto por testes;
- documentacao estiver revisada;
- releases e tags estiverem organizadas;
- uso via Docker estiver confiavel;
- houver instrucoes claras de instalacao e troubleshooting.

## Changelog

O arquivo `CHANGELOG.md` deve seguir este padrao:

```markdown
## [0.1.1] - 2026-05-26

### Fixed
- Corrige uso de BLENDER_PATH no subprocesso. (`BUG-002`)

### Changed
- Remove barra de progresso falsa durante geracao. (`BUG-003`)

### Tests
- Adiciona teste de smoke do exportador 3MF.
```

Categorias recomendadas:

- `Added`
- `Changed`
- `Fixed`
- `Security`
- `Tests`
- `Docs`
- `Deprecated`
- `Removed`

## Tags Git

Criar tag anotada para cada release:

```bash
git tag -a v0.1.1 -m "Release v0.1.1"
git push origin v0.1.1
```

Conferir tags:

```bash
git tag --list
```

Voltar para uma versao:

```bash
git checkout v0.1.0
```

## Releases no GitHub

Para melhorar visibilidade, cada tag estavel deve virar uma GitHub Release contendo:

- resumo da versao;
- bugs corrigidos;
- features adicionadas;
- instrucoes de upgrade;
- riscos conhecidos;
- link para o changelog;
- screenshots quando houver mudanca visual.

## Politica de Compatibilidade

Enquanto o projeto estiver em `0.x`, mudancas ainda podem evoluir com alguma liberdade. Mesmo assim, toda mudanca que possa quebrar o uso atual deve:

- ser descrita no changelog;
- ter rollback documentado;
- idealmente ficar atras de configuracao ou branch ate estabilizar.


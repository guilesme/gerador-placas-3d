# Versionamento e Releases

Este projeto deve usar Semantic Versioning adaptado ao seu estagio atual.

Formato:

```text
MAJOR.MINOR.PATCH
```

Exemplo:

```text
v1.1.0
v1.1.1
v1.2.0
v2.0.0
```

## Estrategia Recomendada

### `v1.1.0` - Baseline funcional

Representa o estado atual da aplicacao: funcional para gerar placas 3D no fluxo conhecido.

Essa versao nao precisa significar "codigo perfeito"; significa "ponto estavel conhecido".

### `v1.1.x` - Correções sem mudar o produto

Usar para:

- corrigir bugs;
- melhorar mensagens de erro;
- adicionar testes;
- corrigir documentacao;
- melhorar seguranca sem alterar UX principal.

Exemplos:

```text
v1.1.1: corrige a configuração do Bambu Studio e adiciona o corte espelhado
v1.1.2: adiciona smoke tests e valida rollback
```

### `v1.2.0` - Melhorias de produto

Usar para features pequenas e compativeis:

- nome do condominio configuravel;
- configuracao de rodape;
- melhorias de preview;
- opcoes adicionais de alinhamento;
- presets de placa.

### `v2.0.0` - Próxima grande evolução do produto

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
git tag -a v1.1.1 -m "Release v1.1.1"
git push origin v1.1.1
```

Conferir tags:

```bash
git tag --list
```

Voltar para uma versao:

```bash
git checkout v1.1.0
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

Na linha estável `1.x`, mudanças compatíveis incrementam a versão menor ou de correção. Toda mudança que possa quebrar o uso atual deve:

- ser descrita no changelog;
- ter rollback documentado;
- idealmente ficar atras de configuracao ou branch ate estabilizar.


# Changelog

Todas as mudancas relevantes deste projeto devem ser documentadas aqui.

O formato segue a ideia de [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) e o versionamento deve seguir Semantic Versioning.

## [Unreleased]

### Docs

- Adiciona documentacao de governanca, versionamento, testes, roadmap e release.
- Adiciona rastreador inicial de bugs e melhorias baseado nas revisoes tecnicas.

### Added

- Padroniza perfis PETG Bambu no `.3mf` gerado, com filamentos marrom/branco usados no fluxo validado. (`IMP-003`)
- Adiciona opcao de tamanho da placa entre padrao `200 x 180 mm` e reduzida `200 x 128 mm`. (`IMP-004`)

### Changed

- Atualiza documentacao publica, especificacao e rastreador para a proxima versao `0.2.0-dev`.

## [0.1.1] - 2026-05-27

### Docs

- Adiciona documentacao de governanca, versionamento, testes, roadmap e release.
- Adiciona rastreador inicial de bugs e melhorias baseado nas revisoes tecnicas.

### Added

- Extrai validacao de texto para modulo puro `src/web/validation.py`.
- Extrai chamada ao Blender para modulo puro `src/web/plate_service.py`.
- Adiciona testes automatizados com `unittest` para validacao de texto e exportador 3MF. (`BUG-011`)
- Adiciona workflow de CI no GitHub Actions para compilacao Python e testes unitarios.
- Adiciona templates de bug report, feature request e pull request para GitHub.
- Documenta perfil validado de materiais/filamentos Bambu para futura `IMP-003`.

### Fixed

- Escapa texto do usuario antes de renderizar o preview HTML. (`BUG-001`)
- Usa `BLENDER_PATH` para localizar o executavel do Blender. (`BUG-002`)
- Remove barra de progresso falsa durante geracao. (`BUG-003`)
- Trata timeout, Blender ausente e erros de sistema com mensagens especificas. (`BUG-004`)
- Separa validacao em erros bloqueantes e avisos nao bloqueantes. (`BUG-005`)
- Remove fallback absoluto `/app/output/placa.3mf` do gerador Blender. (`BUG-007`)
- Escapa valores de atributos XML em `model_settings.config` do exportador 3MF. (`BUG-008`)
- Remove atributo `version` obsoleto do `docker-compose.yml`. (`BUG-010`)
- Controla logs de debug do Blender/exportador por `LOG_LEVEL`. (`BUG-009`)
- Atualiza `spec.md` para refletir o comportamento atual validado. (`BUG-006`)
- Atualiza `CONTRIBUTING.md` para o fluxo atual de governanca, testes e PRs. (`BUG-012`)
- Anota `docs/revisao-antigravity.md` como registro historico para evitar confusao com o estado atual. (`BUG-012`)

### Changed

- Reescreve o `README.md` publico da raiz com status, uso, testes, documentacao e roadmap curto.

### Planned

- Criar tag `v0.1.0` para marcar a baseline funcional atual.
- Corrigir bugs de estabilidade planejados para `v0.1.1`.
- Padronizar filamentos, cores e vinculo automatico do texto ao segundo material em release futura. (`IMP-003`)

## [0.1.0] - A definir

### Added

- Baseline funcional da aplicacao de geracao de placas 3D.
- Interface Streamlit para entrada de texto e download do `.3mf`.
- Geracao procedural de placa com Blender.
- Exportador 3MF compativel com fluxo Bambu Studio/AMS.

### Known Issues

- Preview HTML ainda precisa escapar entrada do usuario. (`BUG-001`)
- `BLENDER_PATH` e configurado no Docker mas ignorado pelo app. (`BUG-002`)
- Barra de progresso durante geracao e enganosa. (`BUG-003`)
- Tratamento de erros do subprocesso ainda e generico. (`BUG-004`)
- Validacao ainda nao separa erros bloqueantes de avisos. (`BUG-005`)
- `spec.md` e codigo divergem em fonte, rodape e timeout. (`BUG-006`)

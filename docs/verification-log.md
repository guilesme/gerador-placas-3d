# Log de Verificacao

Este arquivo registra validacoes executadas durante o desenvolvimento.

Status:

- `Pass`: validacao passou.
- `Fail`: validacao falhou.
- `Blocked`: nao foi possivel executar no ambiente atual.
- `Pending`: ainda nao executado.

## 2026-05-26 - Fixes iniciais `v0.1.1`

Branch: `codex/v0.1.1-stability`

Baseline preservada:

```text
v0.1.0
```

### Validacoes executadas

| Validacao | Status | Observacao |
|---|---|---|
| Criar tag local `v0.1.0` | Pass | Tag criada para preservar baseline funcional atual. |
| Criar branch `codex/v0.1.1-stability` | Pass | Branch criada a partir da baseline atual. |
| `python -m py_compile src/web/app.py src/blender/generator.py src/blender/threemf_exporter.py` | Pass | Sintaxe Python validada. |
| `python -m py_compile src/web/app.py src/web/validation.py src/web/plate_service.py src/blender/generator.py src/blender/threemf_exporter.py tests/test_validation.py tests/test_threemf_exporter.py tests/test_plate_service.py` | Pass | Sintaxe dos novos modulos e testes validada. |
| `python -m unittest discover -s tests -v` | Pass | 13 testes executados com sucesso. |
| UI no Docker em `http://127.0.0.1:8501` | Pass | App abriu no navegador interno apos reiniciar o container. |
| Preview com `<b>Teste</b> & Sala` | Pass | Texto apareceu como literal, nao como HTML renderizado; botao ficou desabilitado por erro de validacao. |
| Geracao real no Docker com `Portaria Principal` | Pass | Placa gerada com sucesso e botao de download `.3mf` exibido. |
| `docker compose config --quiet` | Pass | Configuracao valida sem warning de `version` obsoleto. |
| Abertura do `placa_astro_20260526_065248.3mf` no Bambu Studio | Pass | Usuario confirmou que o arquivo abriu aparentemente correto. |
| Atualizacao de `spec.md` | Pass | Spec alinhada ao comportamento atual validado em vez da versao inicial divergente. |
| Nova rodada `python -m unittest discover -s tests -v` apos BUG-009/BUG-006 | Pass | 13 testes executados com sucesso. |
| Nova rodada `docker compose config --quiet` apos `LOG_LEVEL` | Pass | Configuracao valida. |
| Revisao de encoding/documentacao publica | Pass | `README.md`, `spec.md` e `CONTRIBUTING.md` foram atualizados; `docs/revisao-antigravity.md` foi marcado como historico. |

### Validacoes pendentes

| Validacao | Status | Motivo |
|---|---|---|
| Rodar geracao real com Blender local | Blocked | `blender` nao esta disponivel no PATH local desta sessao. |
| Testar `BLENDER_PATH` invalido pela UI | Pass | Validado por teste automatizado em `tests/test_plate_service.py`. |
| Vinculo automatico do texto ao segundo filamento | Pending | Usuario precisou adicionar segunda cor e vincular `Text` manualmente. Registrado como `IMP-003`. |

### Itens corrigidos nesta leva

- `BUG-001`: escape de texto no preview HTML.
- `BUG-002`: uso de `BLENDER_PATH`.
- `BUG-003`: remocao da progress bar falsa.
- `BUG-004`: tratamento especifico de excecoes no subprocesso.
- `BUG-005`: validacao com erros bloqueantes e warnings.
- `BUG-007`: fallback de output relativo ao projeto.
- `BUG-008`: escape de atributos XML no exportador 3MF.
- `BUG-009`: logs de debug controlados por `LOG_LEVEL`.
- `BUG-006`: especificacao atualizada para refletir valores atuais validados.
- `BUG-012`: documentacao publica revisada e revisao antiga marcada como historica.
- `BUG-011`: testes automatizados iniciais e CI basico.
- `BUG-010`: remocao do atributo `version` obsoleto do Compose.

### Observacoes de validacao manual

- O `.3mf` gerado em `placa_astro_20260526_065248.3mf` abriu no Bambu Studio.
- Ajuste manual observado: foi necessario adicionar uma segunda cor/filamento e vincular o objeto `Text` a essa segunda cor.
- Isso nao bloqueia a geracao atual, mas vira melhoria futura para reduzir configuracao manual no Bambu Studio.

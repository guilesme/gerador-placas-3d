# Rastreador de Bugs e Fixes

Este arquivo acompanha bugs, riscos e melhorias tecnicas identificadas no projeto.

Status possiveis:

- `Open`: identificado, ainda nao corrigido.
- `Planned`: aceito e planejado.
- `In Progress`: em implementacao.
- `Fixed`: corrigido no codigo.
- `Verified`: corrigido e validado por teste/manual.
- `Won't Fix`: decidido nao corrigir.
- `Needs Decision`: depende de decisao de produto.

Severidade:

- `High`: risco de quebra, seguranca, perda de arquivo ou uso bloqueado.
- `Medium`: problema real com contorno conhecido.
- `Low`: melhoria, manutencao ou risco pequeno.

## Bugs e Melhorias Rastreadas

| ID | Severidade | Status | Area | Titulo | Origem | Versao alvo |
|---|---|---|---|---|---|---|
| BUG-001 | High | Verified | Web UI | Texto do usuario entra no preview HTML sem escape | Revisao Codex | v0.1.1 |
| BUG-002 | Medium | Verified | Web/Runtime | `BLENDER_PATH` e configurado no Docker mas ignorado pelo app | Relatorios + Revisao Codex | v0.1.1 |
| BUG-003 | Medium | Verified | Web UX | Barra de progresso falsa congela durante geracao | Relatorios + Revisao Codex | v0.1.1 |
| BUG-004 | Medium | Verified | Web/Errors | Tratamento generico de excecoes em `generate_plate()` | Relatorios + Revisao Codex | v0.1.1 |
| BUG-005 | Medium | Verified | Validation | Validacao avisa mas nao bloqueia entrada problematica | Relatorios + Revisao Codex | v0.1.1 |
| BUG-006 | Medium | Verified | Product Spec | Divergencia entre `spec.md` e codigo sobre fonte, rodape e timeout | Revisao Codex | v0.1.1 |
| BUG-007 | Medium | Verified | Blender CLI | Fallback de output usa caminho absoluto de Docker | Relatorios + Revisao Codex | v0.1.1 |
| BUG-008 | Medium | Verified | 3MF Export | XML gerado por concatenacao manual de strings | Relatorios + Revisao Codex | v0.1.1 |
| BUG-009 | Low | Verified | Logging | `DEBUG=True` fixo em producao | Relatorio LLM | v0.1.1 |
| BUG-010 | Low | Verified | Docker | `docker-compose.yml` usa `version` deprecated | Relatorio LLM | v0.1.1 |
| BUG-011 | Medium | Verified | Tests | Projeto nao possui testes automatizados | Relatorios + Revisao Codex | v0.1.2 |
| BUG-012 | Low | Verified | Docs | Documentos aparentam mojibake/encoding quebrado no ambiente atual | Revisao Codex | v0.1.1 |
| IMP-001 | Medium | Planned | Product | Tornar nome do condominio configuravel | Relatorios + Revisao Codex | v0.2.0 |
| IMP-002 | Low | Planned | Performance | Avaliar busca binaria em `calculate_font_size()` | Plano LLM | v0.2.0 |
| IMP-003 | Medium | Planned | 3MF/Bambu | Padronizar filamentos, cores e vinculo automatico do texto ao segundo material | Validacao manual | v0.2.0 |
| IMP-004 | Medium | Verified | Product/Web/Blender | Suportar placa reduzida 200 x 128mm alem da padrao 200 x 180mm | Implementacao urgente | v0.2.0 |

## Detalhamento

### BUG-001 - Texto do usuario entra no preview HTML sem escape

Problema: `src/web/app.py` monta HTML com `unsafe_allow_html=True` usando `text_input` diretamente.

Risco: injecao de HTML/JS no preview local, quebra visual da UI e comportamento inesperado.

Fix proposto:

- usar `html.escape()` em todo texto de usuario antes de inserir em HTML;
- escapar tambem textos vindos de variaveis de ambiente, como futuro `CONDO_NAME`;
- manter quebras de linha convertidas para `<br>` somente depois do escape.

Validacao:

- testar entrada com `<b>Teste</b>`;
- testar entrada com `A & B`;
- confirmar que aparece como texto literal no preview.

### BUG-002 - `BLENDER_PATH` ignorado

Problema: `docker-compose.yml` define `BLENDER_PATH`, mas o app chama `"blender"` diretamente.

Fix proposto:

- criar constante `BLENDER_BIN = os.environ.get("BLENDER_PATH", "blender")`;
- usar `BLENDER_BIN` no comando do subprocesso;
- melhorar mensagem quando o executavel nao for encontrado.

Validacao:

- `python -m py_compile`;
- teste manual com `BLENDER_PATH` invalido e mensagem amigavel;
- teste no Docker com caminho real.

### BUG-003 - Progress bar falsa

Problema: a barra vai rapidamente ate 50%, trava e so depois pula para 100%.

Fix proposto:

- remover `st.progress()` enquanto nao houver progresso real;
- usar `st.spinner()` com mensagem clara.

Validacao:

- gerar placa e confirmar que nao ha barra enganosa.

### BUG-004 - Tratamento generico de excecoes

Problema: `except Exception as e` reduz a qualidade do diagnostico.

Fix proposto:

- tratar `subprocess.TimeoutExpired`;
- tratar `FileNotFoundError`;
- tratar `OSError`;
- preservar stdout/stderr do Blender no erro de retorno diferente de zero.

Validacao:

- simular Blender inexistente;
- simular timeout em teste unitario com mock futuramente.

### BUG-005 - Validacao nao bloqueia entrada problematica

Problema: warnings aparecem, mas geracao continua.

Fix proposto:

- refatorar `validate_text()` para retornar `errors` e `warnings`;
- desabilitar botao quando houver erros;
- manter warnings nao bloqueantes para legibilidade.

Observacao:

Nao usar bloqueio de `<`, `>`, `&` como substituto para escape. Primeiro corrigir escape de HTML/XML.

### BUG-006 - Divergencia entre `spec.md` e codigo

Problema: especificacao e implementacao discordam em limites e defaults.

Decisao pendente:

- seguir a `spec.md` atual;
- atualizar a `spec.md` para refletir o comportamento atual;
- criar nova especificacao `v0.2`.

Campos divergentes:

- fonte principal: spec 14mm, codigo 20/40mm;
- rodape: spec 6mm, codigo 8mm;
- margem Y do rodape: spec 10mm, codigo 12mm;
- timeout: spec 120s, codigo 180s.

### BUG-007 - Fallback de output hardcoded

Problema: `generator.py` usa `/app/output/placa.3mf` quando nao recebe output.

Fix proposto:

- usar caminho relativo a raiz do projeto;
- criar pasta `output/` se necessario;
- manter compatibilidade com argumento explicito vindo do app.

### BUG-008 - XML por concatenacao manual

Problema: exportador 3MF monta XML por strings.

Fix proposto:

- curto prazo: escapar corretamente atributos e textos variaveis;
- medio prazo: avaliar migracao para `xml.etree.ElementTree`.

Validacao:

- parsear XML gerado com `xml.etree.ElementTree`;
- abrir `.3mf` em Bambu Studio;
- testar nomes/metadados com caracteres especiais.

### BUG-011 - Sem testes automatizados

Problema: nao ha suite de testes.

Fix proposto:

- extrair validacao para modulo puro;
- criar testes para validacao;
- criar smoke tests para funcoes puras do exportador;
- criar teste de estrutura ZIP do `.3mf`;
- manter teste com Blender como manual ou CI opcional, pois depende de binario pesado.

### IMP-003 - Padronizar filamentos, cores e vinculo do texto

Contexto: o arquivo `placa_astro_20260526_065248.3mf` foi aberto no Bambu Studio com sucesso, mas foi necessario adicionar uma segunda cor na lista de filamentos e vincular manualmente o objeto/texto ao segundo filamento.

Objetivo:

- abrir o `.3mf` ja com dois filamentos padronizados;
- manter base vinculada ao material 1;
- manter texto vinculado ao material 2;
- reduzir ajustes manuais no Bambu Studio;
- aproximar o arquivo gerado do perfil final usado em producao.

Entrada util para implementacao futura:

- `.gcode` de uma placa finalizada com cores/configuracoes corretas;
- idealmente tambem um `.3mf` salvo pelo Bambu Studio depois de ajustar os filamentos manualmente, pois o `.3mf` preserva metadados de projeto com mais fidelidade do que o G-code final.
- referencia tecnica consolidada em [material-profile-reference.md](material-profile-reference.md).

Validacao:

- abrir arquivo gerado no Bambu Studio;
- confirmar que ha dois filamentos listados;
- confirmar que o objeto `Texto` ja esta vinculado ao segundo filamento;
- confirmar que o slice usa as cores/material slots esperados.

### IMP-004 - Suportar placa reduzida 200 x 128mm

Contexto: foi adicionada uma feature urgente para permitir gerar a placa tambem em altura reduzida, mantendo a largura de 200mm, espessura, relevo, rodape e fluxo de exportacao.

Implementacao:

- UI Streamlit passa a oferecer seletor entre `Padrao (180 mm)` e `Reduzida (128 mm)`;
- `plate_service.generate_plate()` repassa a altura selecionada para o Blender;
- `generator.py` aceita `plate_height` pela CLI e normaliza para alturas oficiais;
- area vertical disponivel para texto passa a ser calculada conforme a altura da placa;
- runtime oficial permanece Docker; o app usa `BLENDER_PATH` quando definido no ambiente e fallback `blender` dentro do proprio ambiente de execucao.

Validacao:

- `python -m py_compile` dos modulos principais e testes;
- `python -m unittest discover -s tests -v`;
- teste unitario garante que a altura reduzida e enviada ao comando Blender;
- validacao local manual informada pelo usuario antes do registro.

## Como Atualizar Este Arquivo

Ao iniciar uma correcao:

1. mudar `Status` para `In Progress`;
2. criar branch com o ID no nome;
3. implementar;
4. registrar testes executados;
5. mudar para `Fixed`;
6. apos validacao, mudar para `Verified`;
7. atualizar `CHANGELOG.md`.

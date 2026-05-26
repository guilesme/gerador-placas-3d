# Revisao Tecnica da Branch codex/v0.1.1-stability

> Nota de manutencao: esta revisao e um registro historico gerado durante o desenvolvimento.
> Algumas pendencias citadas abaixo foram resolvidas depois da revisao.
> A fonte atual de verdade e [bug-and-fix-tracker.md](bug-and-fix-tracker.md),
> [verification-log.md](verification-log.md) e [CHANGELOG.md](../CHANGELOG.md).

Revisado por: Antigravity (Google DeepMind)
Data: 2026-05-26
Branch analisada: `codex/v0.1.1-stability`
Baseline: `main` (commit `85684df`)

---

## Contexto

Esta revisao avalia o trabalho realizado na branch `codex/v0.1.1-stability` em relacao
ao projeto `gerador-placas-3d`. A analise cobre todos os arquivos modificados, os novos
arquivos criados e os itens que permaneceram pendentes.

Os pontos de referencia usados foram:
- `relatorio_projeto.md` (analise previa)
- `plano_correcoes.md` (plano previa)
- `avaliacao_relatorios_llm.md` (auto-avaliacao da branch)
- Leitura direta do codigo atual
- Execucao dos testes: `python -m unittest discover -s tests -v`

---

## Veredito Geral

O trabalho e tecnicamente solido. A decisao de extrair validacao para um modulo puro
(`src/web/validation.py`) antes de criar testes foi a escolha certa e mais pragmatica
do que o plano original propunha.

Os 9 testes passam sem erro no estado atual da branch.

Entretanto, ha pendencias importantes que precisam ser resolvidas antes de fazer merge
para `main`.

---

## O Que Foi Implementado Corretamente

### BUG-001 - Escape HTML no preview (VERIFICADO)

`src/web/app.py` agora usa `html.escape()` em todo texto do usuario antes de montar
o HTML do preview. Isso inclui o tratamento correto da ordem das operacoes:
primeiro escapa, depois substitui `\n` por `<br>`.

Codigo atual (linhas 376-382):

```python
title_html = f"<div style='text-align: center;'>{html.escape(lines[0])}</div>"
rest_html = "<br>".join(html.escape(line) for line in lines[1:]) ...
safe_text = html.escape(text_input).replace(chr(10), '<br>')
```

Status: CORRETO.

---

### BUG-002 - BLENDER_PATH usado corretamente (VERIFICADO)

`BLENDER_BIN = os.environ.get("BLENDER_PATH", "blender")` foi adicionado como
constante de modulo e usado no comando do subprocesso.

Status: CORRETO.

---

### BUG-003 - Progress bar falsa removida (VERIFICADO)

O loop `for i in range(50): progress.progress(i + 1)` foi removido. Agora usa
apenas `st.spinner()` com mensagem honesta.

Status: CORRETO.

---

### BUG-004 - Tratamento especifico de excecoes (VERIFICADO)

`generate_plate()` agora trata:
- `subprocess.TimeoutExpired`
- `FileNotFoundError`
- `OSError`
- `Exception` generico como catch-all final com tipo identificado

Timeout reduzido de 180s para 120s, alinhado com a `spec.md`.

Status: CORRETO.

---

### BUG-005 - Validacao bloqueante separada de warnings (VERIFICADO)

`src/web/validation.py` retorna `(errors, warnings)`. O botao de geracao esta
desabilitado quando `validation_errors` e nao-vazio.

Status: CORRETO.

---

### BUG-007 - Fallback de output em generator.py (VERIFICADO)

```python
default_output = Path(__file__).parent.parent.parent / "output" / "placa.3mf"
default_output.parent.mkdir(exist_ok=True, parents=True)
output = argv[1] if len(argv) > 1 else str(default_output)
```

Substituiu o caminho absoluto `/app/output/placa.3mf` por caminho relativo a raiz
do projeto.

Status: CORRETO.

---

### BUG-011 - Testes automatizados criados (VERIFICADO)

9 testes passando:
- `tests/test_validation.py`: 4 testes de `validate_text()`
- `tests/test_threemf_exporter.py`: 5 testes de funcoes puras do exportador

A decisao de usar `unittest` da stdlib em vez de `pytest` foi adequada.

Status: VERIFICADO (executado e confirmado).

---

## Pendencias que Precisam ser Resolvidas

### PENDENCIA 1 - BUG-008: XML por concatenacao sem escape (CRITICO)

**Arquivo:** `src/blender/threemf_exporter.py`
**Status no rastreador:** Open, alvo v0.1.2
**Por que e urgente agora:** A `validation.py` foi configurada para PERMITIR os
caracteres `&`, `'`, `"` na entrada do usuario (linha 5):

```python
UNSUPPORTED_TEXT_CHARS = re.compile(r'[^\w\s\.,\-\!\?\&\'\":;/\(\)\u00C0-\u00FF]')
```

Isso e conceitualmente correto -- esses caracteres devem ser permitidos no texto
da placa desde que sejam escapados antes de entrar no XML. Porem, o exportador
**nao foi alterado** e ainda usa interpolacao direta:

```python
# threemf_exporter.py linha 149 -- VULNERAVEL
f'      <metadata key="name" value="{obj_data["name"]}"/>'
```

**Cenario de falha concreto:**
- Usuario digita: `Portao & Guarita`
- `validation.py` permite (correto por design)
- `build_model_settings()` gera: `value="Portao & Guarita"`
- XML invalido: `&` sem escape em atributo XML corrompe o arquivo `.3mf`
- Bambu Studio rejeita ou falha ao importar

**O que precisa ser feito:**

1. Adicionar import no topo de `threemf_exporter.py`:

```python
from xml.sax.saxutils import escape, quoteattr
```

2. Na funcao `build_model_settings()`, linha 149, substituir:

```python
# ANTES (vulneravel):
f'      <metadata key="name" value="{obj_data["name"]}"/>'

# DEPOIS (correto):
f'      <metadata key="name" value={quoteattr(obj_data["name"])}/>',
```

Nota tecnica: usar `quoteattr()` e nao `escape()` para valores de atributos.
`quoteattr()` adiciona as aspas automaticamente E escapa todos os caracteres
especiais dentro do valor, incluindo `"`, `'`, `&`, `<`, `>`.

3. Verificar se ha outros locais no arquivo onde texto variavel e interpolado
em atributos XML. Na leitura atual, o unico ponto de risco real com texto de
usuario e `obj_data["name"]` em `build_model_settings()`. Os demais campos
(UUIDs, inteiros, valores estaticos) sao seguros.

4. Adicionar teste para este caso em `tests/test_threemf_exporter.py`:

```python
def test_model_settings_escapes_special_chars_in_name(self):
    """Verifica que & < > " no nome do objeto nao corrompem o XML."""
    data = [
        {
            "id": 1,
            "uuid": "aaaaaaaa-0000-0000-0000-000000000001",
            "comp_uuid": "bbbbbbbb-0000-0000-0000-000000000001",
            "name": "Portao & Guarita <Teste>",
            "extruder": 1,
            "vertices": [],
            "triangles": [],
            "face_count": 0,
        }
    ]
    xml_text = threemf_exporter.build_model_settings(data, assembly_id=60)

    # O XML deve ser parseavel -- se & nao foi escapado, isso levanta ParseError
    root = ET.fromstring(xml_text)
    self.assertEqual(root.tag, "config")

    # O valor original deve ser recuperavel apos parse
    parts = root.findall(".//part")
    self.assertEqual(len(parts), 1)
    name_meta = parts[0].find("metadata[@key='name']")
    self.assertEqual(name_meta.get("value"), "Portao & Guarita <Teste>")
```

Este teste FALHARA no estado atual (antes da correcao) e PASSARA depois.

---

### PENDENCIA 2 - BUG-006: Decisao sobre spec.md vs codigo (AGUARDANDO PRODUTO)

**Status no rastreador:** Needs Decision
**Nao e um bug de codigo** -- e uma divergencia entre a especificacao escrita e
o comportamento implementado.

Campos divergentes entre `spec.md` e o codigo atual:

| Campo | spec.md | Codigo atual |
|---|---|---|
| Fonte principal padrao | 14mm | 20mm |
| Auto-scale maximo | 14mm | 20mm |
| Auto-scale minimo | 5mm | 5mm |
| Slider maximo | nao especificado | 40mm |
| Tamanho do rodape | 6mm | 8mm |
| Offset Y do rodape | 10mm | 12mm |
| Timeout subprocesso | 120s | agora 120s (corrigido) |

**Acao necessaria:** O responsavel pelo produto precisa decidir uma das opcoes:

1. A `spec.md` e a fonte da verdade -- nesse caso, o codigo precisa ser ajustado
   para 14mm de padrao, rodape de 6mm e offset de 10mm.

2. O comportamento atual e o correto -- nesse caso, a `spec.md` deve ser atualizada
   para refletir o que o codigo faz (20mm, 8mm, 12mm). Esta opcao e mais segura
   se o comportamento atual ja foi validado manualmente com sucesso.

3. Criar uma nova especificacao `v0.2` e manter a `spec.md` atual como registro
   historico.

**Recomendacao:** Optar pela opcao 2 (atualizar a `spec.md`) se as placas geradas
com os valores atuais estao sendo aprovadas visualmente. Mudar parametros geometricos
sem validacao fisica da impressao e arriscado.

---

### PENDENCIA 3 - DEBUG=True fixo em producao (BUG-009, BAIXA PRIORIDADE)

**Arquivo:** `src/blender/threemf_exporter.py`, linha 16
**Codigo atual:** `DEBUG = True`

Em producao, isso gera saida verbosa no stdout do container a cada exportacao.
Nao e critico, mas polui os logs.

**Correcao proposta:**
```python
# threemf_exporter.py linha 16
DEBUG = os.environ.get("LOG_LEVEL", "INFO").upper() == "DEBUG"
```

Mesma logica ja implementada ou prevista para `generator.py`.
Adicionar `LOG_LEVEL=INFO` na secao `environment` do `docker-compose.yml`.

---

### PENDENCIA 4 - version deprecated no docker-compose.yml (BUG-010, BAIXA PRIORIDADE)

**Arquivo:** `docker-compose.yml`, linha 1
**Codigo atual:** `version: '3.8'`

Deprecated no Docker Compose v2+. Causa warning na saida de `docker compose up`.

**Correcao proposta:** Remover a linha `version: '3.8'` inteiramente. O Docker
Compose v2 nao precisa dela.

Aproveitar para adicionar as variaveis de ambiente documentadas no CHANGELOG:

```yaml
services:
  app:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./output:/app/output
      - ./assets:/app/assets
      - ./src:/app/src
    environment:
      - BLENDER_PATH=/opt/blender/blender
      - LOG_LEVEL=INFO
    restart: unless-stopped
```

---

### PENDENCIA 5 - CONDO_NAME nao configuravel (IMP-001, PLANEJADO v0.2)

O nome "Condominio Astro" ainda aparece hardcoded em:
- `src/web/app.py` linha 390: `Condominio Astro` no preview HTML
- `src/blender/generator.py` linha 34: `FOOTER_TEXT = "Condominio Astro"`

O rastreador marca isso como `IMP-001 / Planned / v0.2.0`, o que e aceitavel
dado que nao e um bug, mas uma melhoria de produto.

Quando for implementar:
1. Em `generator.py`: `FOOTER_TEXT = os.environ.get("CONDO_NAME", "Condominio Astro")`
2. Em `app.py`: `CONDO_NAME = os.environ.get("CONDO_NAME", "Condominio Astro")`
   e usar a variavel no preview HTML (com `html.escape(CONDO_NAME)`)
3. Passar `CONDO_NAME` explicitamente como argumento CLI para o Blender OU garantir
   que o subprocesso herda as variaveis de ambiente do processo pai (o comportamento
   padrao do `subprocess.run` sem `env=` explicito).
4. Adicionar `CONDO_NAME=Condominio Astro` no `docker-compose.yml` para documentar
   o valor padrao.

---

## Pontos de Atencao Adicionais

### README.md sem acentuacao

O novo `README.md` foi escrito sem acentos para evitar problemas de encoding
(BUG-012). A intencao e valida, mas o resultado e visualmente pobre para um
README publico no GitHub. Quando BUG-012 for resolvido, revisar a acentuacao.

### Teste de escape ausente nos testes do exportador

Os testes atuais de `test_threemf_exporter.py` usam apenas nomes seguros
("Placa", "Texto"). Nao ha teste que verifique o comportamento com caracteres
especiais. Isso precisa ser adicionado como parte da resolucao de BUG-008
(veja codigo do teste na Pendencia 1 acima).

### Arquivo de saida de teste nao ignorado pelo git

`tests/test_threemf_exporter.py` cria `output/test_unittest_export.3mf` durante
o teste (linha 87). Esse arquivo cai no `output/` que ja esta no `.gitignore`,
entao nao vira para o repositorio. Sem problema.

---

## Ordem de Execucao Recomendada

1. **Resolver BUG-008** (Pendencia 1) -- unica pendencia que representa risco
   real no estado atual da branch. Os outros itens sao melhorias.

2. **Atualizar `spec.md`** conforme decisao de produto sobre BUG-006.

3. **Resolver BUG-009 e BUG-010** juntos (um commit no `threemf_exporter.py` e
   um commit no `docker-compose.yml`).

4. Fazer merge de `codex/v0.1.1-stability` para `main` e criar tag `v0.1.1`.

5. IMP-001 (CONDO_NAME) e os itens de Fase 3 (docs, screenshots) ficam para
   branches futuras.

---

## Verificacao Final Antes do Merge

Apos resolver as pendencias, executar:

```bash
# Validacao de sintaxe
python -m py_compile src/web/app.py src/web/validation.py src/blender/generator.py src/blender/threemf_exporter.py

# Testes automatizados
python -m unittest discover -s tests -v

# Verificar git status
git status
git diff main --stat
```

Resultado esperado dos testes apos BUG-008 corrigido:

```
test_combined_model_is_parseable_xml ... ok
test_export_creates_required_3mf_entries ... ok
test_filament_settings_are_valid_json ... ok
test_main_model_is_parseable_xml ... ok
test_model_settings_contains_extruder_metadata ... ok
test_model_settings_escapes_special_chars_in_name ... ok  <- NOVO
test_common_punctuation_is_allowed ... ok
test_emoji_returns_blocking_error ... ok
test_long_text_returns_warning ... ok
test_valid_text_has_no_errors_or_warnings ... ok
----------------------------------------------------------------------
Ran 10 tests in X.XXXs
OK
```

---

*Revisao realizada em 2026-05-26 sobre o estado da branch codex/v0.1.1-stability.*

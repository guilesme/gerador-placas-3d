# 🛠️ Plano de Correções Técnicas — Gerador de Placas 3D

> **Baseado em:** `relatorio_projeto.md` — análise de 25/05/2026
> **Destino:** Execução por agente de código (sem interação humana necessária)
> **Repositório local:** `c:\Users\bigus\Documents\Projects\gerador-placas-3d`
> **Branch de trabalho:** Criar branch `fix/code-quality` a partir de `main` antes de qualquer alteração

---

## ⚙️ Instruções de Execução para o Agente

1. **Criar branch de trabalho** antes de iniciar:
   ```bash
   git checkout -b fix/code-quality
   ```
2. Aplicar as correções na **ordem numérica** apresentada neste documento (há dependências entre elas).
3. Após cada grupo de arquivos alterados, **commitar** com a mensagem indicada em cada seção.
4. Ao final, **executar o smoke test** conforme seção 14.
5. Fazer `git push origin fix/code-quality` e abrir Pull Request para `main`.

---

## Ordem de Execução

| # | Severidade | Arquivo(s) | Descrição Curta |
|---|---|---|---|
| 1 | 🔴 Crítico | `threemf_exporter.py` | Escape de XML |
| 2 | 🔴 Crítico | `app.py` | Remover progress bar falsa |
| 3 | 🔴 Crítico | `app.py` | Tratar TimeoutExpired separadamente |
| 4 | 🟡 Moderado | `app.py` | Usar BLENDER_PATH do ambiente |
| 5 | 🟡 Moderado | `app.py` | Validação deve bloquear caracteres inválidos |
| 6 | 🟡 Moderado | `generator.py` + `app.py` | Tornar nome do condomínio configurável |
| 7 | 🟡 Moderado | `generator.py` | Corrigir path de saída hardcoded |
| 8 | 🟡 Moderado | `generator.py` | Mover import de `threemf_exporter` para o topo |
| 9 | 🟢 Menor | `generator.py` + `threemf_exporter.py` | DEBUG via variável de ambiente |
| 10 | 🟢 Menor | `generator.py` | Busca binária no calculate_font_size |
| 11 | 🟢 Menor | `app.py` | Limitar slider a 20mm (com aviso acima) |
| 12 | 🟢 Menor | `docker-compose.yml` | Remover `version:` deprecated |
| 13 | 🟢 Menor | `.gitignore` | Adicionar entradas faltantes |
| 14 | 🔴 Novo | `tests/test_smoke.py` (novo arquivo) | Criar testes de fumaça |

---

---

# CORREÇÃO 1 — Escape de XML no Exportador 3MF

**Severidade:** 🔴 Crítico  
**Arquivo:** `src/blender/threemf_exporter.py`  
**Linhas afetadas:** 59–98, 101–133, 136–163  
**Problema:** O texto da placa (nomes de objetos, metadados) é interpolado diretamente em strings XML via f-strings sem nenhum escape. Se o usuário digitar um texto contendo `<`, `>`, `"` ou `&`, o XML resultante estará malformado, corrompendo silenciosamente o arquivo `.3mf`. O Bambu Studio rejeitará ou falhará ao importar.

**Exemplo do bug:**
- Texto digitado: `Portão & Guarita`
- XML gerado: `<metadata name="Title">Portão & Guarita</metadata>` ← XML inválido; `&` sem escape
- Texto digitado: `A<B`
- XML gerado: `<metadata ...>A<B</metadata>` ← parser XML encerra a tag no `<`

**Solução:** Substituir toda geração XML por `xml.etree.ElementTree`. Essa biblioteca da stdlib faz escape automático de todos os caracteres especiais em valores de atributos e texto de nós. Não requer nenhuma dependência extra.

**Nota importante para o agente:** O `xml.etree.ElementTree` não suporta namespace prefixos da forma `xmlns:BambuStudio="..."` de maneira trivial. A solução mais robusta é usar `ET.register_namespace()` + `ET.tostring()`. Alternativamente, pode-se manter a geração por strings para a estrutura XML estática (namespaces, estrutura fixa) mas usar `xml.sax.saxutils.escape()` para **todos os valores variáveis** interpolados. Esta segunda abordagem é mais cirúrgica e de menor risco de regressão — **use esta abordagem**.

**Mudança no topo do arquivo — adicionar import:**

```diff
 import zipfile
 import os
 import uuid
 import datetime
 import json
+from xml.sax.saxutils import escape as xml_escape
```

**Função `build_combined_objects_model` — apenas os nomes de objeto são variáveis aqui. `obj_id` (int) e `obj_uuid` (UUID hex) são seguros. Não há mudança de risco aqui, mas adicionar escape como boa prática:**

Não há valores de texto livre de usuário nesta função — `obj_id` é inteiro e `obj_uuid` é UUID. **Sem alteração necessária aqui.**

**Função `build_main_model` — sem texto de usuário. Sem alteração necessária.**

**Função `build_model_settings` — `obj_data["name"]` pode conter texto de usuário (nome do objeto). Aplicar escape:**

```diff
     for obj_data in objects_data:
         lines.extend([
             f'    <part id="{obj_data["id"]}" subtype="normal_part">',
-            f'      <metadata key="name" value="{obj_data["name"]}"/>',
+            f'      <metadata key="name" value="{xml_escape(obj_data["name"])}"/>',
             f'      <metadata key="extruder" value="{obj_data["extruder"]}"/>',
             f'      <mesh_stat face_count="{obj_data["face_count"]}"/>',
             '    </part>',
         ])
```

**Função `build_main_model` — campo `Title` é estático ("Placa Astro"), mas tornar seguro por consistência:**

Localizar linha:
```python
' <metadata name="Title">Placa Astro</metadata>',
```
Esta string é estática, sem risco. **Sem alteração necessária.**

**Proteção mais importante: no `export()`, o `obj_info['name']` passado pelo `generator.py` é sempre `"Placa"` ou `"Texto"` — strings seguras. No entanto, o `build_model_settings` é a função que recebe `obj_data["name"]`. Adicionar escape é a proteção correta conforme acima.**

**Proteção adicional no `generator.py` — nome do arquivo de saída:**

No `app.py`, o `filename` é gerado com timestamp, sem input do usuário. Sem risco.

**Commit message após esta correção:**
```
fix: adiciona escape de XML em threemf_exporter para prevenir corrupção de 3MF
```

---

---

# CORREÇÃO 2 — Remover Progress Bar Falsa

**Severidade:** 🔴 Crítico (UX)  
**Arquivo:** `src/web/app.py`  
**Linhas afetadas:** 414–423  
**Problema:** O bloco de processamento cria uma `st.progress()` e a incrementa de 0→50 em um loop síncrono instantâneo (sem `time.sleep`). Imediatamente após, chama `generate_plate()` que bloqueia o thread por 30–180 segundos enquanto o Blender roda. Do ponto de vista do usuário: a barra vai instantaneamente para 50%, congela, e depois pula para 100% quando termina. Isso é enganoso e transmite a sensação de travamento.

**Código atual (linhas 413–423):**
```python
if generate_btn and text_input.strip():
    with st.spinner("⏳ Gerando modelo 3D... Isso pode levar alguns segundos."):
        progress = st.progress(0)
        
        for i in range(50):
            progress.progress(i + 1)
        
        success, filepath, msg = generate_plate(text_input.strip(), font_size, text_align)
        
        progress.progress(100)
        progress.empty()
```

**Código corrigido:**
```python
if generate_btn and text_input.strip():
    with st.spinner("⏳ Gerando modelo 3D... Aguarde, isso pode levar até 2 minutos."):
        success, filepath, msg = generate_plate(text_input.strip(), font_size, text_align)
```

**Explicação:** O `st.spinner()` já provê feedback visual honesto (ícone giratório + mensagem) enquanto o código bloqueia. Ele é a ferramenta correta do Streamlit para operações bloqueantes de duração desconhecida. A `st.progress()` só faz sentido quando se tem progresso real mensurável (ex: iterando sobre chunks de arquivo). Removê-la elimina o comportamento enganoso sem perda de UX — pelo contrário, melhora.

**Ajustar também a mensagem do spinner** para ser honesta com o usuário sobre o tempo esperado.

**Commit message após esta correção:**
```
fix: remove progress bar falsa e usa apenas st.spinner para feedback de geração
```

---

---

# CORREÇÃO 3 — Tratamento Específico de TimeoutExpired

**Severidade:** 🔴 Crítico (Robustez)  
**Arquivo:** `src/web/app.py`  
**Linhas afetadas:** 257–269  
**Problema:** O `except Exception as e:` captura qualquer exceção indiscriminadamente, incluindo `subprocess.TimeoutExpired`, `OSError`, `PermissionError`, `FileNotFoundError` (quando o Blender não está no PATH). Todas essas situações distintas resultam na mesma mensagem genérica `str(e)`, dificultando o diagnóstico.

**Código atual (linhas 257–269):**
```python
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        
        if result.returncode != 0:
            return False, None, result.stderr + "\n" + result.stdout
        
        if not output_path.exists() or output_path.stat().st_size < 1000:
            return False, None, "Arquivo de saída inválido"
        
        return True, output_path, "Sucesso"
        
    except Exception as e:
        return False, None, str(e)
```

**Código corrigido:**
```python
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode != 0:
            return False, None, result.stderr + "\n" + result.stdout

        if not output_path.exists() or output_path.stat().st_size < 1000:
            return False, None, "Arquivo de saída inválido ou vazio (verifique os logs do Blender)"

        return True, output_path, "Sucesso"

    except subprocess.TimeoutExpired:
        return False, None, (
            "⏰ Tempo limite atingido (120s). O Blender demorou mais do que o esperado.\n"
            "Tente um texto mais curto ou reinicie a aplicação."
        )
    except FileNotFoundError:
        blender_bin = os.environ.get("BLENDER_PATH", "blender")
        return False, None, (
            f"❌ Executável do Blender não encontrado: '{blender_bin}'.\n"
            "Verifique se o Blender está instalado e acessível no PATH, "
            "ou defina a variável de ambiente BLENDER_PATH com o caminho completo."
        )
    except OSError as e:
        return False, None, f"Erro de sistema ao executar o Blender: {e}"
    except Exception as e:
        return False, None, f"Erro inesperado: {type(e).__name__}: {e}"
```

**Notas para o agente:**
- O timeout foi reduzido de `180` para `120` segundos, alinhando com o valor definido no `spec.md` (seção 4: "Timeout: 120 segundos").
- O `FileNotFoundError` é lançado pelo `subprocess.run` quando o executável (`cmd[0]`) não existe no sistema.
- O `OSError` cobre outros erros de I/O como falta de permissão para criar o processo.
- O `except Exception` final permanece como catch-all para erros genuinamente inesperados, mas agora identifica o tipo.

**Commit message após esta correção:**
```
fix: tratamento específico de TimeoutExpired, FileNotFoundError e OSError em generate_plate
```

---

---

# CORREÇÃO 4 — Usar BLENDER_PATH do Ambiente

**Severidade:** 🟡 Moderado  
**Arquivo:** `src/web/app.py`  
**Linhas afetadas:** 240–255  
**Problema:** `cmd[0]` é sempre a string literal `"blender"`, ignorando a variável de ambiente `BLENDER_PATH` que já está definida no `docker-compose.yml` como `/opt/blender/blender`. Isso causa inconsistência: o Docker Compose prepara o ambiente corretamente, mas o código não o utiliza.

**Adição de import no topo do arquivo** (já existe `import os`, verificar se está presente):

`os` já está importado na linha 8 do `app.py`. Sem necessidade de adicionar.

**Código atual (linhas 240–255):**
```python
def generate_plate(text, font_size, align="CENTER"):
    """Gera a placa"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"placa_astro_{timestamp}.3mf"
    output_path = OUTPUT_DIR / filename
    
    cmd = [
        "blender",
        "--background",
        "--python", str(GENERATOR_SCRIPT),
        "--",
        text,
        str(output_path),
        str(font_size),  # Novo parâmetro
        align           # Parâmetro de alinhamento
    ]
```

**Código corrigido:**
```python
# Constante no topo da seção de caminhos (após as linhas 214-222, antes da função validate_text)
BLENDER_BIN = os.environ.get("BLENDER_PATH", "blender")


def generate_plate(text, font_size, align="CENTER"):
    """Gera a placa"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"placa_astro_{timestamp}.3mf"
    output_path = OUTPUT_DIR / filename

    cmd = [
        BLENDER_BIN,
        "--background",
        "--python", str(GENERATOR_SCRIPT),
        "--",
        text,
        str(output_path),
        str(font_size),
        align
    ]
```

**Onde inserir `BLENDER_BIN`:** Adicionar após a linha 222 (`OUTPUT_DIR.mkdir(exist_ok=True, parents=True)`), antes da definição da função `validate_text` (linha 225). Deve ficar junto ao bloco de constantes de caminhos.

**Commit message:** Incluir junto ao commit da Correção 3 (mesma área de código):
```
fix: usar BLENDER_PATH do ambiente em vez de 'blender' hardcoded
```

---

---

# CORREÇÃO 5 — Validação Deve Bloquear Caracteres Inválidos

**Severidade:** 🟡 Moderado  
**Arquivo:** `src/web/app.py`  
**Linhas afetadas:** 225–237, 358–362  
**Problema:** A função `validate_text()` detecta caracteres problemáticos mas retorna apenas avisos que são exibidos visualmente. O botão de geração permanece habilitado e a geração prossegue normalmente. Caracteres como `<`, `>`, `&`, `"` causam corrupção XML (agora mitigada pela Correção 1) e caracteres fora do charset da Roboto Bold geram falha silenciosa de rendering no Blender.

**Solução:** Separar os problemas em dois tipos:
- **`errors`** (bloqueantes): caracteres XML perigosos (`<`, `>`, `&`, `"`) — bloquear geração
- **`warnings`** (informativos): texto longo, caracteres Unicode não-ASCII — apenas avisar

**Código atual da função `validate_text` (linhas 225–237):**
```python
def validate_text(text):
    """Valida o texto"""
    issues = []
    
    # Caracteres não suportados
    if re.search(r'[^\w\s\.,\-\!\?\u00C0-\u00FF]', text):
        issues.append("Alguns caracteres especiais podem não renderizar corretamente")
    
    # Texto muito longo
    if len(text) > 100:
        issues.append("Texto muito longo pode ficar ilegível")
    
    return issues
```

**Código corrigido:**
```python
# Conjunto de caracteres XML que corrompem o arquivo 3MF
_XML_DANGEROUS = re.compile(r'[<>&"\']')

def validate_text(text):
    """
    Valida o texto de entrada.
    Retorna (errors, warnings) onde:
      - errors: lista de strings com problemas bloqueantes
      - warnings: lista de strings com avisos não-bloqueantes
    """
    errors = []
    warnings = []

    # ERRO BLOQUEANTE: caracteres que corrompem o XML do 3MF
    if _XML_DANGEROUS.search(text):
        found = set(_XML_DANGEROUS.findall(text))
        errors.append(
            f"Caracteres inválidos detectados: {' '.join(repr(c) for c in sorted(found))}. "
            "Remova os caracteres: < > & \" '"
        )

    # AVISO: caracteres fora do range ASCII básico + Latin-1 (podem não ter glifos na Roboto Bold)
    if re.search(r'[^\x00-\xFF]', text):
        warnings.append(
            "Alguns caracteres Unicode avançados podem não renderizar corretamente na fonte Roboto Bold."
        )

    # AVISO: texto muito longo
    if len(text) > 100:
        warnings.append(
            f"Texto longo ({len(text)} caracteres). O auto-scale reduzirá a fonte para caber, "
            "podendo comprometer a legibilidade a 2m de distância."
        )

    return errors, warnings
```

**Código atual do uso da validação no layout (linhas 358–367):**
```python
    if text_input:
        # Validação
        warnings = validate_text(text_input)
        for w in warnings:
            st.markdown(f'<div class="warning-box">⚠️ {w}</div>', unsafe_allow_html=True)
        
        # Info do texto
        lines = len([l for l in text_input.split('\n') if l.strip()])
        chars = len(text_input)
        st.markdown(f"📊 **{chars}** caracteres • **{lines}** linha(s)")
```

**Código corrigido:**
```python
    if text_input:
        # Validação
        val_errors, val_warnings = validate_text(text_input)

        for e in val_errors:
            st.error(f"🚫 {e}")

        for w in val_warnings:
            st.markdown(f'<div class="warning-box">⚠️ {w}</div>', unsafe_allow_html=True)

        # Info do texto
        lines = len([l for l in text_input.split('\n') if l.strip()])
        chars = len(text_input)
        st.markdown(f"📊 **{chars}** caracteres • **{lines}** linha(s)")
```

**Também ajustar o botão para ficar desabilitado quando há erros (linha 406–410):**

```python
# Calcular has_errors antes do botão — precisamos do valor no escopo correto.
# Como o Streamlit roda de cima para baixo, val_errors pode não estar disponível
# neste ponto se text_input estiver vazio. Usar get com default:
_has_validation_errors = bool(text_input and validate_text(text_input)[0])

with col_btn2:
    generate_btn = st.button(
        "🚀 Gerar Placa 3D",
        disabled=not text_input or not text_input.strip() or _has_validation_errors,
        use_container_width=True
    )
```

**Nota:** A variável `_has_validation_errors` chama `validate_text` uma segunda vez. Para evitar duplo processamento, refatorar: calcular `val_errors, val_warnings` **antes** do bloco `with col1:` e usar session_state ou variável de módulo. Mas dado que Streamlit re-executa o script inteiro a cada interação, chamar duas vezes `validate_text` é aceitável (operação O(n) no tamanho do texto).

**Commit message:**
```
fix: validação de texto retorna erros bloqueantes e warnings separados; bloquear geração com chars inválidos
```

---

---

# CORREÇÃO 6 — Nome do Condomínio Configurável via Variável de Ambiente

**Severidade:** 🟡 Moderado  
**Arquivos:** `src/blender/generator.py` (linha 34), `src/web/app.py` (linhas 279, 388, 460)  
**Problema:** A string `"Condomínio Astro"` está hardcoded em 4 locais diferentes. Para utilizar a ferramenta em outro condomínio é necessário editar código-fonte. A solução é ler de uma variável de ambiente `CONDO_NAME` com fallback para `"Condomínio Astro"`.

---

### 6a. Mudança em `generator.py`

**Linha 34 atual:**
```python
FOOTER_TEXT = "Condomínio Astro"
```

**Linha 34 corrigida:**
```python
FOOTER_TEXT = os.environ.get("CONDO_NAME", "Condomínio Astro")
```

O `os` já está importado na linha 8 do arquivo. Sem necessidade de novo import.

---

### 6b. Mudança em `app.py`

**Adicionar constante** após as linhas de configuração de caminhos (após linha 222, antes de `validate_text`):

```python
CONDO_NAME = os.environ.get("CONDO_NAME", "Condomínio Astro")
```

**Linha 279 atual:**
```python
    <p>Condomínio Astro • Padrão oficial de sinalização</p>
```
**Linha 279 corrigida:**
```python
    <p>{CONDO_NAME} • Padrão oficial de sinalização</p>
```
Atenção: esta string está dentro de um `st.markdown(f"""...""")`. Verificar que o f-string está sendo usado (sim, está). Substituir a string literal pela variável.

**Linha 388 atual:**
```python
                Condomínio Astro
```
Esta linha está dentro de um bloco `st.markdown(f"""...""")`. Substituir por:
```python
                {CONDO_NAME}
```

**Linha 460 atual:**
```python
    <p>🏢 Gerador de Placas 3D v1.1 • Condomínio Astro</p>
```
**Linha 460 corrigida:**
```python
    <p>🏢 Gerador de Placas 3D v1.1 • {CONDO_NAME}</p>
```
Verificar que o bloco markdown usa f-string (sim, usa). Substituir a string literal.

---

### 6c. Atualizar `docker-compose.yml`

Adicionar a variável de ambiente na seção `environment`:

```yaml
    environment:
      - BLENDER_PATH=/opt/blender/blender
      - CONDO_NAME=Condomínio Astro
```

Isso documenta explicitamente o valor padrão e permite override fácil por outros operadores.

**Commit message:**
```
feat: tornar nome do condomínio configurável via variável de ambiente CONDO_NAME
```

---

---

# CORREÇÃO 7 — Corrigir Path de Saída Hardcoded no generator.py

**Severidade:** 🟡 Moderado  
**Arquivo:** `src/blender/generator.py`  
**Linha afetada:** 356  
**Problema:** O fallback para o path de output aponta para `/app/output/placa.3mf`, que é um caminho absoluto específico do container Docker. Quando o script é executado localmente (fora do Docker), esse path não existe e qualquer tentativa de usar o padrão quebra.

**Código atual (linha 355–356):**
```python
    text = argv[0]
    output = argv[1] if len(argv) > 1 else "/app/output/placa.3mf"
```

**Código corrigido:**
```python
    text = argv[0]
    # Fallback: cria output/ relativo à raiz do projeto (3 níveis acima deste script)
    _default_output = Path(__file__).parent.parent.parent / "output" / "placa.3mf"
    output = argv[1] if len(argv) > 1 else str(_default_output)
```

**Notas para o agente:**
- `__file__` = `.../src/blender/generator.py`
- `.parent` = `.../src/blender/`
- `.parent.parent` = `.../src/`
- `.parent.parent.parent` = raiz do projeto (`gerador-placas-3d/`)
- O `Path` já está importado na linha 10 do arquivo.
- Garantir que o diretório `output/` exista antes de escrever: adicionar `_default_output.parent.mkdir(exist_ok=True, parents=True)` após a definição de `_default_output`.

**Código final:**
```python
    text = argv[0]
    _default_output = Path(__file__).parent.parent.parent / "output" / "placa.3mf"
    _default_output.parent.mkdir(exist_ok=True, parents=True)
    output = argv[1] if len(argv) > 1 else str(_default_output)
```

**Commit message:**
```
fix: substituir path de saída hardcoded /app/output por path relativo ao projeto
```

---

---

# CORREÇÃO 8 — Mover Import de threemf_exporter para o Topo do Arquivo

**Severidade:** 🟡 Moderado  
**Arquivo:** `src/blender/generator.py`  
**Linhas afetadas:** 315–320  
**Problema:** O módulo `threemf_exporter` é importado dentro da função `generate_plate()`, em tempo de execução (linhas 315–320). Imports dentro de funções são um anti-pattern Python: dificultam o rastreamento de dependências, impedem detecção de `ImportError` na inicialização e confundem ferramentas de análise estática.

**Código atual (linhas 315–320):**
```python
    # 8. Exportar
    log("Exportando 3MF...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    import threemf_exporter
```

**Solução:** Mover o ajuste do `sys.path` e o import para o topo do arquivo, logo após os imports existentes (após linha 11).

**Adicionar após linha 11 (`from mathutils import Vector`):**
```python
# Garante que o diretório do script está no sys.path para importar threemf_exporter
import sys as _sys
_script_dir = os.path.dirname(os.path.abspath(__file__))
if _script_dir not in _sys.path:
    _sys.path.insert(0, _script_dir)
import threemf_exporter
```

**Nota:** `sys` já está importado na linha 9. Não usar `_sys`, usar `sys` diretamente:
```python
# Garante que o diretório deste script está no sys.path
_script_dir = os.path.dirname(os.path.abspath(__file__))
if _script_dir not in sys.path:
    sys.path.insert(0, _script_dir)
import threemf_exporter
```

**Remover as linhas 315–320 da função `generate_plate()`**, substituindo pelo simples comentário:
```python
    # 8. Exportar
    log("Exportando 3MF...")
```

O restante da função (`plate_obj = bpy.data.objects.get("Placa")` etc.) permanece inalterado.

**Commit message:**
```
refactor: mover import de threemf_exporter para o topo do arquivo generator.py
```

---

---

# CORREÇÃO 9 — DEBUG via Variável de Ambiente

**Severidade:** 🟢 Menor  
**Arquivos:** `src/blender/generator.py` (linha 39), `src/blender/threemf_exporter.py` (linha 16)  
**Problema:** `DEBUG = True` está hardcoded em ambos os módulos Blender. Em produção isso gera verbosidade desnecessária no stdout do container, poluindo os logs. Deve ser controlável via variável de ambiente.

---

### 9a. Em `generator.py`

**Linha 39 atual:**
```python
DEBUG = True
```

**Linha 39 corrigida:**
```python
DEBUG = os.environ.get("LOG_LEVEL", "INFO").upper() == "DEBUG"
```

---

### 9b. Em `threemf_exporter.py`

**Linha 16 atual:**
```python
DEBUG = True
```

**Linha 16 corrigida:**
```python
import os as _os
DEBUG = _os.environ.get("LOG_LEVEL", "INFO").upper() == "DEBUG"
```

**Nota:** `threemf_exporter.py` não importa `os` atualmente (apenas `zipfile`, `os`, `uuid`, `datetime`, `json`). Verificar: na linha 7 o import é `import os`. Então usar `os` diretamente:
```python
DEBUG = os.environ.get("LOG_LEVEL", "INFO").upper() == "DEBUG"
```

---

### 9c. Atualizar `docker-compose.yml`

Adicionar na seção `environment`:
```yaml
      - LOG_LEVEL=INFO
```

Para ativar modo debug em desenvolvimento, o operador define `LOG_LEVEL=DEBUG`.

**Commit message:**
```
fix: controlar modo DEBUG via variável de ambiente LOG_LEVEL em vez de hardcoded True
```

---

---

# CORREÇÃO 10 — Busca Binária em calculate_font_size

**Severidade:** 🟢 Menor (Performance)  
**Arquivo:** `src/blender/generator.py`  
**Linhas afetadas:** 212–234  
**Problema:** O algoritmo atual decrementa o tamanho da fonte em 1mm por iteração (`size -= 1.0`). Para um texto que só cabe com fonte de 5mm, o algoritmo faz até 15 iterações (de 20mm → 5mm). Cada iteração chama `wrap_text_to_fit()` que cria/destrói objetos Blender. Busca binária reduz para ~4 iterações.

**Código atual (linhas 212–234):**
```python
def calculate_font_size(text, font):
    """Calcula tamanho de fonte para caber na área, aplicando quebra de texto"""
    size = DEFAULT_FONT_SIZE
    best_text = text
    
    while size > MIN_FONT_SIZE:
        wrapped_text = wrap_text_to_fit(text, font, size, MAX_TEXT_WIDTH)
        lines = wrapped_text.split('\n')
        total_height = len(lines) * size * 1.3
        
        # Testa se a altura total não excede o máximo permitido
        if total_height <= MAX_TEXT_HEIGHT:
            best_text = wrapped_text
            break
            
        size -= 1.0
        
    if size <= MIN_FONT_SIZE:
        size = MIN_FONT_SIZE
        best_text = wrap_text_to_fit(text, font, size, MAX_TEXT_WIDTH)
    
    log(f"Tamanho calculado: {size}mm")
    return size, best_text
```

**Código corrigido:**
```python
def calculate_font_size(text, font):
    """
    Calcula tamanho de fonte para caber na área usando busca binária.
    Complexidade: O(log n) iterações em vez de O(n), onde n = (MAX - MIN) / step.
    """
    lo = MIN_FONT_SIZE
    hi = DEFAULT_FONT_SIZE
    best_size = MIN_FONT_SIZE
    best_text = wrap_text_to_fit(text, font, MIN_FONT_SIZE, MAX_TEXT_WIDTH)

    # Busca binária com resolução de 1mm
    while lo <= hi:
        mid = round((lo + hi) / 2)  # arredonda para inteiro (resolução 1mm)
        wrapped_text = wrap_text_to_fit(text, font, float(mid), MAX_TEXT_WIDTH)
        lines = wrapped_text.split('\n')
        total_height = len(lines) * mid * 1.3

        if total_height <= MAX_TEXT_HEIGHT:
            # mid cabe: tentar maior
            best_size = float(mid)
            best_text = wrapped_text
            lo = mid + 1
        else:
            # mid não cabe: tentar menor
            hi = mid - 1

    log(f"Tamanho calculado: {best_size}mm (busca binária em [{MIN_FONT_SIZE}, {DEFAULT_FONT_SIZE}]mm)")
    return best_size, best_text
```

**Nota sobre corretude:** A busca binária encontra o maior tamanho de fonte que ainda cabe. O resultado é idêntico ao linear, porém em ~4 iterações máximas (log2(15) ≈ 4) em vez de até 15.

**Commit message:**
```
perf: substituir busca linear por busca binária em calculate_font_size
```

---

---

# CORREÇÃO 11 — Limitar Slider de Fonte e Adicionar Aviso

**Severidade:** 🟢 Menor (UX/Conformidade com spec)  
**Arquivo:** `src/web/app.py`  
**Linhas afetadas:** 290–306  
**Problema:** O slider aceita valores até 40mm. A spec define `DEFAULT_FONT_SIZE = 20mm` e `MIN_FONT_SIZE = 5mm`. O valor máximo de 20mm já é o padrão, e valores acima disso com auto-scale desabilitado podem gerar texto que extravasa a placa. O `generator.py` não valida o tamanho contra as dimensões da placa quando `custom_font_size` é fornecido.

**Abordagem escolhida:** Manter o slider permitindo valores > 20mm (para casos especiais de textos curtos), mas exibir um aviso quando `font_size > 20` informando que textos longos podem extrapolar a área útil.

**Código atual (linhas 290–306):**
```python
    font_size = st.slider(
        "Tamanho da fonte (mm)",
        min_value=5,
        max_value=40,
        value=20,
        step=1,
        help="Ajuste o tamanho das letras do texto principal. O rodapé mantém tamanho fixo."
    )
    
    # Preview do tamanho
    size_desc = "Pequeno" if font_size < 15 else "Médio" if font_size < 25 else "Grande"
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem; background: rgba(230,126,34,0.1); border-radius: 10px;">
        <div style="font-size: 2rem; color: #e67e22;">{font_size}mm</div>
        <div style="color: rgba(255,255,255,0.6);">{size_desc}</div>
    </div>
    """, unsafe_allow_html=True)
```

**Código corrigido:**
```python
    font_size = st.slider(
        "Tamanho da fonte (mm)",
        min_value=5,
        max_value=30,
        value=20,
        step=1,
        help=(
            "Ajuste o tamanho das letras. "
            "Padrão: 20mm (máximo recomendado pela spec). "
            "Acima de 20mm, textos longos podem extrapolar a área útil da placa. "
            "O rodapé mantém tamanho fixo de 8mm."
        )
    )

    # Preview do tamanho
    if font_size <= 14:
        size_desc = "Pequeno (≤14mm)"
        size_color = "#e67e22"
    elif font_size <= 20:
        size_desc = "Padrão (spec)"
        size_color = "#2ecc71"
    else:
        size_desc = "⚠️ Acima do padrão"
        size_color = "#f39c12"

    st.markdown(f"""
    <div style="text-align: center; padding: 1rem; background: rgba(230,126,34,0.1); border-radius: 10px;">
        <div style="font-size: 2rem; color: {size_color};">{font_size}mm</div>
        <div style="color: rgba(255,255,255,0.6);">{size_desc}</div>
    </div>
    """, unsafe_allow_html=True)

    if font_size > 20:
        st.warning(
            "Fonte acima de 20mm. Para textos com mais de ~8 caracteres por linha, "
            "o texto pode extrapolar a área útil da placa (160mm × 100mm). "
            "Use apenas para textos muito curtos."
        )
```

**Commit message:**
```
feat: ajustar slider de fonte para max 30mm com aviso contextual acima de 20mm
```

---

---

# CORREÇÃO 12 — Remover `version:` Deprecated do docker-compose.yml

**Severidade:** 🟢 Menor  
**Arquivo:** `docker-compose.yml`  
**Linha afetada:** 1  
**Problema:** O atributo `version: '3.8'` no `docker-compose.yml` está deprecated no Docker Compose v2+ (Compose Spec). Sua presença causa warning na saída do `docker compose up` e será removido em versões futuras.

**Arquivo atual:**
```yaml
version: '3.8'

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
    restart: unless-stopped
```

**Arquivo corrigido** (com todas as variáveis de ambiente das Correções 6 e 9 já incluídas):
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
      - CONDO_NAME=Condomínio Astro
      - LOG_LEVEL=INFO
    restart: unless-stopped
```

**Commit message:**
```
chore: remover atributo version deprecated do docker-compose.yml; adicionar CONDO_NAME e LOG_LEVEL
```

---

---

# CORREÇÃO 13 — Atualizar .gitignore

**Severidade:** 🟢 Menor  
**Arquivo:** `.gitignore`  
**Problema:** O `.gitignore` atual falta algumas entradas comuns para projetos Python e está comentando `code_review_report.md` como `# Reports` — o que é correto mas pode ser expandido.

**Arquivo atual:**
```
# Python
__pycache__/
*.py[cod]
*$py.class
venv/
.env

# Project Output
output/
*.3mf
*.zip

# Analysis/Logs
3mf_analysis_*/

# IDE
.vscode/
.idea/

# OS
Thumbs.db
Desktop.ini
.DS_Store

# Reports
code_review_report.md
```

**Arquivo corrigido:**
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.egg-info/
dist/
build/
venv/
.venv/
env/
.env
.env.*

# Project Output
output/
*.3mf
*.zip

# Analysis/Logs
3mf_analysis_*/
*.log

# Tests
.pytest_cache/
.coverage
htmlcov/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
Thumbs.db
Desktop.ini
.DS_Store
ehthumbs.db

# Reports (gerados localmente, não versionados)
code_review_report.md
```

**Itens adicionados e por quê:**
- `.venv/`, `env/`: nomes alternativos comuns de virtualenv
- `.env.*`: variantes de arquivo de configuração local (`.env.local`, `.env.development`)
- `*.egg-info/`, `dist/`, `build/`: artefatos de build Python
- `*.log`: arquivos de log gerados
- `.pytest_cache/`, `.coverage`, `htmlcov/`: artefatos de teste (necessários para a Correção 14)
- `*.swp`, `*.swo`: arquivos temporários do Vim
- `ehthumbs.db`: arquivo de thumbnail do Windows Explorer

**Commit message:**
```
chore: expandir .gitignore com entradas para virtualenv, build, logs e testes
```

---

---

# CORREÇÃO 14 — Criar Testes de Fumaça

**Severidade:** 🔴 (Ausência total — novo arquivo)  
**Arquivo:** `tests/test_smoke.py` (criar novo), `tests/__init__.py` (criar novo)  
**Problema:** Zero testes automatizados. Regressões em qualquer módulo só são detectadas em produção. Os módulos do Blender (`generator.py`, `threemf_exporter.py`) dependem do `bpy` e não podem ser testados fora do contexto Blender. No entanto, o `threemf_exporter.py` tem funções puras que **não dependem do bpy** e podem ser testadas diretamente. O `app.py` tem a função `validate_text` que também é pura.

**Criar diretório e arquivos:**

```
tests/
├── __init__.py        (arquivo vazio)
└── test_smoke.py
```

**Conteúdo de `tests/__init__.py`:**
```python
# Pacote de testes
```

**Conteúdo de `tests/test_smoke.py`:**
```python
"""
Testes de fumaça para o Gerador de Placas 3D.

Cobre funções puras que não dependem do Blender (bpy):
  - threemf_exporter: geração de XML, conteúdo do ZIP, escape de caracteres
  - app.py: validação de texto

Execução:
    pip install pytest
    pytest tests/ -v
"""

import sys
import os
import zipfile
import json
import re
import pytest

# Adiciona o src/blender ao sys.path para importar threemf_exporter sem bpy
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'blender'))

# threemf_exporter importa 'bpy' apenas dentro de get_mesh_data(), que não será chamado nos testes.
# As funções de build_* são puras (sem bpy). O import direto funciona no ambiente de testes.
import threemf_exporter


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def sample_objects_data():
    """Dados mínimos simulando dois objetos exportados (Placa + Texto)."""
    return [
        {
            'id': 1,
            'uuid': 'aaaaaaaa-0000-0000-0000-000000000001',
            'comp_uuid': 'bbbbbbbb-0000-0000-0000-000000000001',
            'name': 'Placa',
            'extruder': 1,
            'vertices': [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)],
            'triangles': [(0, 1, 2)],
            'face_count': 1,
        },
        {
            'id': 2,
            'uuid': 'aaaaaaaa-0000-0000-0000-000000000002',
            'comp_uuid': 'bbbbbbbb-0000-0000-0000-000000000002',
            'name': 'Texto',
            'extruder': 2,
            'vertices': [(0.0, 0.0, 2.0), (0.5, 0.0, 2.0), (0.0, 0.5, 2.0)],
            'triangles': [(0, 1, 2)],
            'face_count': 1,
        },
    ]


@pytest.fixture
def sample_objects_data_special_chars():
    """Objeto com nome contendo caracteres XML perigosos."""
    return [
        {
            'id': 1,
            'uuid': 'aaaaaaaa-0000-0000-0000-000000000001',
            'comp_uuid': 'bbbbbbbb-0000-0000-0000-000000000001',
            'name': 'Placa <Especial> & "Teste"',
            'extruder': 1,
            'vertices': [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)],
            'triangles': [(0, 1, 2)],
            'face_count': 1,
        },
    ]


# ============================================================
# Testes: build_combined_objects_model
# ============================================================

class TestBuildCombinedObjectsModel:

    def test_retorna_string_xml(self, sample_objects_data):
        result = threemf_exporter.build_combined_objects_model(sample_objects_data)
        assert isinstance(result, str)
        assert result.startswith('<?xml')

    def test_contem_dois_objetos(self, sample_objects_data):
        result = threemf_exporter.build_combined_objects_model(sample_objects_data)
        # Deve haver 2 tags <object ...>
        assert result.count('<object ') == 2

    def test_contem_vertices(self, sample_objects_data):
        result = threemf_exporter.build_combined_objects_model(sample_objects_data)
        assert '<vertex ' in result

    def test_contem_triangulos(self, sample_objects_data):
        result = threemf_exporter.build_combined_objects_model(sample_objects_data)
        assert '<triangle ' in result

    def test_xml_valido(self, sample_objects_data):
        """Verifica que o XML gerado é parseável."""
        import xml.etree.ElementTree as ET
        result = threemf_exporter.build_combined_objects_model(sample_objects_data)
        # ElementTree não lida com múltiplos namespaces prefixados de forma simples,
        # mas pode ao menos verificar a estrutura básica removendo declarações problemáticas
        # Para um smoke test, verificar que não lança exceção de parsing é suficiente.
        # Adaptamos removendo a linha de declaração de namespace customizado:
        stripped = re.sub(r' xmlns[^"]*"[^"]*"', '', result)
        try:
            ET.fromstring(stripped)
        except ET.ParseError as e:
            pytest.fail(f"XML inválido gerado: {e}\n\nXML:\n{result[:500]}")


# ============================================================
# Testes: build_model_settings
# ============================================================

class TestBuildModelSettings:

    def test_retorna_xml_com_extrusora(self, sample_objects_data):
        result = threemf_exporter.build_model_settings(sample_objects_data, assembly_id=60)
        assert 'extruder' in result
        assert 'value="1"' in result
        assert 'value="2"' in result

    def test_nomes_de_objetos_presentes(self, sample_objects_data):
        result = threemf_exporter.build_model_settings(sample_objects_data, assembly_id=60)
        assert 'Placa' in result
        assert 'Texto' in result

    def test_escape_de_xml_em_nomes(self, sample_objects_data_special_chars):
        """
        TESTE CRÍTICO: Verifica que caracteres XML no nome do objeto são escapados.
        Este teste FALHARÁ antes da Correção 1 ser aplicada.
        Após a Correção 1, deve PASSAR.
        """
        result = threemf_exporter.build_model_settings(sample_objects_data_special_chars, assembly_id=60)
        # O nome contém < > & " — no XML escapado devem aparecer como entidades
        assert '&lt;' in result or '<Especial>' not in result, (
            "Caractere < não foi escapado no XML — risco de corrupção do 3MF!"
        )
        assert '&amp;' in result or '& ' not in result, (
            "Caractere & não foi escapado no XML — risco de corrupção do 3MF!"
        )


# ============================================================
# Testes: build_content_types e build_rels
# ============================================================

class TestBuildStaticXmls:

    def test_content_types_tem_model(self):
        result = threemf_exporter.build_content_types()
        assert '3dmanufacturing-3dmodel' in result

    def test_rels_tem_relacionamento(self):
        result = threemf_exporter.build_rels()
        assert 'Relationship' in result
        assert '3dmodel.model' in result


# ============================================================
# Testes: build_filament_settings
# ============================================================

class TestBuildFilamentSettings:

    def test_retorna_json_valido(self):
        result = threemf_exporter.build_filament_settings(1, "#8B4513", "PLA Brown")
        data = json.loads(result)
        assert data['name'] == 'PLA Brown'
        assert '#8B4513' in data['default_filament_colour']

    def test_campo_from_e_project(self):
        result = threemf_exporter.build_filament_settings(2, "#FFFFFF", "PLA White")
        data = json.loads(result)
        assert data['from'] == 'project'


# ============================================================
# Testes: export() — integração sem Blender (mock de get_mesh_data)
# ============================================================

class TestExport:

    def test_export_cria_arquivo_zip(self, tmp_path, sample_objects_data, monkeypatch):
        """
        Testa o fluxo completo de export() mockando get_mesh_data
        para não precisar do bpy.
        """
        # Mock de get_mesh_data para retornar dados sintéticos
        def mock_get_mesh_data(obj):
            return obj['vertices'], obj['triangles']

        monkeypatch.setattr(threemf_exporter, 'get_mesh_data', mock_get_mesh_data)

        # Ajustar objects para simular o formato que generator.py passa
        mock_objects = [
            {'obj': d, 'extruder': d['extruder'], 'name': d['name']}
            for d in sample_objects_data
        ]

        output_file = tmp_path / "test_output.3mf"
        result = threemf_exporter.export(str(output_file), mock_objects)

        assert result is not None, "export() retornou None — falha na exportação"
        assert output_file.exists(), "Arquivo .3mf não foi criado"
        assert output_file.stat().st_size > 1000, "Arquivo .3mf muito pequeno (< 1KB)"

    def test_export_zip_contem_arquivos_obrigatorios(self, tmp_path, sample_objects_data, monkeypatch):
        """Verifica que o ZIP contém todos os arquivos exigidos pelo formato 3MF."""
        def mock_get_mesh_data(obj):
            return obj['vertices'], obj['triangles']

        monkeypatch.setattr(threemf_exporter, 'get_mesh_data', mock_get_mesh_data)

        mock_objects = [
            {'obj': d, 'extruder': d['extruder'], 'name': d['name']}
            for d in sample_objects_data
        ]

        output_file = tmp_path / "test_output.3mf"
        threemf_exporter.export(str(output_file), mock_objects)

        expected_entries = [
            '[Content_Types].xml',
            '_rels/.rels',
            '3D/3dmodel.model',
            '3D/_rels/3dmodel.model.rels',
            '3D/Objects/objects.model',
            'Metadata/model_settings.config',
            'Metadata/filament_settings_1.config',
            'Metadata/filament_settings_2.config',
        ]

        with zipfile.ZipFile(str(output_file), 'r') as zf:
            names = zf.namelist()
            for entry in expected_entries:
                assert entry in names, f"Entrada obrigatória ausente no 3MF: '{entry}'"


# ============================================================
# Testes: validate_text (app.py)
# Nota: importar apenas a função, sem inicializar o Streamlit
# ============================================================

class TestValidateText:
    """
    Para testar validate_text sem importar o Streamlit completo,
    copiamos a lógica aqui ou importamos com mock do st.
    Abordagem: importar apenas a função isolada usando importlib
    com Streamlit mockado.
    """

    @pytest.fixture(autouse=True)
    def mock_streamlit(self, monkeypatch):
        """Mock mínimo do Streamlit para evitar inicialização da UI."""
        import types
        st_mock = types.ModuleType('streamlit')
        st_mock.set_page_config = lambda **kwargs: None
        st_mock.markdown = lambda *a, **kw: None
        st_mock.sidebar = types.SimpleNamespace()
        monkeypatch.setitem(sys.modules, 'streamlit', st_mock)

    def _get_validate_text(self):
        """Importa validate_text isolando o módulo app."""
        import importlib
        # Limpar cache se já importado
        if 'app' in sys.modules:
            del sys.modules['app']

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'web'))
        import app
        return app.validate_text

    def test_texto_valido_sem_erros(self):
        validate_text = self._get_validate_text()
        errors, warnings = validate_text("Portaria Principal")
        assert errors == []
        assert warnings == []

    def test_detecta_caractere_menor_que(self):
        validate_text = self._get_validate_text()
        errors, warnings = validate_text("A<B")
        assert len(errors) > 0, "Deveria detectar '<' como erro bloqueante"

    def test_detecta_ampersand(self):
        validate_text = self._get_validate_text()
        errors, warnings = validate_text("Portão & Guarita")
        assert len(errors) > 0, "Deveria detectar '&' como erro bloqueante"

    def test_texto_longo_gera_warning(self):
        validate_text = self._get_validate_text()
        long_text = "A" * 101
        errors, warnings = validate_text(long_text)
        assert errors == [], "Texto longo não deve ser erro bloqueante"
        assert len(warnings) > 0, "Texto longo deve gerar aviso"

    def test_texto_curto_valido_sem_avisos(self):
        validate_text = self._get_validate_text()
        errors, warnings = validate_text("Bloco A")
        assert errors == []
        assert warnings == []
```

**Instalar pytest** (adicionar ao `requirements.txt` como dependência de dev, ou instalar separadamente):

Adicionar ao final do `requirements.txt`:
```
pytest==8.2.0
```

**Ou criar `requirements-dev.txt` separado** (preferível — não poluir a imagem Docker de produção):

Criar novo arquivo `requirements-dev.txt`:
```
pytest==8.2.0
```

**Comando de execução:**
```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

**Resultado esperado após todas as correções:**
```
tests/test_smoke.py::TestBuildCombinedObjectsModel::test_retorna_string_xml PASSED
tests/test_smoke.py::TestBuildCombinedObjectsModel::test_contem_dois_objetos PASSED
tests/test_smoke.py::TestBuildCombinedObjectsModel::test_contem_vertices PASSED
tests/test_smoke.py::TestBuildCombinedObjectsModel::test_contem_triangulos PASSED
tests/test_smoke.py::TestBuildCombinedObjectsModel::test_xml_valido PASSED
tests/test_smoke.py::TestBuildModelSettings::test_retorna_xml_com_extrusora PASSED
tests/test_smoke.py::TestBuildModelSettings::test_nomes_de_objetos_presentes PASSED
tests/test_smoke.py::TestBuildModelSettings::test_escape_de_xml_em_nomes PASSED
tests/test_smoke.py::TestBuildStaticXmls::test_content_types_tem_model PASSED
tests/test_smoke.py::TestBuildStaticXmls::test_rels_tem_relacionamento PASSED
tests/test_smoke.py::TestBuildFilamentSettings::test_retorna_json_valido PASSED
tests/test_smoke.py::TestBuildFilamentSettings::test_campo_from_e_project PASSED
tests/test_smoke.py::TestExport::test_export_cria_arquivo_zip PASSED
tests/test_smoke.py::TestExport::test_export_zip_contem_arquivos_obrigatorios PASSED
tests/test_smoke.py::TestValidateText::test_texto_valido_sem_erros PASSED
tests/test_smoke.py::TestValidateText::test_detecta_caractere_menor_que PASSED
tests/test_smoke.py::TestValidateText::test_detecta_ampersand PASSED
tests/test_smoke.py::TestValidateText::test_texto_longo_gera_warning PASSED
tests/test_smoke.py::TestValidateText::test_texto_curto_valido_sem_avisos PASSED
19 passed in X.XXs
```

**Commit message:**
```
test: adicionar testes de fumaça para threemf_exporter e validate_text
```

---

---

## Resumo dos Commits (ordem sugerida)

```bash
# 1. XML escape (crítico)
git add src/blender/threemf_exporter.py
git commit -m "fix: adiciona escape de XML em threemf_exporter para prevenir corrupção de 3MF"

# 2+3+4. UX e subprocess (críticos, mesmo arquivo)
git add src/web/app.py
git commit -m "fix: remove progress bar falsa, trata TimeoutExpired/FileNotFoundError, usa BLENDER_PATH do ambiente"

# 5. Validação bloqueante
git add src/web/app.py
git commit -m "fix: validação retorna erros bloqueantes separados de warnings; bloquear geração com chars inválidos"

# 6. Nome do condomínio configurável
git add src/blender/generator.py src/web/app.py docker-compose.yml
git commit -m "feat: tornar nome do condomínio configurável via variável de ambiente CONDO_NAME"

# 7+8. Correções em generator.py
git add src/blender/generator.py
git commit -m "fix: corrigir path de saída hardcoded; mover import de threemf_exporter para o topo"

# 9. DEBUG via LOG_LEVEL
git add src/blender/generator.py src/blender/threemf_exporter.py docker-compose.yml
git commit -m "fix: controlar modo DEBUG via variável LOG_LEVEL"

# 10. Busca binária
git add src/blender/generator.py
git commit -m "perf: substituir busca linear por busca binária em calculate_font_size"

# 11. Slider de fonte
git add src/web/app.py
git commit -m "feat: ajustar slider de fonte para max 30mm com aviso contextual acima de 20mm"

# 12+13. Infra/config
git add docker-compose.yml .gitignore
git commit -m "chore: remover version deprecated do docker-compose; expandir .gitignore"

# 14. Testes
git add tests/ requirements-dev.txt
git commit -m "test: adicionar testes de fumaça para threemf_exporter e validate_text"

# Push e PR
git push origin fix/code-quality
```

---

## Verificação Final

Após todas as correções, o agente deve executar:

```bash
# 1. Verificar que os testes passam
pip install -r requirements-dev.txt
pytest tests/ -v --tb=short

# 2. Verificar que o .gitignore está correto (output/ não rastreado)
git status

# 3. Verificar diferença em relação ao main
git diff main --stat

# 4. Build Docker (opcional, para validação completa)
docker compose build
docker compose up -d
# Acessar http://localhost:8501 e gerar uma placa teste
docker compose down
```

---

*Documento gerado em 25/05/2026 — para execução por agente de código na branch `fix/code-quality`.*

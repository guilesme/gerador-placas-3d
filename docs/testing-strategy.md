# Estrategia de Testes

O projeto combina UI Streamlit, subprocesso Blender e geracao de arquivo 3MF. Por isso, os testes devem ser organizados por camadas.

## Objetivos

- detectar regressao antes de quebrar o fluxo atual;
- validar que `.3mf` gerado tem estrutura esperada;
- manter funcoes puras testaveis fora do Blender;
- documentar testes manuais inevitaveis;
- dar confianca para releases e tags.

## Camadas de Teste

### 1. Testes estaticos basicos

Rodar sempre:

```bash
python -m py_compile src/web/app.py src/web/validation.py src/web/plate_service.py src/blender/generator.py src/blender/threemf_exporter.py
python -m unittest discover -s tests -v
```

Objetivo: detectar erro de sintaxe/import basico.

### 2. Testes unitarios sem Blender

Criar modulos puros para serem testados sem Streamlit e sem Blender.

Alvos recomendados:

- validacao de texto;
- sanitizacao/escape para HTML;
- sanitizacao/escape para XML;
- montagem de XML/JSON do exportador que nao depende de `bpy`;
- verificacao de estrutura ZIP `.3mf` com `get_mesh_data` mockado.

Recomendacao de estrutura futura:

```text
src/
  web/
    app.py
    validation.py
  blender/
    threemf_exporter.py
tests/
  test_validation.py
  test_threemf_exporter.py
```

### 3. Smoke test de exportador 3MF

Objetivo: confirmar que `export()` cria um ZIP com as entradas obrigatorias.

Entradas esperadas:

```text
[Content_Types].xml
_rels/.rels
3D/3dmodel.model
3D/_rels/3dmodel.model.rels
3D/Objects/objects.model
Metadata/model_settings.config
Metadata/filament_settings_1.config
Metadata/filament_settings_2.config
```

### 4. Teste de integracao com Blender

Rodar em ambiente com Blender instalado ou dentro do Docker:

```bash
blender --background --python src/blender/generator.py -- "Teste" output/test_smoke.3mf 20 CENTER
```

Validar:

- comando retorna exit code 0;
- arquivo existe;
- arquivo tem tamanho maior que 1KB;
- ZIP abre;
- XML principal parseia;
- Bambu Studio importa o arquivo manualmente.

### 5. Testes manuais de UI

Antes de release:

- abrir Streamlit;
- gerar placa com uma linha;
- gerar placa com multiplas linhas;
- testar alinhamento central;
- testar alinhamento esquerdo;
- testar titulo centralizado;
- testar texto longo;
- testar caracteres especiais;
- baixar `.3mf`;
- verificar mensagem de erro com Blender invalido.

## Comandos Recomendados

Sem dependencias extras:

```bash
python -m py_compile src/web/app.py src/blender/generator.py src/blender/threemf_exporter.py
```

Com pytest futuramente:

```bash
python -m pytest tests/ -v
```

Com Docker:

```bash
docker compose build
docker compose up
```

## Matriz Minima de Regressao

| Cenario | Entrada | Esperado |
|---|---|---|
| Texto simples | `Portaria` | `.3mf` gerado |
| Multilinha | `Bloco A\nSalao` | texto em linhas separadas |
| Texto longo | 120+ caracteres | warning ou auto-scale |
| HTML no texto | `<b>Teste</b>` | aparece como texto literal no preview |
| Ampersand | `A & B` | preview correto e XML valido |
| Blender ausente | `BLENDER_PATH` invalido | erro amigavel |
| Alinhamento esquerdo | `Linha 1\nLinha 2` | linhas alinhadas a esquerda |

## Quando Adicionar Teste

Adicionar teste quando:

- bug foi corrigido e pode voltar;
- comportamento e regra de negocio;
- houve refatoracao;
- houve alteracao no exportador 3MF;
- houve mudanca em validacao/sanitizacao;
- houve mudanca de CLI ou variaveis de ambiente.

## Definicao de Teste Suficiente por Tipo de Mudanca

| Tipo de mudanca | Teste minimo |
|---|---|
| Documentacao | leitura/revisao + links funcionando |
| UI | teste manual + screenshot se possivel |
| Validacao | teste unitario |
| Subprocesso Blender | teste com mock + teste manual |
| Exportador 3MF | teste unitario + parse XML + smoke ZIP |
| Geometria Blender | geracao real + importacao no Bambu Studio |

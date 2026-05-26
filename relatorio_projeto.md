# 📊 Relatório Completo — Gerador de Placas 3D

> **Projeto:** `gerador-placas-3d`
> **Repositório:** [github.com/guilesme/gerador-placas-3d](https://github.com/guilesme/gerador-placas-3d)
> **Data da Análise:** 25 de Maio de 2026
> **Branch:** `main`

---

## 1. Visão Geral

Aplicação containerizada (Docker) para **automação de geração de placas de sinalização 3D** para impressão no Bambu Lab A1. O sistema recebe texto via interface web (Streamlit), aciona o Blender 4.0.2 em modo headless via subprocesso para gerar geometria 3D, e entrega um arquivo `.3mf` pronto para importar no Bambu Studio com suporte multi-material (AMS).

**Caso de uso principal:** Gerar placas de sinalização personalizadas para o Condomínio Astro com padrão estético rigoroso.

---

## 2. Estrutura do Projeto

```
gerador-placas-3d/
├── assets/
│   └── fonts/
│       └── Roboto-Bold.ttf         # Fonte da placa (514 KB)
├── src/
│   ├── __init__.py
│   ├── blender/
│   │   ├── generator.py            # Script bpy principal (382 linhas)
│   │   └── threemf_exporter.py     # Exportador 3MF customizado (251 linhas)
│   └── web/
│       └── app.py                  # Frontend Streamlit (463 linhas)
├── output/                         # 42 arquivos .3mf gerados (staging local)
├── Dockerfile                      # Build da imagem Docker
├── docker-compose.yml              # Orquestração
├── requirements.txt                # Dependências Python
├── spec.md                         # Especificação técnica detalhada
├── code_review_report.md           # Relatório de code review anterior
├── README.md
├── CONTRIBUTING.md
└── LICENSE (MIT)
```

**Métricas de código:**
| Arquivo | Linhas | Tamanho |
|---|---|---|
| `src/web/app.py` | 463 | 14 KB |
| `src/blender/generator.py` | 382 | 11.8 KB |
| `src/blender/threemf_exporter.py` | 251 | 8.6 KB |
| `Dockerfile` | 67 | 1.6 KB |
| **Total** | **~1.163** | **~36 KB** |

---

## 3. Stack Tecnológico

| Camada | Tecnologia | Versão |
|---|---|---|
| Frontend | Streamlit | 1.30.0 |
| Backend 3D | Blender (headless via `bpy`) | 4.0.2 |
| Runtime | Python | 3.10 |
| Containerização | Docker + Docker Compose | 3.8 |
| Fonte tipográfica | Roboto Bold | — |
| Formato de saída | 3MF (ZIP + XML) | Bambu-compatible |
| Dependência auxiliar | watchdog | 3.0.0 |

---

## 4. Arquitetura

```
[Usuário] 
    │ HTTP (8501)
    ▼
[Streamlit - app.py]
    │ subprocess.run(blender --background --python ...)
    ▼
[Blender 4.0.2 headless]
    │ bpy API
    ├─ generator.py ──► Cria geometria (placa + texto 3D)
    └─ threemf_exporter.py ──► Escreve .3mf (ZIP com XMLs)
    │
    ▼
[output/*.3mf]
    │ st.download_button
    ▼
[Usuário baixa o arquivo]
```

**Fluxo de geração:**
1. Texto inserido no frontend → validação de caracteres e tamanho
2. `generate_plate()` monta o comando `blender --background --python generator.py -- <texto> <output> <font_size> <align>`
3. Blender executa: limpa cena → cria placa base (pentágono com chanfro) → calcula auto-scale da fonte → cria texto 3D (extrusão) → cria rodapé fixo → exporta `.3mf`
4. O `.3mf` é servido via `st.download_button` para download direto

---

## 5. Pontos Positivos ✅

- **Geometria correta:** A placa possui forma personalizada (pentágono com chanfro oblíquo de 42.48mm na quina inferior direita), fielmente implementada com `bmesh`.
- **Auto-scale inteligente:** O algoritmo `calculate_font_size()` testa tamanhos de 20mm para baixo (até 5mm), aplicando quebra de linha automática (`wrap_text_to_fit()`) para garantir que o texto sempre caiba.
- **Multi-material AMS:** Dois objetos separados (Placa e Texto) são exportados com `extruder ID` correto para que o Bambu Studio reconheça as cores automaticamente.
- **3MF customizado:** O exportador implementa do zero o formato 3MF compatível com o Bambu Lab, incluindo metadados de filamento (`filament_settings_*.config`), relacionamentos XML e assemblagem por componentes — um trabalho não trivial.
- **UI Premium:** O frontend Streamlit usa CSS extensivo com glassmorphism, gradientes, dark mode, animações em hover e preview em tempo real da placa — visual bem acima do padrão do Streamlit puro.
- **Preview ao vivo:** Renderização HTML/CSS da placa no sidebar antes de gerar o 3D — melhora muito a UX.
- **Configurabilidade:** O usuário pode ajustar tamanho de fonte (5–40mm) e alinhamento (Centro, Esquerda, Título centralizado) via sidebar.
- **Documentação:** `spec.md` detalha rigorosamente dimensões, z-logic, margens e materiais. `CONTRIBUTING.md` e `README.md` presentes.
- **Licença MIT** e estrutura de projeto bem organizada.

---

## 6. Problemas Identificados ⚠️

### 🔴 Críticos

| # | Problema | Localização | Impacto |
|---|---|---|---|
| 1 | **Progress bar falsa** | `app.py` L417-418 | Loop síncrono vai de 0→50% instantaneamente, depois congela até o Blender terminar (pode levar minutos), dando a impressão de travamento. |
| 2 | **Timeout muito longo** | `app.py` L258 | `timeout=180s` (3 min). Junto com a progress bar falsa, o usuário fica sem feedback por tempo excessivo. |

### 🟡 Moderados

| # | Problema | Localização | Impacto |
|---|---|---|---|
| 3 | **Hardcoding do nome do condomínio** | `generator.py` L34, `app.py` L279/374/446 | "Condomínio Astro" está fixo em múltiplos locais — impossível reutilizar a ferramenta para outros condomínios sem editar código. |
| 4 | **Hardcoding do path de saída** | `generator.py` L356 | Fallback aponta para `/app/output/placa.3mf` (path Docker), quebrando em execução local. |
| 5 | **Validação não bloqueia** | `app.py` L358-362 | Avisos de caracteres inválidos são exibidos mas a geração prossegue, podendo resultar em malhas defeituosas sem o usuário entender o motivo. |
| 6 | **Exception genérica** | `app.py` L268 | `except Exception as e:` silencia erros sem distinção (timeout, I/O, permissão). |
| 7 | **XML por concatenação de strings** | `threemf_exporter.py` (todo) | Frágil a caracteres especiais no texto (ex: `<`, `>`, `&`) — pode corromper o XML silenciosamente. |
| 8 | **Blender path hardcoded** | `app.py` L247 | `"blender"` pressupõe que está no PATH; ignora `BLENDER_PATH` da variável de ambiente definida no `docker-compose.yml`. |

### 🟢 Menores

| # | Problema | Localização | Impacto |
|---|---|---|---|
| 9 | **DEBUG=True fixo em produção** | `generator.py` L39, `threemf_exporter.py` L16 | Sempre loga para stdout; deveria ser configurável. |
| 10 | **`output/` com 42 arquivos commitados** | `.gitignore` L9-10 | O `.gitignore` ignora `output/*.3mf`, mas a pasta local acumula arquivos temporários (não vão pro Git, mas ocupam espaço local). |
| 11 | **`font_size` máximo de 40mm no slider** | `app.py` L293 | A spec define máximo de 14mm com auto-scale; permitir 40mm pode gerar texto que extrapola a placa sem aviso. |
| 12 | **Sem testes automatizados** | — | Zero testes unitários ou de integração; regressões são detectadas apenas manualmente. |
| 13 | **`docker-compose.yml` usa `version: '3.8'`** | `docker-compose.yml` L1 | Atributo `version` deprecated no Docker Compose v2+. |

---

## 7. Análise por Módulo

### `src/blender/generator.py`
**Qualidade geral: 🟡 Boa com ressalvas**
- Constantes bem definidas e documentadas no topo ✅
- `create_plate()` com normais recalculadas via bmesh ✅
- `wrap_text_to_fit()` cria/destrói objetos temporários no Blender repetidamente — pode ser lento para textos longos
- `calculate_font_size()` usa decremento fixo de 1mm — poderia usar busca binária para performance
- Import de `threemf_exporter` feito em runtime (linha 320) em vez de no topo do arquivo

### `src/blender/threemf_exporter.py`
**Qualidade geral: 🟡 Funcional mas frágil**
- Implementação completa e funcional do formato Bambu 3MF ✅
- Triangulação automática + aplicação de transformação mundial ✅
- XML gerado por f-strings — **risco real** se o texto da placa contiver `<`, `>` ou `&`
- `build_filament_settings()` usa `json.dumps` para um JSON estático — poderia ser constante

### `src/web/app.py`
**Qualidade geral: 🟡 UX boa, código com pontos de atenção**
- CSS premium extenso e bem estruturado ✅
- Preview ao vivo da placa no HTML ✅
- `generate_plate()` mistura orquestração e I/O — poderia ser dividida
- Sem tratamento específico para `subprocess.TimeoutExpired`
- `validate_text()` usa regex genérico — não verifica especificamente contra o charset da Roboto Bold

---

## 8. Recomendações Prioritárias

### Prioridade Alta
1. **Escapar texto XML** em `threemf_exporter.py`: usar `xml.sax.saxutils.escape()` ou `xml.etree.ElementTree` para evitar corrupção silenciosa.
2. **Feedback real de progresso**: substituir o loop falso por `st.spinner()` ou usar threading para não bloquear a UI.
3. **Usar `BLENDER_PATH`** do ambiente: `cmd[0] = os.environ.get("BLENDER_PATH", "blender")`.

### Prioridade Média
4. **Tornar o nome do condomínio configurável** via variável de ambiente ou campo na interface.
5. **Tratar `subprocess.TimeoutExpired`** separadamente com mensagem amigável.
6. **Adicionar pelo menos 1 teste de smoke** para a exportação 3MF.

### Prioridade Baixa
7. **Busca binária** no `calculate_font_size()` para performance.
8. **Remover `DEBUG=True`** fixo; usar `logging` com nível configurável via `LOG_LEVEL`.
9. **Remover `version:` do `docker-compose.yml`** (deprecated).

---

## 9. Status de Sincronização com GitHub 🔄

> [!IMPORTANT]
> **O repositório está ✅ completamente sincronizado com o GitHub.**

| Item | Status |
|---|---|
| Remote | `origin` → `https://github.com/guilesme/gerador-placas-3d.git` |
| Branch local | `main` |
| Branch remota | `origin/main` |
| Working tree | `clean` (nada para commitar) |
| Ahead/Behind | `0 commits` de diferença |

**Histórico de commits (3 commits):**

| Hash | Mensagem | 
|---|---|
| `85684df` | `feat: adiciona ajuste de tamanho de fonte e alinhamento de título` |
| `3076fce` | `Add readme, license and contrib` |
| `9e77544` | `Initial commit: 3D Plate Generator App` |

O commit mais recente (`85684df`) é idêntico tanto no local quanto no remoto — não há divergências, branches pendentes nem stash acumulado.

---

## 10. Resumo Executivo

| Dimensão | Avaliação |
|---|---|
| **Funcionalidade** | ✅ Completa e funcional |
| **Arquitetura** | ✅ Bem separada (frontend / geração 3D / exportação) |
| **Qualidade de código** | 🟡 Boa com 3 pontos de atenção críticos |
| **Robustez / Tratamento de erros** | 🟡 Precisa melhorar |
| **Segurança** | 🟡 Risco de injeção XML (texto → XML sem escape) |
| **Testabilidade** | 🔴 Zero testes automatizados |
| **Documentação** | ✅ Excelente (spec.md, README, CONTRIBUTING) |
| **DevOps / Docker** | ✅ Funcional e pronto para deploy |
| **Sincronização GitHub** | ✅ 100% sincronizado |

---

*Relatório gerado em 25/05/2026 por análise estática completa do código-fonte.*

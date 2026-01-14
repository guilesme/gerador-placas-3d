# SPEC.MD - Agente Gerador de Placas 3D (Antigravity)

## 1. Visão Geral
Aplicação containerizada para automação de design de placas de sinalização 3D. O sistema transforma strings de texto em modelos `.3mf` prontos para impressão no Bambu Lab A1, respeitando padrões estéticos rigorosos, dimensões fixas e requisitos de multi-material (AMS).

## 2. Requisitos Funcionais

### Entrada (Input)
- **Interface Web:** Campo de texto simples via Streamlit.
- **Múltiplas Linhas:** Suporte a quebra de linha (Enter = novo parágrafo na placa).
- **Validação:**
    - **Auto-scale:** O texto deve ser redimensionado automaticamente para caber na área útil.
    - **Legibilidade:** Limite mínimo de tamanho de fonte (5mm). Se o texto for longo demais e ferir a legibilidade (distância de 2m), exibir alerta de confirmação (Continuar/Cancelar).
    - **Caracteres:** Detecção de caracteres não suportados pela fonte "Roboto Bold". Exibir aviso se detectado.

### Processamento (Core)
1.  **Carregamento do Template:** Geração procedural baseada em dimensões fixas.
2.  **Texto Principal:**
    - Fonte: Roboto Bold.
    - Tamanho Padrão: 14mm (auto-scale entre 5mm e 14mm).
    - Posicionamento: Centralizado (H/V) na face superior.
    - Operação: Extrusão direta do texto com altura total de 0.7mm (0.3mm escavado + 0.4mm salto).
3.  **Texto Fixo (Rodapé):**
    - Conteúdo: "Condomínio Astro".
    - Posição: Inferior Esquerdo (offset: X=15mm, Y=10mm da borda).
    - Tamanho de Fonte: 6mm.
4.  **Materiais (AMS):**
    - Slot 1 (Base/Placa): Cor Marrom.
    - Slot 2 (Texto): Cor Branca.
    - **Técnica:** Objetos separados na exportação 3MF com atribuição de extruder ID para que o Bambu Studio reconheça as cores automaticamente.

### Saída (Output)
- **Download:** Botão na interface Streamlit para baixar o arquivo `.3mf` gerado imediatamente após o sucesso.
- **Logs:** Visualização de logs de erro na interface em caso de falha.

## 3. Especificações Técnicas e Design

### Dimensões da Placa
- **Tamanho Total:** 200mm (L) x 180mm (A) x 2mm (P).
- **Geometria Específica:** Retângulo com corte oblíquo (chanfro) na quina inferior direita.
- **Medida do Chanfro:** 42.48mm (diagonal).

### Margens e Áreas Úteis
- **Margem Lateral (X):** 20mm de cada lado.
- **Margem Vertical (Y):** 30mm (topo e base).
- **Área Útil do Texto Principal:** 160mm x 120mm.

### Z-Logic (Profundidade)
| Camada | Valor | Descrição |
|--------|-------|-----------|
| `Z_surface` | 2.0mm | Topo da placa |
| `Z_text_base` | 1.7mm | Base do texto (escavado 0.3mm) |
| `Z_text_top` | 2.4mm | Topo do texto (salto 0.4mm) |
| `TEXT_TOTAL_HEIGHT` | 0.7mm | Altura total do texto sólido |

### Estrutura do Projeto
```text
/
├── assets/
│   ├── templates/              # Base .3mf files (se necessário)
│   └── fonts/                  # Roboto-Bold.ttf
├── src/
│   ├── blender/
│   │   ├── generator.py        # Script bpy principal
│   │   └── threemf_exporter.py # Módulo de exportação 3MF
│   └── web/
│       └── app.py              # Streamlit Frontend
├── output/                     # Staging area para arquivos gerados
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── spec.md
```

## 4. Tratamento de Erros e Validação
- **Exit Codes:** Script Python/Blender retorna `0` (Sucesso) ou `1` (Erro).
- **File Check:** Verificação de existência e tamanho (>1KB) do arquivo de saída.
- **Timeout:** Limite de 120 segundos (2 minutos) para geração do arquivo.
- **UX de Erro:** Exibir mensagem descritiva no frontend, opção de ver logs técnicos, e botão "Reiniciar" para limpar estado.

## 5. Deployment
- **Docker:**
    - Imagem base: `python:3.10-slim` com Blender 4.0.2 instalado.
    - **Porta:** 8501 (Streamlit).
    - **Persistência:** Arquivos gerados em pasta temporária dentro do container, servidos via HTTP pelo Streamlit para download direto.
    - **Fontes:** Roboto-Bold copiada para `/usr/share/fonts/truetype/` durante build.
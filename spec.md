# Especificacao Tecnica - Gerador de Placas 3D

Versao da especificacao: `0.2.0-dev`

Esta especificacao descreve o comportamento atual validado da aplicacao. Ela substitui a especificacao inicial gerada durante a fase de prototipo.

## 1. Visao Geral

O projeto e uma aplicacao containerizada para gerar placas de sinalizacao 3D em formato `.3mf`, usando Streamlit como interface e Blender em modo headless para criar geometria e exportar o modelo.

O caso de uso atual e a geracao de placas para o Condominio Astro, com base marrom e texto branco, destinadas ao fluxo Bambu Studio / Bambu Lab A1.

## 2. Entrada

### Interface

- Campo de texto via Streamlit.
- Suporte a multiplas linhas.
- Controle de tamanho de fonte principal.
- Controle de tamanho da placa:
  - padrao: 200 x 180mm;
  - reduzida: 200 x 128mm.
- Controle de alinhamento:
  - centro;
  - esquerda;
  - esquerda com primeira linha centralizada.

### Validacao

A validacao retorna dois tipos de resultado:

- `errors`: bloqueiam a geracao;
- `warnings`: avisam o usuario, mas permitem continuar.

Regras atuais:

- caracteres nao suportados pela politica da aplicacao geram erro bloqueante;
- texto com mais de 100 caracteres gera warning de legibilidade;
- texto inserido no preview HTML deve ser escapado antes da renderizacao.

## 3. Geometria da Placa

| Campo | Valor |
|---|---:|
| Largura | 200mm |
| Altura | 180mm ou 128mm |
| Espessura | 2mm |
| Chanfro inferior direito | 42.48mm |

A placa e gerada proceduralmente como malha solida, com corte obliquo na quina inferior direita.

## 4. Texto Principal

| Campo | Valor atual |
|---|---:|
| Fonte | Roboto Bold |
| Tamanho padrao no gerador | 20mm |
| Tamanho minimo | 5mm |
| Slider da UI | 5mm a 20mm |
| Largura util | 160mm |
| Altura util considerada no gerador | 100mm na placa 180mm; 48mm na placa 128mm |
| Altura total do texto 3D | 0.7mm |

Observacao: textos longos ainda precisam de validacao visual, principalmente na placa reduzida, pois a area vertical disponivel e menor.

## 5. Rodape

| Campo | Valor atual |
|---|---:|
| Texto | Condominio Astro |
| Fonte | Roboto Bold |
| Tamanho | 8mm |
| Offset X | 15mm da borda esquerda |
| Offset Y | 12mm da borda inferior |

O nome do rodape ainda e fixo no codigo. A melhoria para torna-lo configuravel esta registrada como `IMP-001`.

## 6. Z-Logic

| Camada | Valor | Descricao |
|---|---:|---|
| `Z_PLATE_TOP` | 2.0mm | Topo da placa |
| `Z_TEXT_BASE` | 1.7mm | Base do texto, 0.3mm abaixo do topo |
| `Z_TEXT_TOP` | 2.4mm | Topo do texto, 0.4mm acima da placa |
| `TEXT_HEIGHT` | 0.7mm | Altura total do solido do texto |

## 7. Materiais e Bambu Studio

Objetos exportados:

- `Placa`: extruder/material 1;
- `Texto`: extruder/material 2.

Cores pretendidas:

- Slot 1: PETG marrom `#804000` para a placa, perfil `Voolt3D PETG Premium - Marrom`;
- Slot 2: PETG branco `#FFFFFF` para texto, perfil `Voolt3D PETG Premium - White`.

Validacao manual atual:

- o arquivo `.3mf` abre no Bambu Studio;
- a geometria aparece corretamente;
- testes automatizados confirmam que os dois arquivos `filament_settings_*.config` usam os perfis PETG padronizados;
- validacao manual apos `IMP-003` mostrou que os filamentos ainda nao abriram selecionados corretamente, mas a selecao manual foi simples e o restante ja ficou configurado/preenchido.

Essa padronizacao de filamentos esta registrada como `IMP-003`; a investigacao do preenchimento automatico dos filamentos no Bambu Studio foi separada em `IMP-005`.

## 8. Saida

- Arquivo `.3mf`;
- download direto via Streamlit;
- arquivo salvo na pasta `output/`;
- validacao minima: arquivo existe e possui mais de 1KB.

## 9. Tratamento de Erros

Timeout:

- 120 segundos.

Erros tratados no frontend:

- timeout do subprocesso;
- Blender ausente;
- erro de sistema ao executar Blender;
- retorno nao-zero do Blender com logs preservados;
- arquivo de saida ausente ou pequeno demais.

## 10. Estrutura Atual

```text
assets/
  fonts/
    Roboto-Bold.ttf
src/
  blender/
    generator.py
    threemf_exporter.py
  web/
    app.py
    plate_service.py
    validation.py
tests/
docs/
output/
```

## 11. Testes

Comandos de validacao:

```bash
python -m py_compile src/web/app.py src/web/validation.py src/web/plate_service.py src/blender/generator.py src/blender/threemf_exporter.py
python -m unittest discover -s tests -v
docker compose config --quiet
```

Validacoes manuais:

- abrir a UI em `http://localhost:8501`;
- gerar placa com texto simples;
- baixar `.3mf`;
- abrir/importar no Bambu Studio;
- confirmar mapeamento de materiais quando `IMP-003` for implementado.

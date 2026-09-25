# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Pessoas responsáveis pela sinalização de um condomínio que configuram e imprimem placas no Bambu Studio. Usam a ferramenta para preparar uma placa com texto, tamanho, corte e rodapé antes de produzir o arquivo `.3mf`.

## Product Purpose

Gerar placas 3D de sinalização para o Condomínio Astro de forma rápida e consistente. O sucesso é produzir um arquivo pronto para impressão sem exigir edição manual da geometria.

## Positioning

Uma ferramenta operacional que transforma a configuração da placa diretamente em geometria e em um projeto 3MF para o fluxo Bambu Studio, incluindo texto em relevo, dois materiais e os dois formatos de placa.

## Operating Context

O trabalho acontece em computador, próximo ao preparo de impressão 3D. O usuário escolhe texto, rodapé, dimensões, alinhamento e lado do corte; em seguida baixa o `.3mf` e o abre no Bambu Studio.

## Capabilities and Constraints

- Placas padrão de 200 x 180 mm e reduzidas de 200 x 128 mm.
- Base marrom e texto branco são propriedades da placa impressa e não devem mudar.
- O site deve manter todos os controles atuais e a geração de `.3mf`.
- O redesign solicitado é exclusivamente da interface web: mais bonita e moderna, sem perda de funcionalidade.

## Brand Commitments

Nome: Gerador de Placas 3D. O Condomínio Astro é o contexto atual. A interface deve ser clara, objetiva e adequada a uma ferramenta de trabalho.

## Evidence on Hand

- Fonte Roboto Bold em `assets/fonts/Roboto-Bold.ttf`.
- Placas impressas de referência em marrom e branco.
- Aplicação Streamlit em `src/web/app.py`.

## Product Principles

- Configurar uma placa deve ser compreensível em uma única tela.
- O preview deve ajudar a evitar erros antes da impressão.
- Preferir clareza operacional a decoração.
- Preservar a consistência física das placas.

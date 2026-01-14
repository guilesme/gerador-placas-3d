# Gerador de Placas 3D

Este projeto é uma aplicação containerizada para automação de design de placas de sinalização 3D. O sistema transforma strings de texto em modelos `.3mf` prontos para impressão no Bambu Lab A1, respeitando padrões estéticos rigorosos, dimensões fixas e requisitos de multi-material (AMS).

## 🚀 Funcionalidades

*   **Interface Web Simples**: Interface amigável construída com Streamlit.
*   **Geração Automática**: Transforma texto em modelos 3D (`.3mf`) prontos para impressão.
*   **Auto-scale Inteligente**: Redimensionamento automático do texto para caber na área útil (5mm a 14mm).
*   **Multi-material (AMS)**: Suporte nativo para impressão multicolorida (Base e Texto separados).
*   **Validação de Input**: Verificação de caracteres suportados e legibilidade.

## 🛠️ Tecnologias Utilizadas

*   **Python 3.10**
*   **Blender 4.0.2** (para processamento 3D)
*   **Streamlit** (Frontend)
*   **Docker** (Containerização)

## 📋 Pré-requisitos

*   [Docker](https://www.docker.com/get-started) instalado e rodando na sua máquina.

## 🔧 Como Rodar

A maneira mais fácil de rodar o projeto é utilizando o Docker Compose:

1.  **Clone o repositório:**
    ```bash
    git clone <seu-repositorio-url>
    cd <nome-da-pasta>
    ```

2.  **Suba a aplicação:**
    ```bash
    docker-compose up --build
    ```

3.  **Acesse a interface:**
    Abra o seu navegador e vá para `http://localhost:8501`.

## 📂 Estrutura do Projeto

```text
/
├── assets/
│   ├── templates/      # Arquivos base .3mf
│   └── fonts/          # Fontes (Roboto-Bold.ttf)
├── src/
│   ├── blender/        # Scripts de automação do Blender
│   └── web/            # Interface Streamlit
├── output/             # Área temporária para arquivos gerados
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## ⚙️ Detalhes Técnicos

*   **Dimensões da Placa**: 200mm x 180mm x 2mm.
*   **Fonte Padrão**: Roboto Bold.
*   **Cores Padrão**:
    *   Slot 1: Marrom (Base)
    *   Slot 2: Branco (Texto)

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

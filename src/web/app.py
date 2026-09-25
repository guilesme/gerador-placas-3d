"""
Gerador de Placas 3D - Frontend Streamlit v1.1.1
Interface de ficha de produção para configuração e geração de placas.
"""

import html
import os
from pathlib import Path
import streamlit as st
from plate_service import generate_plate
from validation import validate_text

DEFAULT_CONDO_NAME = os.environ.get("CONDO_NAME", "Condominio Astro")
VERSION_FILE = Path(__file__).resolve().parents[2] / "VERSION"
APP_VERSION = VERSION_FILE.read_text(encoding="utf-8").strip() if VERSION_FILE.exists() else "1.1.1"

# Configuração da página
st.set_page_config(
    page_title="Gerador de Placas 3D",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Premium
st.markdown("""
<style>
    /* Reset e Base */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #0f0f1a 100%);
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #e0e0e0;
    }
    
    /* Header Principal */
    .main-header {
        background: linear-gradient(135deg, #e67e22 0%, #d35400 100%);
        padding: 2rem 2.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(230, 126, 34, 0.3);
        text-align: center;
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
    }
    
    /* Cards */
    .card {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .card-title {
        color: #e67e22;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Input de Texto */
    .stTextArea textarea {
        background: rgba(255,255,255,0.08) !important;
        border: 2px solid rgba(255,255,255,0.15) !important;
        border-radius: 12px !important;
        color: white !important;
        font-size: 1.1rem !important;
        padding: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #e67e22 !important;
        box-shadow: 0 0 20px rgba(230, 126, 34, 0.3) !important;
    }
    
    /* Sliders */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #e67e22, #f39c12) !important;
    }
    
    /* Botões */
    .stButton > button {
        background: linear-gradient(135deg, #e67e22 0%, #d35400 100%) !important;
        color: white !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        padding: 0.8rem 2rem !important;
        border: none !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(230, 126, 34, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 25px rgba(230, 126, 34, 0.5) !important;
    }
    
    /* Download Button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%) !important;
        color: white !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        padding: 1rem 2rem !important;
        border: none !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(39, 174, 96, 0.4) !important;
    }
    
    /* Métricas */
    [data-testid="stMetricValue"] {
        color: #e67e22 !important;
        font-size: 1.8rem !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: rgba(255,255,255,0.7) !important;
    }
    
    /* Alertas */
    .success-box {
        background: linear-gradient(135deg, rgba(39, 174, 96, 0.2) 0%, rgba(46, 204, 113, 0.1) 100%);
        border: 1px solid rgba(39, 174, 96, 0.5);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        margin: 1rem 0;
    }
    
    .success-box h3 {
        color: #2ecc71;
        margin: 0 0 0.5rem 0;
    }
    
    .warning-box {
        background: rgba(241, 196, 15, 0.1);
        border: 1px solid #f1c40f;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    /* Preview Box */
    .preview-box {
        background: rgba(230, 126, 34, 0.1);
        border: 2px dashed rgba(230, 126, 34, 0.5);
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        color: rgba(255,255,255,0.7);
    }
    
    /* Specs Table */
    .specs-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin-top: 1rem;
    }
    
    .spec-item {
        background: rgba(255,255,255,0.05);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    
    .spec-value {
        color: #e67e22;
        font-size: 1.5rem;
        font-weight: 700;
    }
    
    .spec-label {
        color: rgba(255,255,255,0.6);
        font-size: 0.85rem;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: rgba(255,255,255,0.4);
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Sistema visual: ficha de produção para uma peça física, não um dashboard genérico.
st.markdown("""
<style>
    :root {
        --ink: #172321;
        --muted: #5e6c68;
        --paper: #f1f3ef;
        --line: #c8d0ca;
        --wood: #78401f;
        --wood-dark: #4f2917;
        --brass: #af7b38;
        --white-ink: #fffdf8;
    }
    .stApp { background: var(--paper) !important; color: var(--ink) !important; }
    [data-testid="stHeader"] { background: rgba(241,243,239,.92) !important; }
    [data-testid="stSidebar"] {
        background: #e4e9e4 !important;
        border-right: 1px solid var(--line) !important;
    }
    [data-testid="stSidebar"] * { color: var(--ink) !important; }
    .block-container { max-width: 1280px !important; padding-top: 2.25rem !important; padding-bottom: 3rem !important; }
    .main-header {
        background: transparent !important;
        box-shadow: none !important;
        border-radius: 0 !important;
        border-bottom: 1px solid var(--line);
        color: var(--ink) !important;
        display: grid;
        grid-template-columns: minmax(0,1fr) 184px;
        gap: 2rem;
        align-items: end;
        margin: 0 0 2.25rem 0 !important;
        padding: 0 0 1.5rem 0 !important;
        text-align: left !important;
    }
    .main-header h1 { color: var(--ink) !important; font-size: clamp(2.1rem, 5vw, 4.25rem) !important; letter-spacing: -.055em; line-height: .92; text-shadow: none !important; }
    .main-header p { color: var(--muted) !important; max-width: 48ch; margin: .75rem 0 0 !important; }
    .plate-mark { width: 184px; height: 108px; background: var(--wood); clip-path: polygon(0 0,100% 0,100% 60%,72% 100%,0 100%); position: relative; }
    .plate-mark::after { content: ""; position: absolute; inset: 12px; border: 1px solid rgba(255,253,248,.58); clip-path: polygon(0 0,100% 0,100% 60%,72% 100%,0 100%); }
    .card-title { color: var(--ink) !important; font-size: 1.05rem !important; letter-spacing: -.02em; border-bottom: 1px solid var(--line); padding-bottom: .7rem; margin-bottom: .9rem !important; }
    .stTextArea textarea, .stTextInput input {
        background: #fbfcfa !important; border: 1px solid #aeb9b2 !important; border-radius: 6px !important;
        color: var(--ink) !important; box-shadow: none !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus { border-color: var(--wood) !important; box-shadow: 0 0 0 3px rgba(120,64,31,.15) !important; }
    .stSlider > div > div > div { background: var(--wood) !important; }
    .stButton > button, .stDownloadButton > button {
        border-radius: 6px !important; border: 1px solid var(--wood-dark) !important; background: var(--wood) !important;
        box-shadow: 0 5px 0 var(--wood-dark) !important; color: var(--white-ink) !important; font-weight: 700 !important;
        transition: transform .16s ease, box-shadow .16s ease !important;
    }
    .stButton > button:hover, .stDownloadButton > button:hover { transform: translateY(2px) !important; box-shadow: 0 3px 0 var(--wood-dark) !important; }
    .stButton > button:focus-visible, .stDownloadButton > button:focus-visible { outline: 3px solid var(--brass) !important; outline-offset: 3px !important; }
    .preview-box { background: #e8ece8 !important; border: 1px dashed #aeb9b2 !important; border-radius: 6px !important; color: var(--muted) !important; }
    .production-preview { background: var(--wood); min-height: 280px; padding: 2rem; position: relative; clip-path: polygon(0 0,100% 0,100% 79%,84% 100%,0 100%); box-shadow: 0 12px 28px rgba(23,35,33,.18); }
    .production-preview::before { content: ""; position: absolute; inset: 12px; border: 1px solid rgba(255,253,248,.34); clip-path: polygon(0 0,100% 0,100% 79%,84% 100%,0 100%); pointer-events: none; }
    .production-preview .plate-copy { position: relative; color: var(--white-ink); font-weight: 700; line-height: 1.35; }
    .production-preview .plate-footer { position: absolute; bottom: 25px; left: 32px; color: rgba(255,253,248,.86); font-size: .72rem; }
    .success-box { background: #e5eee7 !important; border: 1px solid #75927a !important; border-radius: 6px !important; text-align: left !important; }
    .success-box h3 { color: #245336 !important; }
    .warning-box { background: #fbf2df !important; border: 1px solid var(--brass) !important; color: var(--ink) !important; }
    .footer { border-top: 1px solid var(--line); color: var(--muted) !important; margin-top: 4rem; padding: 1.5rem 0 !important; text-align: left !important; }
    @media (max-width: 760px) {
        .main-header { grid-template-columns: 1fr; }
        .plate-mark { width: 132px; height: 76px; }
        .production-preview { min-height: 230px; }
    }
</style>
""", unsafe_allow_html=True)

# ========== LAYOUT ==========

# Header
st.markdown(f"""
<div class="main-header">
    <div>
        <h1>Gerador de<br>Placas 3D</h1>
        <p>Prepare uma placa consistente para impressão, do texto ao arquivo 3MF.</p>
    </div>
    <div class="plate-mark" aria-hidden="true"></div>
</div>
""", unsafe_allow_html=True)

# Sidebar - Configurações
with st.sidebar:
    st.markdown("## Configuração")
    st.markdown("---")
    
    # Tamanho da Fonte
    st.markdown("### Texto")
    font_size = st.slider(
        "Tamanho da fonte (mm)",
        min_value=5,
        max_value=40,
        value=20,
        step=1,
        key="font_size_mm",
        help="Ajuste o tamanho das letras do texto principal. O rodapé mantém tamanho fixo."
    )
    
    # Preview do tamanho
    size_desc = "Pequeno" if font_size < 15 else "Médio" if font_size < 25 else "Grande"
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem; background: #f1e5d9; border: 1px solid #d5b99e; border-radius: 6px;">
        <div style="font-size: 2rem; color: #78401f;">{font_size} mm</div>
        <div style="color: #5e6c68;">{size_desc}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

    # Rodape
    st.markdown("### Rodape")
    footer_text = st.text_input(
        "Texto do rodape",
        value=DEFAULT_CONDO_NAME,
        max_chars=40,
        key="footer_text",
        help="Texto exibido no canto inferior esquerdo da placa."
    ).strip() or DEFAULT_CONDO_NAME

    st.markdown("---")

    # Altura da placa
    st.markdown("### Tamanho da Placa")
    plate_size_option = st.radio(
        "Altura da placa",
        options=["Padrao (180 mm)", "Reduzida (128 mm)"],
        index=0,
        key="plate_height_option",
        help="Selecione a altura da placa. A largura, espessura, relevo, rodape e cores permanecem iguais."
    )
    plate_height = 128 if plate_size_option.startswith("Reduzida") else 180

    st.markdown("---")

    # Lado do corte
    st.markdown("### Corte inferior")
    cut_side_option = st.radio(
        "Lado do corte",
        options=["Direita", "Esquerda"],
        index=0,
        horizontal=True,
        key="cut_side_option",
        help="Use esquerda para a placa de trás, espelhada em relação ao padrão.",
    )
    cut_side = "LEFT" if cut_side_option == "Esquerda" else "RIGHT"

    st.markdown("---")
    
    # Alinhamento
    st.markdown("### Alinhamento")
    align_option = st.radio(
        "Alinhamento",
        options=["Centro", "Esquerda"],
        index=0,
        horizontal=True,
        key="text_align_option",
        label_visibility="collapsed"
    )
    align_map = {"Centro": "CENTER", "Esquerda": "LEFT"}
    text_align = align_map[align_option]
    
    if align_option == "Esquerda":
        center_title = st.checkbox("Centralizar apenas o título (1ª linha)", value=False)
        if center_title:
            text_align = "LEFT_CENTER_TITLE"
    
    st.markdown("---")
    
    # Especificações
    st.markdown("### Especificações")
    st.markdown(f"""
    - **Placa:** 200 x {plate_height} mm
    - **Espessura:** 2 mm
    - **Relevo:** 0.7 mm
    - **Rodapé:** 8 mm
    - **Corte inferior:** {cut_side_option.lower()}
    """)
    
    st.markdown("---")
    st.markdown("### Materiais")
    st.markdown("""
    - **Slot 1:** Placa (Marrom)
    - **Slot 2:** Texto (Branco)
    """)

# Conteúdo Principal
col1, col2 = st.columns([2, 1])
validation_errors = []
validation_warnings = []

with col1:
    st.markdown('<div class="card-title">Texto da placa</div>', unsafe_allow_html=True)
    
    text_input = st.text_area(
        "Digite o texto",
        height=180,
        placeholder="Digite aqui o texto que aparecerá na placa...\n\nUse Enter para criar novas linhas.",
        label_visibility="collapsed"
    )
    
    if text_input:
        # Validação
        validation_errors, validation_warnings = validate_text(text_input)
        for e in validation_errors:
            st.error(f"🚫 {e}")
        for w in validation_warnings:
            safe_warning = html.escape(w)
            st.markdown(f'<div class="warning-box">⚠️ {safe_warning}</div>', unsafe_allow_html=True)
        
        # Info do texto
        lines = len([l for l in text_input.split('\n') if l.strip()])
        chars = len(text_input)
        st.markdown(f"**{chars}** caracteres · **{lines}** linha(s)")

with col2:
    st.markdown('<div class="card-title">Prévia de produção</div>', unsafe_allow_html=True)
    
    if text_input:
        lines = text_input.split('\n')
        if text_align == 'LEFT_CENTER_TITLE' and lines:
            title_html = f"<div style='text-align: center;'>{html.escape(lines[0])}</div>"
            rest_html = "<br>".join(html.escape(line) for line in lines[1:]) if len(lines) > 1 else ""
            content_html = title_html + (f"<div style='text-align: left;'>{rest_html}</div>" if rest_html else "")
        else:
            align_css = 'left' if text_align == 'LEFT' else 'center'
            safe_text = html.escape(text_input).replace(chr(10), '<br>')
            content_html = f"<div style='text-align: {align_css};'>{safe_text}</div>"
            
        st.markdown(f"""
        <div class="production-preview">
            <div class="plate-copy" style="font-size: {min(font_size/2, 14)}px; padding-top: 1rem;">
                {content_html}
            </div>
            <div class="plate-footer">
                {html.escape(footer_text)}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="preview-box">
            <div style="font-size: 1.1rem; margin-bottom: 0.5rem;">Aguardando conteúdo</div>
            <div>Digite o texto para montar a prévia da placa.</div>
        </div>
        """, unsafe_allow_html=True)

# Botão de Geração
st.markdown("<br>", unsafe_allow_html=True)

col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])

with col_btn2:
    generate_btn = st.button(
        "Gerar arquivo 3MF",
        disabled=not text_input or not text_input.strip() or bool(validation_errors),
        use_container_width=True
    )

# Processamento
if generate_btn and text_input.strip():
    with st.spinner("⏳ Gerando modelo 3D... Aguarde, isso pode levar ate 2 minutos."):
        success, filepath, msg = generate_plate(text_input.strip(), font_size, text_align, plate_height, footer_text, cut_side)
        
        if success:
            st.markdown("""
            <div class="success-box">
                <h3>Arquivo pronto para impressão</h3>
                <p>Baixe o arquivo 3MF para abrir no Bambu Studio.</p>
            </div>
            """, unsafe_allow_html=True)
            
            col_dl1, col_dl2, col_dl3 = st.columns([1, 2, 1])
            with col_dl2:
                with open(filepath, "rb") as f:
                    st.download_button(
                        label="Baixar arquivo .3mf",
                        data=f,
                        file_name=filepath.name,
                        mime="application/vnd.ms-package.3dmanufacturing-3dmodel+xml",
                        use_container_width=True
                    )
            
            with st.expander("Como usar no Bambu Studio"):
                st.markdown("""
                1. **Abra** o arquivo .3mf no Bambu Studio
                2. **Configure o AMS:**
                   - Slot 1: Filamento Marrom (placa)
                   - Slot 2: Filamento Branco (texto)
                3. **Faça o slice** e envie para a impressora
                """)
        else:
            st.error(f"❌ Erro na geração")
            with st.expander("Ver detalhes do erro"):
                st.code(msg)

# Footer
st.markdown(f"""
<div class="footer">
    <p>Gerador de Placas 3D · v{html.escape(APP_VERSION)}</p>
</div>
""", unsafe_allow_html=True)

import os
import streamlit as st
import base64
from openai import OpenAI
import openai
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas

# ─────────────────────────────
# CONFIG
# ─────────────────────────────
st.set_page_config(page_title='Tablero para Guiones 💖', layout='wide')

# 🎀 GIRLY STYLE
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

/* Fondo */
.stApp {
    background: linear-gradient(135deg, #fff0f5, #ffe4ec);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 2px solid #fbcfe8;
}

/* Títulos */
h1 { color: #be185d !important; }
h2, h3 { color: #9d174d !important; }

/* Botones */
.stButton > button {
    background: linear-gradient(135deg, #f472b6, #ec4899) !important;
    color: white !important;
    border-radius: 12px !important;
    border: none !important;
    font-weight: 600 !important;
}

/* Inputs */
input {
    border-radius: 10px !important;
    border: 1px solid #f9a8d4 !important;
}

/* Canvas card */
.canvas-card {
    background: white;
    border-radius: 18px;
    padding: 18px;
    border: 1px solid #fbcfe8;
    box-shadow: 0 6px 18px rgba(236,72,153,0.15);
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────
# SESSION STATE
# ─────────────────────────────
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'full_response' not in st.session_state:
    st.session_state.full_response = ""
if 'base64_image' not in st.session_state:
    st.session_state.base64_image = ""

# ─────────────────────────────
# FUNCIONES
# ─────────────────────────────
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# ─────────────────────────────
# UI
# ─────────────────────────────
st.title("🎀 Tablero Inteligente")
st.subheader("Dibuja tu idea y crea contenido para Instagram automáticamente ✨")

with st.sidebar:
    st.subheader("💖 Configuración")
    stroke_width = st.slider('Grosor del trazo', 1, 30, 5)

# Canvas
st.markdown('<div class="canvas-card">', unsafe_allow_html=True)

canvas_result = st_canvas(
    fill_color="rgba(255, 192, 203, 0.3)",
    stroke_width=stroke_width,
    stroke_color="#000000",
    background_color="#FFFFFF",
    height=300,
    width=400,
    drawing_mode="freedraw",
    key="canvas",
)

st.markdown('</div>', unsafe_allow_html=True)

# API KEY
api_key = st.text_input('🔑 Ingresa tu API Key', type="password")
os.environ['OPENAI_API_KEY'] = api_key

# Botón analizar
analyze_button = st.button("✨ Analizar dibujo")

# ─────────────────────────────
# ANÁLISIS DE IMAGEN
# ─────────────────────────────
if canvas_result.image_data is not None and api_key and analyze_button:

    with st.spinner("💭 Analizando tu dibujo..."):
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype('uint8')).convert('RGBA')
        input_image.save('img.png')

        base64_image = encode_image_to_base64("img.png")
        st.session_state.base64_image = base64_image

        prompt_text = "Describe en español brevemente la imagen"

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            max_tokens=300,
        )

        descripcion = response.choices[0].message.content
        st.markdown("### 💡 Interpretación de tu dibujo:")
        st.write(descripcion)

        st.session_state.full_response = descripcion
        st.session_state.analysis_done = True

# ─────────────────────────────
# GENERADOR INSTAGRAM
# ─────────────────────────────
if st.session_state.analysis_done:

    st.divider()
    st.subheader("📱 Generador de contenido para Instagram")

    tipo_contenido = st.selectbox(
        "Tipo de contenido",
        ["Reel", "Post", "Story"]
    )

    tono = st.selectbox(
        "Tono",
        ["Divertido", "Profesional", "Inspirador", "Vendedor", "Educativo"]
    )

    publico = st.text_input(
        "¿A quién va dirigido?",
        placeholder="Ej: emprendedores, mujeres jóvenes..."
    )

    if st.button("💖 Generar contenido viral"):

        with st.spinner("Creando magia... ✨"):

            prompt_instagram = f"""
            Basado en esta idea: {st.session_state.full_response}

            Crea un contenido para Instagram que incluya:

            - Hook llamativo
            - Idea del video/post
            - Guion paso a paso
            - Caption atractivo
            - Hashtags (5-8)
            - Call to Action

            Tipo: {tipo_contenido}
            Tono: {tono}
            Público: {publico}
            """

            response_ig = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt_instagram}],
                max_tokens=600,
            )

            resultado = response_ig.choices[0].message.content

            st.markdown("### ✨ Tu contenido listo:")
            st.markdown(resultado)

# ─────────────────────────────
# WARNING
# ─────────────────────────────
if not api_key:
    st.warning("⚠️ Ingresa tu API key para usar la app 💖")

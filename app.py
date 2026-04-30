import streamlit as st
import speech_recognition as sr
from groq import Groq
import os
from datetime import datetime
from fpdf import FPDF
from pydub import AudioSegment
from gtts import gTTS
import re

# 1. Configuración de Pantalla
st.set_page_config(page_title="Audio2Task Ultimate v3", page_icon="🏢", layout="wide")

# Barra Lateral: Configuración Visual y Accesibilidad
with st.sidebar:
    st.header("🎨 Estética y Foco")
    tema = st.selectbox("Ambiente:", ["Oficina Nocturna", "Modo Beige"])
    st.markdown("---")
    hablar = st.checkbox("🔊 Activar Narrador IA")
    st.info("💡 El fondo se difuminará automáticamente al procesar para mejorar la lectura.")

# Lógica de Colores de Alto Contraste (Cero Confusión Visual)
if tema == "Oficina Nocturna":
    bg_overlay = "rgba(0, 0, 0, 0.95)" # Casi opaco para resaltar texto
    text_main = "#F0F0F0"
    accent_color = "#00d2ff"
    container_bg = "#0D0D0D" # Fondo sólido negro
else:
    bg_overlay = "rgba(245, 245, 220, 0.98)"
    text_main = "#121212"
    accent_color = "#d35400"
    container_bg = "#FFFFFF" # Fondo sólido blanco

# Estilo CSS Avanzado: Corrección de Difuminado y Legibilidad
st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&q=80&w=2069");
        background-attachment: fixed;
        background-size: cover;
    }}
    .main {{
        background-color: {bg_overlay} !important;
        backdrop-filter: blur(50px); /* Difuminado máximo */
        transition: all 0.5s ease;
    }}
    .report-container {{
        background-color: {container_bg} !important;
        padding: 40px;
        border-radius: 15px;
        border-left: 10px solid {accent_color};
        color: {text_main} !important;
        box-shadow: 0 20px 40px rgba(0,0,0,0.5);
    }}
    h1, h2, h3, p, span, li {{
        color: {text_main} !important;
    }}
    .header-tag {{
        text-align: center;
        background: {accent_color};
        color: white !important;
        padding: 15px;
        border-radius: 10px;
        font-weight: 900;
        font-size: 1.5em;
        margin-bottom: 25px;
        text-transform: uppercase;
    }}
    </style>
    """, unsafe_allow_html=True)

# Encabezado con tu nombre (Visible y Grande)
st.markdown(f"<div class='header-tag'>Software desarrollado por Nicolas Gil Sanchez</div>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #888;'>Aprendiz ADSO | Ficha 3312447</h4>", unsafe_allow_html=True)
st.markdown(f"<h1 style='text-align: center; color: {accent_color} !important;'>🏢 AUDIO2TASK ULTIMATE</h1>", unsafe_allow_html=True)

# --- MOTOR TÉCNICO ---
def procesar_audio_avanzado(archivo, lang_in):
    audio = AudioSegment.from_file(archivo)
    audio.export("temp.wav", format="wav")
    r = sr.Recognizer()
    audio_wav = AudioSegment.from_wav("temp.wav")
    
    # Procesamiento por bloques de 45 seg para eficiencia
    duracion_ms = 45 * 1000 
    chunks = [audio_wav[i:i + duracion_ms] for i in range(0, len(audio_wav), duracion_ms)]
    texto_final = ""
    
    progreso = st.progress(0)
    for idx, chunk in enumerate(chunks):
        chunk.export("chunk.wav", format="wav")
        with sr.AudioFile("chunk.wav") as source:
            data = r.record(source)
            try:
                texto_final += r.recognize_google(data, language=lang_in) + " "
            except: pass
        progreso.progress((idx + 1) / len(chunks))
    return texto_final

# --- INTERFAZ DE USUARIO ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

col1, col2 = st.columns([1, 1.8])

with col1:
    st.subheader("📥 Configuración de Procesamiento")
    archivo = st.file_uploader("Sube Audio o Video (MP3, WAV, MP4, M4A)", type=["mp3", "wav", "m4a", "mp4"])
    
    # Selector de Flujo de Idioma Inteligente
    flujo = st.selectbox("🌐 Selecciona el flujo de traducción:", [
        "Audio Español ➡️ Texto Español",
        "Audio Inglés ➡️ Texto Español",
        "Audio Español ➡️ Texto Inglés",
        "Audio Inglés ➡️ Texto Inglés",
        "Audio Polaco ➡️ Texto Polaco",
        "Audio Polaco ➡️ Texto Español",
        "Audio Español ➡️ Texto Polaco"
    ])
    
    # Mapeo de lógica
    mapa = {
        "Audio Español ➡️ Texto Español": ("es-ES", "español"),
        "Audio Inglés ➡️ Texto Español": ("en-US", "español"),
        "Audio Español ➡️ Texto Inglés": ("es-ES", "inglés"),
        "Audio Inglés ➡️ Texto Inglés": ("en-US", "inglés"),
        "Audio Polaco ➡️ Texto Polaco": ("pl-PL", "polaco"),
        "Audio Polaco ➡️ Texto Español": ("pl-PL", "español"),
        "Audio Español ➡️ Texto Polaco": ("es-ES", "polaco")
    }
    lang_in, lang_out = mapa[flujo]

    if archivo:
        st.audio(archivo)
        if st.button("🚀 INICIAR ANÁLISIS"):
            with st.spinner(f"Analizando audio en {lang_in}..."):
                st.session_state['texto_raw'] = procesar_audio_avanzado(archivo, lang_in)

if 'texto_raw' in st.session_state:
    with col2:
        # CONTENEDOR DE RESULTADOS SÓLIDO (Sin transparencia molesta)
        st.markdown('<div class="report-container">', unsafe_allow_html=True)
        st.subheader("📋 Resultados del Análisis Profesional")
        
        prompt = f"""
        Analiza profundamente este texto: '{st.session_state['texto_raw']}'
        IDIOMA DE RESPUESTA: Debes responder OBLIGATORIAMENTE en idioma {lang_out.upper()}.
        
        ESTRUCTURA:
        1. TRANSCRIPCIÓN LIMPIA (Sin muletillas).
        2. RESUMEN EJECUTIVO (Puntos clave).
        3. MATRIZ DE TAREAS (Responsable, Tarea, Prioridad, Plazo sugerido).
        4. ANÁLISIS DE SENTIMIENTO (Tono de la conversación).
        """
        
        res = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama-3.3-70b-versatile")
        analisis = res.choices[0].message.content
        st.markdown(analisis)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Herramientas de Valor Añadido
        if hablar:
            gTTS(analisis.replace("|",""), lang=lang_in[:2]).save("voz.mp3")
            st.audio("voz.mp3")

        st.write("")
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        pdf_txt = analisis.encode('ascii', 'ignore').decode('ascii').replace('**', '').replace('###', '')
        pdf.multi_cell(0, 10, txt=pdf_txt)
        st.download_button("📥 Descargar Acta (PDF)", pdf.output(dest='S').encode('latin-1', 'replace'), "Acta_Audio2Task.pdf", "application/pdf")

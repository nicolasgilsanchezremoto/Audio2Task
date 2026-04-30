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
st.set_page_config(page_title="Audio2Task Ultimate Elite", page_icon="🏢", layout="wide")

# Selector de Tema y Estética
with st.sidebar:
    st.header("🎨 Estética y Foco")
    tema = st.selectbox("Elige el ambiente:", ["Oficina Nocturna", "Modo Beige"])
    st.markdown("---")
    hablar = st.checkbox("🔊 Activar Narrador IA")

# Lógica de Colores de Máxima Legibilidad
if tema == "Oficina Nocturna":
    bg_overlay = "rgba(0, 0, 0, 0.94)" # Casi negro total para no distraer
    text_main = "#F0F0F0"
    accent_color = "#00d2ff"
    container_bg = "#080808" # Fondo sólido
else:
    bg_overlay = "rgba(245, 245, 220, 0.96)"
    text_main = "#121212"
    accent_color = "#d35400"
    container_bg = "#FFFFFF"

# Estilo CSS con Fondo Oscurecido y Difuminado Pro
st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("https://images.unsplash.com/photo-1497215728101-856f4ea42174?auto=format&fit=crop&q=80&w=2070");
        background-attachment: fixed;
        background-size: cover;
    }}
    .main {{
        background-color: {bg_overlay} !important;
        backdrop-filter: blur(45px); /* Difuminado extremo para enfoque */
        color: {text_main};
    }}
    .report-container {{
        background-color: {container_bg} !important;
        padding: 45px;
        border-radius: 20px;
        border: 2px solid {accent_color};
        color: {text_main} !important;
        box-shadow: 0 25px 50px rgba(0,0,0,0.8);
        font-size: 1.1em;
    }}
    .header-box {{
        text-align: center;
        background: {accent_color};
        color: white !important;
        padding: 20px;
        border-radius: 15px;
        font-weight: 900;
        font-size: 1.8em;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    }}
    h1, h2, h3, p, li, span {{
        color: {text_main} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# Encabezado Requerido
st.markdown(f"<div class='header-box'>SOFTWARE DESARROLLADO POR NICOLAS GIL SANCHEZ</div>", unsafe_allow_html=True)
st.markdown("<h5 style='text-align: center; color: #777;'>Aprendiz ADSO | Ficha 3312447</h5>", unsafe_allow_html=True)
st.markdown(f"<h1 style='text-align: center; color: {accent_color} !important;'>🏢 AUDIO2TASK ULTIMATE</h1>", unsafe_allow_html=True)

# --- FUNCIONES TÉCNICAS ---
def procesar_audio_largo(archivo, lang_in):
    audio = AudioSegment.from_file(archivo)
    audio.export("temp.wav", format="wav")
    r = sr.Recognizer()
    audio_wav = AudioSegment.from_wav("temp.wav")
    
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

# --- INTERFAZ ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

col1, col2 = st.columns([1, 1.7])

with col1:
    st.subheader("📥 Panel de Control")
    archivo = st.file_uploader("Sube Audio o Video (MP3, WAV, MP4, M4A)", type=["mp3", "wav", "m4a", "mp4"])
    
    # Selector de Flujo de Traducción
    flujo = st.selectbox("🌐 Selecciona el flujo de idioma:", [
        "Audio Español ➡️ Texto Español",
        "Audio Inglés ➡️ Texto Español (Traducción)",
        "Audio Inglés ➡️ Texto Inglés",
        "Audio Español ➡️ Texto Inglés (Traducción)",
        "Audio Polaco ➡️ Texto Polaco",
        "Audio Polaco ➡️ Texto Español (Traducción)",
        "Audio Español ➡️ Texto Polaco (Traducción)"
    ])
    
    # Mapeo de lógica de idiomas
    mapa = {
        "Audio Español ➡️ Texto Español": ("es-ES", "español"),
        "Audio Inglés ➡️ Texto Español (Traducción)": ("en-US", "español"),
        "Audio Inglés ➡️ Texto Inglés": ("en-US", "inglés"),
        "Audio Español ➡️ Texto Inglés (Traducción)": ("es-ES", "inglés"),
        "Audio Polaco ➡️ Texto Polaco": ("pl-PL", "polaco"),
        "Audio Polaco ➡️ Texto Español (Traducción)": ("pl-PL", "español"),
        "Audio Español ➡️ Texto Polaco (Traducción)": ("es-ES", "polaco")
    }
    lang_in, lang_out = mapa[flujo]

    if archivo:
        st.audio(archivo)
        if st.button("🚀 INICIAR PROCESAMIENTO ELITE"):
            with st.spinner(f"Escuchando en {lang_in} y analizando..."):
                st.session_state['texto_base'] = procesar_audio_largo(archivo, lang_in)

if 'texto_base' in st.session_state:
    with col2:
        # CONTENEDOR CON FONDO SÓLIDO Y DIFUMINADO
        st.markdown('<div class="report-container">', unsafe_allow_html=True)
        st.subheader("📋 Resultados del Análisis Profesional")
        
        prompt = f"""
        Actúa como un experto lingüista y gestor de proyectos. 
        Analiza: '{st.session_state['texto_base']}'
        
        REGLA DE IDIOMA: Responde TODO el acta en {lang_out.upper()}.
        
        ESTRUCTURA REQUERIDA:
        1. TRANSCRIPCIÓN LIMPIA (Sin repeticiones).
        2. RESUMEN EJECUTIVO (Puntos principales).
        3. MATRIZ DE TAREAS (Responsable, Tarea, Prioridad, Plazo sugerido).
        4. DECISIONES CLAVE (Acuerdos finales).
        5. ANÁLISIS DE SENTIMIENTO (Tono de la reunión).
        """
        
        res = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama-3.3-70b-versatile")
        analisis = res.choices[0].message.content
        st.markdown(analisis)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Herramientas Finales
        if hablar:
            gTTS(analisis.replace("|",""), lang=lang_in[:2]).save("v.mp3")
            st.audio("v.mp3")

        st.write("")
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        # Limpiar para evitar errores de codificación en PDF
        clean_pdf_txt = analisis.encode('ascii', 'ignore').decode('ascii').replace('**', '').replace('###', '')
        pdf.multi_cell(0, 10, txt=clean_pdf_txt)
        st.download_button("📥 Descargar Acta Profesional (PDF)", pdf.output(dest='S').encode('latin-1', 'replace'), "Acta_Final.pdf", "application/pdf")

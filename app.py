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
st.set_page_config(page_title="Audio2Task Ultimate v4", page_icon="🏢", layout="wide")

# Selector de Tema
with st.sidebar:
    st.header("🎨 Estética y Foco")
    tema = st.selectbox("Elige el ambiente:", ["Pizarra Nocturna", "Modo Beige"])
    st.markdown("---")
    hablar = st.checkbox("🔊 Activar Narrador IA")

# Lógica de Colores de Máxima Visibilidad
if tema == "Pizarra Nocturna":
    bg_app = "#0E1117"  # Color oscuro sólido de Streamlit
    text_main = "#FFFFFF" # Blanco puro
    accent_color = "#00d2ff"
    container_bg = "#1A1C24" # Bloque sólido para el texto
    border_color = "#3a7bd5"
else:
    bg_app = "#F5F5DC"  # Beige sólido
    text_main = "#121212" # Negro profundo
    accent_color = "#d35400"
    container_bg = "#FFFFFF" # Blanco sólido
    border_color = "#e67e22"

# Estilo CSS de Alto Contraste (Sin distracciones de fondo)
st.markdown(f"""
    <style>
    .stApp {{
        background-color: {bg_app} !important;
    }}
    .report-container {{
        background-color: {container_bg} !important;
        padding: 40px;
        border-radius: 15px;
        border: 2px solid {border_color};
        color: {text_main} !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        margin-top: 20px;
    }}
    h1, h2, h3, h4, p, span, li, label {{
        color: {text_main} !important;
    }}
    .author-header {{
        background: linear-gradient(90deg, #00d2ff, #3a7bd5);
        color: white !important;
        padding: 20px;
        text-align: center;
        border-radius: 10px;
        font-weight: 900;
        font-size: 2em;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,210,255,0.3);
    }}
    </style>
    """, unsafe_allow_html=True)

# Encabezado Solicitado
st.markdown("<div class='author-header'>SOFTWARE DESARROLLADO POR NICOLAS GIL SANCHEZ</div>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #888;'>Aprendiz ADSO | Ficha 3312447</h4>", unsafe_allow_html=True)
st.markdown(f"<h1 style='text-align: center; color: {accent_color} !important;'>🎙️ AUDIO2TASK ULTIMATE</h1>", unsafe_allow_html=True)

# --- FUNCIONES TÉCNICAS ---
def procesar_audio(archivo, lang_in):
    audio = AudioSegment.from_file(archivo)
    audio.export("temp.wav", format="wav")
    r = sr.Recognizer()
    audio_wav = AudioSegment.from_wav("temp.wav")
    
    # Procesar por partes para audios largos (40 min)
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

col1, col2 = st.columns([1, 1.8])

with col1:
    st.subheader("📥 Carga y Configuración")
    archivo = st.file_uploader("Sube Audio o Video (MP3, WAV, MP4, M4A)", type=["mp3", "wav", "m4a", "mp4"])
    
    # NUEVO: Selector de Flujo Inteligente de Traducción
    flujo = st.selectbox("🌐 Elige el modo de traducción:", [
        "Audio Español ➡️ Texto Español",
        "Audio Inglés ➡️ Texto Español (Traducir)",
        "Audio Inglés ➡️ Texto Inglés",
        "Audio Español ➡️ Texto Inglés (Traducir)",
        "Audio Polaco ➡️ Texto Polaco",
        "Audio Polaco ➡️ Texto Español (Traducir)"
    ])
    
    mapa_idiomas = {
        "Audio Español ➡️ Texto Español": ("es-ES", "español"),
        "Audio Inglés ➡️ Texto Español (Traducir)": ("en-US", "español"),
        "Audio Inglés ➡️ Texto Inglés": ("en-US", "inglés"),
        "Audio Español ➡️ Texto Inglés (Traducir)": ("es-ES", "inglés"),
        "Audio Polaco ➡️ Texto Polaco": ("pl-PL", "polaco"),
        "Audio Polaco ➡️ Texto Español (Traducir)": ("pl-PL", "español")
    }
    idioma_in, idioma_out = mapa_idiomas[flujo]

    if archivo:
        st.audio(archivo)
        if st.button("🚀 INICIAR PROCESAMIENTO"):
            with st.spinner(f"Escuchando audio en {idioma_in}..."):
                st.session_state['texto_raw'] = procesar_audio(archivo, idioma_in)

if 'texto_raw' in st.session_state:
    with col2:
        # BLOQUE SÓLIDO PARA MÁXIMA LECTURA
        st.markdown('<div class="report-container">', unsafe_allow_html=True)
        st.subheader("📋 Resultados del Análisis Profesional")
        
        prompt = f"""
        Analiza el texto: '{st.session_state['texto_raw']}'
        IDIOMA DE RESPUESTA: Debes responder en {idioma_out.upper()}.
        
        ENTREGA:
        1. TRANSCRIPCIÓN LIMPIA (Sin errores).
        2. RESUMEN EJECUTIVO (Puntos clave).
        3. TABLA DE TAREAS (Responsable, Tarea, Prioridad, Fecha).
        4. ANÁLISIS DE SENTIMIENTO (Tono de la reunión).
        """
        
        res = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama-3.3-70b-versatile")
        analisis = res.choices[0].message.content
        st.markdown(analisis)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Herramientas Útiles
        if hablar:
            gTTS(analisis.replace("|",""), lang=idioma_in[:2]).save("voz.mp3")
            st.audio("voz.mp3")

        st.write("")
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        # Limpieza para exportación
        pdf_txt = analisis.encode('ascii', 'ignore').decode('ascii').replace('**', '').replace('###', '')
        pdf.multi_cell(0, 10, txt=pdf_txt)
        st.download_button("📥 Descargar Acta en PDF", pdf.output(dest='S').encode('latin-1', 'replace'), "Acta_Audio2Task.pdf", "application/pdf")

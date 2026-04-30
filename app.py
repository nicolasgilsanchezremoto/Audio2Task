import streamlit as st
import speech_recognition as sr
from groq import Groq
import os
from datetime import datetime
from fpdf import FPDF
from pydub import AudioSegment
from gtts import gTTS
import re

# 1. Configuración de Pantalla y Alto Contraste
st.set_page_config(page_title="Audio2Task Turbo", page_icon="⚡", layout="wide")

with st.sidebar:
    st.header("🎨 Estética y Foco")
    tema = st.selectbox("Elige el ambiente:", ["Pizarra Nocturna", "Modo Beige"])
    st.markdown("---")
    hablar = st.checkbox("🔊 Narrador IA")

if tema == "Pizarra Nocturna":
    bg_app = "#0A0B10"  # Negro ultra profundo
    text_main = "#FFFFFF"
    accent_color = "#00d2ff"
    container_bg = "#161B22" # Bloque sólido tipo código
    border_color = "#00d2ff"
else:
    bg_app = "#FDF6E3"  # Beige sólido premium
    text_main = "#121212"
    accent_color = "#d35400"
    container_bg = "#FFFFFF"
    border_color = "#d35400"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_app} !important; }}
    .report-container {{
        background-color: {container_bg} !important;
        padding: 35px;
        border-radius: 12px;
        border: 2px solid {border_color};
        color: {text_main} !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.6);
    }}
    h1, h2, h3, h4, p, span, li, label {{ color: {text_main} !important; }}
    .author-header {{
        background: linear-gradient(90deg, #00d2ff, #3a7bd5);
        color: white !important;
        padding: 15px;
        text-align: center;
        border-radius: 8px;
        font-weight: 900;
        font-size: 1.8em;
    }}
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='author-header'>SOFTWARE DESARROLLADO POR NICOLAS GIL SANCHEZ</div>", unsafe_allow_html=True)
st.markdown("<h5 style='text-align: center; color: #555;'>Aprendiz ADSO | Ficha 3312447</h5>", unsafe_allow_html=True)

# --- MOTOR DE ALTA VELOCIDAD ---
def procesar_audio_turbo(archivo, lang_in):
    audio = AudioSegment.from_file(archivo)
    audio.export("temp.wav", format="wav")
    r = sr.Recognizer()
    audio_wav = AudioSegment.from_wav("temp.wav")
    
    # Fragmentos más grandes (60s) para reducir latencia
    duracion_ms = 60 * 1000 
    chunks = [audio_wav[i:i + duracion_ms] for i in range(0, len(audio_wav), duracion_ms)]
    texto_final = ""
    
    progreso = st.progress(0)
    # Procesamiento optimizado
    for idx, chunk in enumerate(chunks):
        chunk_name = f"c_{idx}.wav"
        chunk.export(chunk_name, format="wav")
        with sr.AudioFile(chunk_name) as source:
            data = r.record(source)
            try:
                texto_final += r.recognize_google(data, language=lang_in) + " "
            except: pass
        os.remove(chunk_name) # Limpieza inmediata para velocidad
        progreso.progress((idx + 1) / len(chunks))
    
    return texto_final

# --- INTERFAZ ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

col1, col2 = st.columns([1, 1.8])

with col1:
    st.subheader("📥 Carga Rápida")
    archivo = st.file_uploader("Audio/Video (MP3, WAV, MP4, M4A)", type=["mp3", "wav", "m4a", "mp4"])
    
    flujo = st.selectbox("🌐 Traducción Inteligente:", [
        "Audio Español ➡️ Texto Español",
        "Audio Inglés ➡️ Texto Español (Traducir)",
        "Audio Inglés ➡️ Texto Inglés",
        "Audio Español ➡️ Texto Inglés (Traducir)",
        "Audio Polaco ➡️ Texto Polaco",
        "Audio Polaco ➡️ Texto Español (Traducir)"
    ])
    
    mapa = {
        "Audio Español ➡️ Texto Español": ("es-ES", "español"),
        "Audio Inglés ➡️ Texto Español (Traducir)": ("en-US", "español"),
        "Audio Inglés ➡️ Texto Inglés": ("en-US", "inglés"),
        "Audio Español ➡️ Texto Inglés (Traducir)": ("es-ES", "inglés"),
        "Audio Polaco ➡️ Texto Polaco": ("pl-PL", "polaco"),
        "Audio Polaco ➡️ Texto Español (Traducir)": ("pl-PL", "español")
    }
    idioma_in, idioma_out = mapa[flujo]

    if archivo:
        st.audio(archivo)
        if st.button("🚀 PROCESAMIENTO TURBO"):
            with st.spinner("IA trabajando a máxima velocidad..."):
                st.session_state['t_raw'] = procesar_audio_turbo(archivo, idioma_in)

if 't_raw' in st.session_state:
    with col2:
        st.markdown('<div class="report-container">', unsafe_allow_html=True)
        st.subheader("📋 Acta de Reunión Generada")
        
        # Uso de Llama 3.3 70B para análisis instantáneo
        prompt = f"Analiza: '{st.session_state['t_raw']}'. Responde en {idioma_out.upper()}. Incluye: Transcripción, Resumen, Tabla de Tareas y Sentimiento."
        
        res = client.chat.completions.create(
            messages=[{"role":"user","content":prompt}], 
            model="llama-3.3-70b-versatile",
            temperature=0.2 # Menor temperatura = mayor velocidad de respuesta
        )
        analisis = res.choices[0].message.content
        st.markdown(analisis)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if hablar:
            gTTS(analisis.replace("|",""), lang=idioma_in[:2]).save("v.mp3")
            st.audio("v.mp3")

        st.write("")
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        clean_txt = analisis.encode('ascii', 'ignore').decode('ascii').replace('**', '').replace('###', '')
        pdf.multi_cell(0, 10, txt=clean_txt)
        st.download_button("📥 Descargar PDF", pdf.output(dest='S').encode('latin-1', 'replace'), "Acta.pdf", "application/pdf")

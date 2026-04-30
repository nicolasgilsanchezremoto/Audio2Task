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
st.set_page_config(page_title="Audio2Task Global Turbo", page_icon="🌍", layout="wide")

with st.sidebar:
    st.header("🎨 Estética y Foco")
    tema = st.selectbox("Elige el ambiente:", ["Pizarra Nocturna", "Modo Beige"])
    st.markdown("---")
    hablar = st.checkbox("🔊 Narrador IA")

# Lógica de Colores de Máxima Visibilidad
if tema == "Pizarra Nocturna":
    bg_app = "#0A0B10"
    text_main = "#FFFFFF"
    accent_color = "#00d2ff"
    container_bg = "#161B22"
    border_color = "#00d2ff"
else:
    bg_app = "#FDF6E3"
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
    
    # Bloques de 60s para balancear velocidad y precisión
    duracion_ms = 60 * 1000 
    chunks = [audio_wav[i:i + duracion_ms] for i in range(0, len(audio_wav), duracion_ms)]
    texto_final = ""
    
    progreso = st.progress(0)
    for idx, chunk in enumerate(chunks):
        chunk_name = f"c_{idx}.wav"
        chunk.export(chunk_name, format="wav")
        with sr.AudioFile(chunk_name) as source:
            data = r.record(source)
            try:
                texto_final += r.recognize_google(data, language=lang_in) + " "
            except: pass
        os.remove(chunk_name)
        progreso.progress((idx + 1) / len(chunks))
    
    return texto_final

# --- INTERFAZ ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

col1, col2 = st.columns([1, 1.8])

with col1:
    st.subheader("📥 Carga Rápida Multilingüe")
    archivo = st.file_uploader("Audio/Video (MP3, WAV, MP4, M4A)", type=["mp3", "wav", "m4a", "mp4"])
    
    # Selector Extendido de Idiomas
    idioma_seleccionado = st.selectbox("🌐 Idioma del Audio:", [
        "Español", "Inglés", "Polaco", "Alemán", "Francés", 
        "Italiano", "Portugués", "Ruso", "Japonés", "Chino (Mandarín)"
    ])
    
    # Mapeo de códigos ISO
    iso_map = {
        "Español": "es-ES", "Inglés": "en-US", "Polaco": "pl-PL", 
        "Alemán": "de-DE", "Francés": "fr-FR", "Italiano": "it-IT", 
        "Portugués": "pt-BR", "Ruso": "ru-RU", "Japonés": "ja-JP", 
        "Chino (Mandarín)": "zh-CN"
    }
    
    idioma_in = iso_map[idioma_seleccionado]

    if archivo:
        st.audio(archivo)
        if st.button("🚀 PROCESAMIENTO TURBO"):
            with st.spinner(f"Analizando audio en {idioma_seleccionado}..."):
                st.session_state['t_raw'] = procesar_audio_turbo(archivo, idioma_in)

if 't_raw' in st.session_state:
    with col2:
        st.markdown('<div class="report-container">', unsafe_allow_html=True)
        st.subheader(f"📋 Resultados en {idioma_seleccionado}")
        
        # Llama 3.3 procesará el texto en el mismo idioma detectado
        prompt = f"Analiza el siguiente texto en {idioma_seleccionado}: '{st.session_state['t_raw']}'. Genera: 1. Transcripción limpia, 2. Resumen corto, 3. Tabla de tareas, 4. Sentimiento."
        
        res = client.chat.completions.create(
            messages=[{"role":"user","content":prompt}], 
            model="llama-3.3-70b-versatile",
            temperature=0.2
        )
        analisis = res.choices[0].message.content
        st.markdown(analisis)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if hablar:
            # gTTS usa los primeros dos caracteres del código ISO (ej: 'es', 'en', 'de')
            gTTS(analisis.replace("|",""), lang=idioma_in[:2]).save("v.mp3")
            st.audio("v.mp3")

        st.write("")
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        clean_txt = analisis.encode('ascii', 'ignore').decode('ascii').replace('**', '').replace('###', '')
        pdf.multi_cell(0, 10, txt=clean_txt)
        st.download_button("📥 Descargar PDF", pdf.output(dest='S').encode('latin-1', 'replace'), "Acta.pdf", "application/pdf")

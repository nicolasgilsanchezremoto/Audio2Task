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
st.set_page_config(page_title="Audio2Task Ultimate v2", page_icon="🏢", layout="wide")

# Selector de Tema en la barra lateral para no estorbar
with st.sidebar:
    st.header("🎨 Personalización")
    tema = st.selectbox("Elige el ambiente:", ["Oficina Nocturna", "Modo Beige"])

# Lógica de Colores Dinámica (Corregida)
if tema == "Oficina Nocturna":
    bg_overlay = "rgba(0, 0, 0, 0.75)"  # Fondo más oscuro para contraste
    text_main = "#ffffff"
    accent_color = "#00d2ff"
    container_color = "rgba(20, 20, 20, 0.85)"
else:
    bg_overlay = "rgba(245, 245, 220, 0.85)"
    text_main = "#2d3436"
    accent_color = "#d35400"
    container_color = "rgba(255, 255, 255, 0.9)"

# Estilo CSS Avanzado
st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&q=80&w=2069");
        background-attachment: fixed;
        background-size: cover;
    }}
    .main {{
        background-color: {bg_overlay};
        color: {text_main};
        padding: 30px;
        border-radius: 20px;
    }}
    .report-container {{
        background: {container_color};
        backdrop-filter: blur(20px);
        padding: 35px;
        border-radius: 30px;
        border: 2px solid {accent_color};
        color: {text_main};
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }}
    .header-text {{
        text-align: center;
        background: linear-gradient(90deg, #00d2ff, #3a7bd5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5em;
        font-weight: 900;
        margin-bottom: 0px;
    }}
    .sub-header {{
        text-align: center;
        color: {accent_color};
        font-size: 1.8em;
        font-weight: bold;
        margin-bottom: 20px;
    }}
    </style>
    """, unsafe_allow_html=True)

# Encabezado solicitado con nombre y ficha
st.markdown(f"<div class='sub-header'>Software desarrollado por Nicolas Gil Sanchez</div>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: gray;'>Aprendiz ADSO | Ficha 3312447</h4>", unsafe_allow_html=True)
st.markdown("<h1 class='header-text'>🏢 AUDIO2TASK ULTIMATE</h1>", unsafe_allow_html=True)

# --- FUNCIONES TÉCNICAS ---
def transcribir_avanzado(archivo, lang):
    audio = AudioSegment.from_file(archivo)
    ruta_wav = "temp_full.wav"
    audio.export(ruta_wav, format="wav")
    
    r = sr.Recognizer()
    audio_wav = AudioSegment.from_wav(ruta_wav)
    duracion_ms = 45 * 1000 
    chunks = [audio_wav[i:i + duracion_ms] for i in range(0, len(audio_wav), duracion_ms)]
    texto_final = ""
    
    progreso = st.progress(0)
    for idx, chunk in enumerate(chunks):
        chunk.export("chunk.wav", format="wav")
        with sr.AudioFile("chunk.wav") as source:
            data = r.record(source)
            try:
                texto_final += r.recognize_google(data, language=lang) + " "
            except: pass
        progreso.progress((idx + 1) / len(chunks))
    return texto_final

# --- INTERFAZ ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("📂 Entrada de Medios")
    archivo = st.file_uploader("Sube Audio o Video (MP3, WAV, MP4)", type=["mp3", "wav", "m4a", "mp4"])
    
    # Selector de idioma justo al lado de la entrada
    idioma_audio = st.selectbox("🌐 Idioma a procesar:", ["es-ES", "en-US", "fr-FR", "de-DE", "it-IT", "pt-BR"])
    
    if archivo:
        st.audio(archivo)
        if st.button("🚀 INICIAR ANÁLISIS"):
            with st.spinner(f"Analizando profundamente en {idioma_audio}..."):
                st.session_state['texto'] = transcribir_avanzado(archivo, idioma_audio)

if 'texto' in st.session_state:
    with col2:
        st.markdown('<div class="report-container">', unsafe_allow_html=True)
        st.subheader("📋 Resultados del Análisis")
        
        prompt_pro = f"""
        Actúa como Consultor Senior. Analiza: '{st.session_state['texto']}'
        1. TRANSCRIPCIÓN LIMPIA PROFESIONAL.
        2. RESUMEN EJECUTIVO.
        3. TABLA DE TAREAS (Responsable, Tarea, Fecha, Prioridad).
        4. DECISIONES Y ACUERDOS.
        5. ANÁLISIS DE SENTIMIENTO DE LA REUNIÓN.
        Responde en el idioma: {idioma_audio}.
        """
        
        res = client.chat.completions.create(messages=[{"role":"user","content":prompt_pro}], model="llama-3.3-70b-versatile")
        analisis_completo = res.choices[0].message.content
        st.markdown(analisis_completo)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Inclusividad en barra lateral para no romper diseño
        with st.sidebar:
            st.markdown("---")
            st.header("♿ Accesibilidad")
            hablar = st.checkbox("Activar Narrador")
        
        if hablar:
            gTTS(analisis_completo.replace("|", ""), lang=idioma_audio[:2]).save("final.mp3")
            st.audio("final.mp3")

        # Exportación PDF
        st.write("")
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        pdf_txt = analisis_completo.encode('ascii', 'ignore').decode('ascii').replace('**', '').replace('###', '')
        pdf.multi_cell(0, 10, txt=pdf_txt)
        st.download_button("📥 Descargar Acta PDF Profesional", pdf.output(dest='S').encode('latin-1', 'replace'), "Acta_Audio2Task.pdf", "application/pdf")

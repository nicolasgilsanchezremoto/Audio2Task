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
st.set_page_config(page_title="Audio2Task Ultimate", page_icon="🏢", layout="wide")

# Estilos CSS Avanzados para Legibilidad y Estética
st.markdown("""
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&q=80&w=2069");
        background-attachment: fixed;
        background-size: cover;
    }
    /* Capa oscura general para que el fondo no brille tanto */
    .main {
        background-color: rgba(0, 0, 0, 0.7);
        padding: 20px;
        border-radius: 15px;
    }
    /* Contenedor de resultados: Negro profundo para legibilidad total */
    .report-container {
        background: rgba(0, 0, 0, 0.92) !important;
        backdrop-filter: blur(20px);
        padding: 40px;
        border-radius: 20px;
        border: 2px solid #00d2ff;
        color: white !important;
        box-shadow: 0 15px 35px rgba(0,0,0,0.8);
        font-size: 1.1em;
        line-height: 1.6;
    }
    .header-main {
        text-align: center;
        color: #00fbff;
        font-size: 2.8em;
        font-weight: 900;
        text-shadow: 3px 3px 10px rgba(0,0,0,1);
        margin-bottom: 5px;
    }
    .sub-header-name {
        text-align: center;
        color: #00d2ff;
        font-size: 1.8em;
        font-weight: bold;
        text-shadow: 2px 2px 5px rgba(0,0,0,1);
    }
    /* Estilo para los textos de Streamlit que a veces se pierden */
    .stMarkdown p, .stMarkdown h3 {
        color: white !important;
        text-shadow: 1px 1px 2px black;
    }
    </style>
    """, unsafe_allow_html=True)

# Encabezados solicitados
st.markdown("<div class='sub-header-name'>SOFTWARE DESARROLLADO POR NICOLAS GIL SANCHEZ</div>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #bbbbbb;'>Aprendiz ADSO | Ficha 3312447</h4>", unsafe_allow_html=True)
st.markdown("<h1 class='header-main'>🎙️ AUDIO2TASK ULTIMATE</h1>", unsafe_allow_html=True)

# --- FUNCIONES TÉCNICAS ---
def transcribir_avanzado(archivo, lang_audio):
    audio = AudioSegment.from_file(archivo)
    ruta_wav = "temp_full.wav"
    audio.export(ruta_wav, format="wav")
    
    r = sr.Recognizer()
    audio_wav = AudioSegment.from_wav(ruta_wav)
    # Fragmentos de 45 seg para no saturar la API gratuita
    duracion_ms = 45 * 1000 
    chunks = [audio_wav[i:i + duracion_ms] for i in range(0, len(audio_wav), duracion_ms)]
    texto_final = ""
    
    progreso = st.progress(0)
    for idx, chunk in enumerate(chunks):
        chunk.export("chunk.wav", format="wav")
        with sr.AudioFile("chunk.wav") as source:
            data = r.record(source)
            try:
                texto_final += r.recognize_google(data, language=lang_audio) + " "
            except: pass
        progreso.progress((idx + 1) / len(chunks))
    return texto_final

# --- INTERFAZ ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("📂 Configuración de Procesamiento")
    archivo = st.file_uploader("Sube Audio o Video (MP3, WAV, MP4, M4A)", type=["mp3", "wav", "m4a", "mp4"])
    
    # Opciones de Idioma Cruzado
    idioma_entrada = st.selectbox("🎙️ ¿En qué idioma está el AUDIO?", 
                                 options=["es-ES", "en-US", "fr-FR", "pt-BR"], 
                                 index=0)
    
    idioma_salida = st.selectbox("📄 ¿En qué idioma quieres el TEXTO final?", 
                                options=["Español", "Inglés", "Francés", "Portugués"], 
                                index=0)

    if archivo:
        st.audio(archivo)
        if st.button("🚀 INICIAR TRADUCCIÓN E INTELIGENCIA"):
            with st.spinner(f"Escuchando en {idioma_entrada} y traduciendo..."):
                st.session_state['texto_crudo'] = transcribir_avanzado(archivo, idioma_entrada)

if 'texto_crudo' in st.session_state:
    with col2:
        st.markdown('<div class="report-container">', unsafe_allow_html=True)
        st.subheader(f"📋 Análisis en {idioma_salida}")
        
        # Prompt dinámico que obliga a la traducción
        prompt_ia = f"""
        Actúa como un traductor y consultor experto. 
        Toma este texto: '{st.session_state['texto_crudo']}'
        TRADÚCELO COMPLETAMENTE AL IDIOMA {idioma_salida} y genera:
        1. TRANSCRIPCIÓN LIMPIA Y CORREGIDA.
        2. RESUMEN EJECUTIVO.
        3. TABLA DE TAREAS (Responsable, Tarea, Fecha, Prioridad).
        4. CONCLUSIONES.
        Toda la respuesta debe estar en {idioma_salida}.
        """
        
        res = client.chat.completions.create(messages=[{"role":"user","content":prompt_ia}], model="llama-3.3-70b-versatile")
        analisis = res.choices[0].message.content
        st.markdown(analisis)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Narrador IA
        with st.sidebar:
            st.markdown("---")
            hablar = st.checkbox("📢 Escuchar Resultados")
        
        if hablar:
            # Diccionario para gTTS
            lang_tts = {"Español": "es", "Inglés": "en", "Francés": "fr", "Portugués": "pt"}
            gTTS(analisis.replace("|", ""), lang=lang_tts[idioma_salida]).save("final.mp3")
            st.audio("final.mp3")

        # Exportación
        st.write("")
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        # Limpieza para evitar errores en PDF
        pdf_txt = analisis.encode('ascii', 'ignore').decode('ascii').replace('**', '').replace('###', '')
        pdf.multi_cell(0, 10, txt=pdf_txt)
        st.download_button("📥 Descargar Acta Profesional", pdf.output(dest='S').encode('latin-1', 'replace'), "Acta_Final.pdf", "application/pdf")

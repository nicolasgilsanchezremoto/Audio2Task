import streamlit as st
import speech_recognition as sr
from groq import Groq
import os
from datetime import datetime
from fpdf import FPDF
from pydub import AudioSegment
from gtts import gTTS
import re

# 1. Configuración de Pantalla y Temas Personalizados
st.set_page_config(page_title="Audio2Task Ultimate", page_icon="🏢", layout="wide")

# Selector de Tema en la barra lateral
with st.sidebar:
    st.header("🎨 Personalización")
    tema = st.selectbox("Elige el ambiente:", ["Oficina Nocturna", "Modo Beige"])
    idioma_audio = st.selectbox("Idioma del audio:", ["es-ES", "en-US", "fr-FR", "de-DE", "it-IT", "pt-BR"])

# Definición de Colores según el Tema
if tema == "Oficina Nocturna":
    bg_color = "rgba(30, 30, 47, 0.85)"
    text_color = "#ffffff"
    container_bg = "rgba(255, 255, 255, 0.05)"
else:
    bg_color = "rgba(245, 245, 220, 0.9)"
    text_color = "#2d3436"
    container_bg = "rgba(0, 0, 0, 0.05)"

# Estilo CSS Avanzado con Imagen de Fondo
st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&q=80&w=2069");
        background-attachment: fixed;
        background-size: cover;
    }}
    .main {{
        background-color: {bg_color};
        color: {text_color};
        padding: 20px;
        border-radius: 15px;
    }}
    .report-container {{
        background: {container_bg};
        backdrop-filter: blur(15px);
        padding: 30px;
        border-radius: 25px;
        border: 1px solid rgba(255,255,255,0.2);
        color: {text_color};
    }}
    .header-text {{
        text-align: center;
        background: linear-gradient(90deg, #00d2ff, #3a7bd5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3em;
        font-weight: 900;
    }}
    </style>
    """, unsafe_allow_html=True)

# Encabezado ADSO
st.markdown("<h3 style='text-align: center; color: #00d2ff;'>Sistema desarrollado por el aprendiz del tecnólogo ADSO</h3>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: gray;'>Nicolas Gil Sanchez | Ficha 3312447</h4>", unsafe_allow_html=True)
st.markdown("<h1 class='header-text'>🏢 AUDIO2TASK ULTIMATE</h1>", unsafe_allow_html=True)

# --- FUNCIONES TÉCNICAS MEJORADAS ---
def transcribir_avanzado(archivo, lang):
    audio = AudioSegment.from_file(archivo)
    ruta_wav = "temp_full.wav"
    audio.export(ruta_wav, format="wav")
    
    r = sr.Recognizer()
    audio_wav = AudioSegment.from_wav(ruta_wav)
    # Fragmentación para mayor precisión
    duracion_ms = 45 * 1000 
    chunks = [audio_wav[i:i + duracion_ms] for i in range(0, len(audio_wav), duracion_ms)]
    texto_final = ""
    
    progreso = st.progress(0)
    for idx, chunk in enumerate(chunks):
        chunk.export("chunk.wav", format="wav")
        with sr.AudioFile("chunk.wav") as source:
            data = r.record(source)
            try:
                # Usa el idioma seleccionado
                texto_final += r.recognize_google(data, language=lang) + " "
            except: pass
        progreso.progress((idx + 1) / len(chunks))
    return texto_final

# --- INTERFAZ DE USUARIO ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

with st.sidebar:
    st.header("♿ Accesibilidad")
    tamano = st.radio("Lectura:", ["Normal", "Grande"])
    hablar = st.checkbox("Activar Narrador IA")
    f_size = "22px" if tamano == "Grande" else "18px"
    st.markdown(f"<style>p, li, span {{ font-size: {f_size} !important; }}</style>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("📂 Entrada de Medios")
    archivo = st.file_uploader("Sube cualquier formato (MP3, WAV, MP4, M4A)", type=["mp3", "wav", "m4a", "mp4"])
    if archivo:
        st.audio(archivo)
        if st.button("🚀 INICIAR PROCESAMIENTO"):
            with st.spinner(f"Analizando audio en {idioma_audio}..."):
                st.session_state['texto'] = transcribir_avanzado(archivo, idioma_audio)

if 'texto' in st.session_state:
    with col2:
        st.markdown('<div class="report-container">', unsafe_allow_html=True)
        st.subheader("📋 Resultados del Análisis Inteligente")
        
        # Petición de IA Multi-función
        prompt_pro = f"""
        Actúa como un Consultor de Negocios Senior. Analiza este texto: '{st.session_state['texto']}'
        1. TRANSCRIPCIÓN LIMPIA (Corrige errores gramaticales).
        2. RESUMEN EJECUTIVO (Puntos clave).
        3. TABLA DE TAREAS (Responsable, Tarea, Fecha, Prioridad).
        4. DECISIONES TOMADAS (Lista de acuerdos finales).
        5. ANÁLISIS DE SENTIMIENTO (¿Cómo fue el tono de la reunión?).
        Idiomas: Responde en el mismo idioma que el texto original.
        """
        
        res = client.chat.completions.create(messages=[{"role":"user","content":prompt_pro}], model="llama-3.3-70b-versatile")
        analisis_completo = res.choices[0].message.content
        st.markdown(analisis_completo)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Audio-guía Inclusiva
        if hablar:
            gTTS(analisis_completo.replace("|", ""), lang=idioma_audio[:2]).save("final.mp3")
            st.audio("final.mp3")

        # Descargas
        st.write("")
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        # Limpieza básica para el PDF
        pdf_txt = analisis_completo.encode('ascii', 'ignore').decode('ascii').replace('**', '').replace('###', '')
        pdf.multi_cell(0, 10, txt=pdf_txt)
        st.download_button("📥 Exportar Acta Profesional (PDF)", pdf.output(dest='S').encode('latin-1', 'replace'), "Acta_Elite.pdf", "application/pdf")

import streamlit as st
import speech_recognition as sr
from groq import Groq
import os
from datetime import datetime
from fpdf import FPDF
from pydub import AudioSegment
from gtts import gTTS
import re

# 1. Configuración y Estilo Animado (MODO ELITE)
st.set_page_config(page_title="Audio2Task Pro Elite", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #1e1e2f 0%, #2d3436 100%);
        color: #ffffff;
    }
    .stButton>button {
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
        border: none; color: white; font-weight: bold;
        border-radius: 50px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .report-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        padding: 25px;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.1);
        color: white;
    }
    .header-text {
        text-align: center;
        background: -webkit-linear-gradient(#00d2ff, #3a7bd5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
    }
    </style>
    """, unsafe_allow_html=True)

# Encabezado del Autor
st.markdown("<h3 style='text-align: center; color: #00d2ff; margin-bottom: 0;'>Sistema desarrollado por el aprendiz del tecnólogo ADSO</h3>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #ffffff; margin-top: 0;'>Nicolas Gil Sanchez | Ficha 3312447</h4>", unsafe_allow_html=True)
st.markdown("<h1 class='header-text'>🎙️ AUDIO2TASK PRO ELITE</h1>", unsafe_allow_html=True)

# --- FUNCIONES TÉCNICAS ---
def limpiar_para_pdf(texto):
    texto_limpio = texto.encode('ascii', 'ignore').decode('ascii')
    return texto_limpio.replace('###', '').replace('**', '').replace('|', ' ')

def convertir_a_wav(archivo_entrada):
    audio = AudioSegment.from_file(archivo_entrada)
    ruta_temporal = "temp_audio_pro.wav"
    audio.export(ruta_temporal, format="wav")
    return ruta_temporal

def transcribir_por_partes(ruta_wav):
    r = sr.Recognizer()
    audio = AudioSegment.from_wav(ruta_wav)
    # Trozos de 60 segundos para no bloquear el sistema gratuito
    duracion_ms = 60 * 1000 
    chunks = [audio[i:i + duracion_ms] for i in range(0, len(audio), duracion_ms)]
    texto_completo = ""
    barra_progreso = st.progress(0)
    for idx, chunk in enumerate(chunks):
        chunk.export("chunk.wav", format="wav")
        with sr.AudioFile("chunk.wav") as source:
            data = r.record(source)
            try:
                texto_completo += r.recognize_google(data, language="es-ES") + " "
            except: pass
        barra_progreso.progress((idx + 1) / len(chunks))
    return texto_completo

# --- INTERFAZ ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

with st.sidebar:
    st.header("♿ Accesibilidad")
    tamano = st.radio("Tamaño de letra:", ["Normal", "Grande", "Extra Grande"])
    hablar = st.checkbox("Lector de voz (Inclusivo)")
    font_size = "18px" if tamano == "Normal" else "24px" if tamano == "Grande" else "32px"
    st.markdown(f"<style>p, span, li {{ font-size: {font_size} !important; }}</style>", unsafe_allow_html=True)

col_izq, col_der = st.columns([1, 1.5])

with col_izq:
    st.subheader("📁 Cargar Reunión")
    archivo = st.file_uploader("Audio (MP3, WAV, M4A)", type=["mp3", "wav", "m4a"])
    if archivo:
        st.audio(archivo)
        if st.button("🚀 INICIAR ANÁLISIS"):
            with st.spinner("Procesando inteligencia artificial..."):
                ruta = convertir_a_wav(archivo)
                st.session_state['transcripcion'] = transcribir_por_partes(ruta)

if 'transcripcion' in st.session_state:
    with col_der:
        # Aquí empieza el cuadro iluminado
        st.markdown('<div class="report-container">', unsafe_allow_html=True)
        
        st.subheader("📝 Transcripción Detectada")
        st.write(st.session_state['transcripcion'])
        
        st.markdown("---")
        
        # Llamada a la IA
        prompt = f"Resume esta reunión y haz una tabla de tareas (Responsable, Tarea, Fecha, Prioridad): {st.session_state['transcripcion']}. Hoy es 28 de Abril 2026."
        res = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama-3.3-70b-versatile")
        analisis = res.choices[0].message.content
        
        st.subheader("📋 Plan de Acción")
        st.markdown(analisis)
        
        st.markdown('</div>', unsafe_allow_html=True) # Aquí termina el cuadro iluminado
        
        # Lector de voz inclusivo
        if hablar:
            gTTS(analisis.replace("|",""), lang='es').save("voz.mp3")
            st.audio("voz.mp3")

        # Botón PDF (Corregido sin st.ln)
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=10)
            pdf.multi_cell(0, 10, txt=limpiar_para_pdf(analisis))
            pdf_bytes = pdf.output(dest='S').encode('latin-1', 'replace')
            st.write("") # Espacio en blanco correcto
            st.download_button("📥 Descargar Acta PDF", pdf_bytes, "Acta_Reunion.pdf", "application/pdf")
        except:
            st.download_button("📥 Descargar Respaldo (Texto)", analisis, "Acta.txt")

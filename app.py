import streamlit as st
import speech_recognition as sr
from groq import Groq
import os
from datetime import datetime
from fpdf import FPDF
from pydub import AudioSegment
from gtts import gTTS
import re

# 1. Configuración de la página con Estilo Animado
st.set_page_config(page_title="Audio2Task Pro Elite", page_icon="🚀", layout="wide")

# CSS para Interfaz Entretenida y Animada
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;500;900&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Roboto', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #1e1e2f 0%, #2d3436 100%);
        color: #ffffff;
    }
    
    .stButton>button {
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
        border: none;
        color: white;
        font-weight: bold;
        transition: all 0.3s ease;
        border-radius: 50px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 20px rgba(0,210,255,0.5);
    }
    
    .report-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        padding: 30px;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.1);
        margin-top: 20px;
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

# Encabezado Requerido
st.markdown(f"<h3 style='text-align: center; color: #00d2ff;'>Sistema desarrollado por el aprendiz del tecnólogo ADSO</h3>", unsafe_allow_html=True)
st.markdown(f"<h4 style='text-align: center; color: #ffffff;'>Nicolas Gil Sanchez | Ficha 3312447</h4>", unsafe_allow_html=True)
st.markdown("<h1 class='header-text'>🎙️ AUDIO2TASK PRO ELITE</h1>", unsafe_allow_html=True)

# 2. Funciones de Procesamiento de Audio (Largo y Multinivel)
def convertir_a_wav(archivo_entrada):
    """Convierte cualquier formato de audio a WAV compatible"""
    audio = AudioSegment.from_file(archivo_entrada)
    nombre_wav = "temp_converted.wav"
    audio.export(nombre_wav, format="wav")
    return nombre_wav

def transcribir_audio_largo(ruta_audio):
    """Divide audios largos en partes para evitar bloqueos"""
    r = sr.Recognizer()
    audio = AudioSegment.from_wav(ruta_audio)
    
    # Dividir en trozos de 60 segundos
    duracion_chunk = 60 * 1000 
    chunks = [audio[i:i + duracion_chunk] for i in range(0, len(audio), duracion_chunk)]
    
    texto_completo = ""
    progreso = st.progress(0)
    
    for idx, chunk in enumerate(chunks):
        chunk.export("chunk.wav", format="wav")
        with sr.AudioFile("chunk.wav") as source:
            data = r.record(source)
            try:
                texto = r.recognize_google(data, language="es-ES")
                texto_completo += texto + " "
            except:
                pass
        progreso.progress((idx + 1) / len(chunks))
    
    return texto_completo

# 3. Función PDF Corregida (Usando Fuente Estándar)
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Acta de Tareas - Generado por Audio2Task', 0, 1, 'C')

def generar_pdf_seguro(transcripcion, analitica):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    
    # Limpieza extrema de caracteres no-latin1
    def safe_text(t):
        return t.encode('latin-1', 'replace').decode('latin-1')

    pdf.cell(0, 10, "1. TRANSCRIPCION", ln=True)
    pdf.multi_cell(0, 5, safe_text(transcripcion))
    pdf.ln(10)
    pdf.cell(0, 10, "2. ANALISIS DE IA", ln=True)
    pdf.multi_cell(0, 5, safe_text(analitica))
    
    return pdf.output(dest='S').encode('latin-1')

# 4. Interfaz de Usuario
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Opciones de Inclusividad
with st.sidebar:
    st.header("♿ Inclusividad")
    tamano = st.radio("Tamaño de texto:", ["Normal", "Grande", "Extra Grande"])
    activar_voz = st.checkbox("Activar Lector de Resultados (Voz)")
    
    if tamano == "Grande": font_val = "22px"
    elif tamano == "Extra Grande": font_val = "30px"
    else: font_val = "18px"
    
    st.markdown(f"<style>p, li, span {{ font-size: {font_val} !important; }}</style>", unsafe_allow_html=True)

col_carga, col_result = st.columns([1, 1.5])

with col_carga:
    st.subheader("📁 Cargar Reunión")
    archivo_subido = st.file_uploader("Sube MP3, WAV, M4A, etc.", type=["mp3", "wav", "m4a", "ogg"])
    
    if archivo_subido:
        st.audio(archivo_subido)
        if st.button("🚀 ANALIZAR AHORA"):
            with st.spinner("Procesando audio largo (esto puede tardar unos minutos)..."):
                # Paso 1: Convertir
                ruta_wav = convertir_a_wav(archivo_subido)
                # Paso 2: Transcribir trozo a trozo
                texto_total = transcribir_audio_largo(ruta_wav)
                st.session_state['texto_voz'] = texto_total

if 'texto_voz' in st.session_state:
    with col_result:
        st.markdown('<div class="report-container">', unsafe_allow_html=True)
        st.subheader("📝 Transcripción Detectada")
        st.write(st.session_state['texto_voz'])
        
        # Procesar con IA
        prompt = f"Analiza esta reunión: '{st.session_state['texto_voz']}'. Crea un Resumen Ejecutivo y una Tabla de Tareas (Responsable, Tarea, Plazo, Prioridad). Fecha hoy: 28 de Abril 2026."
        
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile"
        )
        
        analisis = res.choices[0].message.content
        st.markdown("---")
        st.subheader("📋 Resultados de la IA")
        st.markdown(analisis)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Función Inclusiva: Lector de Voz
        if activar_voz:
            tts = gTTS(analisis.replace("|", ""), lang='es')
            tts.save("resumen.mp3")
            st.audio("resumen.mp3")

        # Botón PDF Seguro
        try:
            pdf_bytes = generar_pdf_seguro(st.session_state['texto_voz'], analisis)
            st.download_button("📥 Descargar Acta en PDF", pdf_bytes, "Acta.pdf", "application/pdf")
        except:
            st.download_button("📥 Descargar (Respaldo Texto)", analisis, "Acta.txt")

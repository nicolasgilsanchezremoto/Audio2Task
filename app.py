import streamlit as st
import speech_recognition as sr
from groq import Groq
import os
from pydub import AudioSegment

# 1. Configuración Ultra Ligera
st.set_page_config(page_title="Audio2Task Flash", page_icon="⚡", layout="wide")

# Estilo Minimalista de Alto Contraste (Cero distracciones)
st.markdown("""
    <style>
    .stApp { background-color: #0E1117 !important; }
    .report-container {
        background-color: #161B22 !important;
        padding: 25px;
        border-radius: 10px;
        border: 1px solid #00d2ff;
        color: white !important;
    }
    .author-header {
        background: #00d2ff;
        color: black !important;
        padding: 10px;
        text-align: center;
        font-weight: 900;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='author-header'>SOFTWARE DESARROLLADO POR NICOLAS GIL SANCHEZ - ADSO</div>", unsafe_allow_html=True)

# --- MOTOR ULTRA RÁPIDO ---
def procesar_audio_flash(archivo, lang):
    # Carga y conversión inmediata
    audio = AudioSegment.from_file(archivo)
    audio.export("t.wav", format="wav")
    r = sr.Recognizer()
    audio_wav = AudioSegment.from_wav("t.wav")
    
    # Bloques de 90 segundos para máxima velocidad
    duracion_ms = 90 * 1000 
    chunks = [audio_wav[i:i + duracion_ms] for i in range(0, len(audio_wav), duracion_ms)]
    texto_final = ""
    
    progreso = st.progress(0)
    for idx, chunk in enumerate(chunks):
        chunk.export("c.wav", format="wav")
        with sr.AudioFile("c.wav") as source:
            data = r.record(source)
            try:
                # Transcripción directa (sin traducción)
                texto_final += r.recognize_google(data, language=lang) + " "
            except: pass
        progreso.progress((idx + 1) / len(chunks))
    return texto_final

# --- INTERFAZ SIMPLIFICADA ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("📥 Carga de Archivo")
    archivo = st.file_uploader("Sube Audio o Video", type=["mp3", "wav", "mp4", "m4a"])
    
    idioma = st.radio("🌐 Idioma del Audio:", ["es-ES", "en-US", "pl-PL"], horizontal=True)

    if archivo and st.button("🚀 PROCESAR AHORA"):
        with st.spinner("IA analizando..."):
            st.session_state['texto_flash'] = procesar_audio_flash(archivo, idioma)

if 'texto_flash' in st.session_state:
    with col2:
        st.markdown('<div class="report-container">', unsafe_allow_html=True)
        st.subheader("📋 Resultados")
        
        # Prompt simplificado para respuesta instantánea
        prompt = f"Analiza rápido en {idioma}: '{st.session_state['texto_flash']}'. Resumen y Tabla de tareas corta."
        
        res = client.chat.completions.create(
            messages=[{"role":"user","content":prompt}], 
            model="llama-3.3-70b-versatile",
            temperature=0, # Respuesta determinística y más rápida
            max_tokens=500 # Limita la salida para ganar segundos
        )
        st.markdown(res.choices[0].message.content)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("🗑️ Limpiar para otra prueba"):
            del st.session_state['texto_flash']
            st.rerun()

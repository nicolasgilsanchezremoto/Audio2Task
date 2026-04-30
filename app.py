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

# Selector de Tema
with st.sidebar:
    st.header("🎨 Estética y Foco")
    tema = st.selectbox("Ambiente:", ["Oficina Nocturna", "Modo Beige"])
    st.markdown("---")
    st.info("💡 Consejo: Usa el Modo Beige si prefieres texto oscuro sobre fondo claro.")

# Lógica de Colores de Alto Contraste
if tema == "Oficina Nocturna":
    bg_overlay = "rgba(0, 0, 0, 0.92)" # Casi negro para eliminar distracciones
    text_main = "#ECECEC"
    accent_color = "#00d2ff"
    container_bg = "#0A0A0A" # Fondo sólido para el texto
else:
    bg_overlay = "rgba(245, 245, 220, 0.95)"
    text_main = "#0D0D0D"
    accent_color = "#d35400"
    container_bg = "#FFFFFF"

# Estilo CSS con Enfoque en Legibilidad y Difuminado
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
        padding: 40px;
        backdrop-filter: blur(40px); /* Difuminado extremo para concentración */
    }}
    .report-container {{
        background: {container_bg};
        padding: 45px;
        border-radius: 20px;
        border: 3px solid {accent_color};
        color: {text_main};
        box-shadow: 0 30px 60px rgba(0,0,0,0.8);
        font-size: 1.1em;
    }}
    .header-title {{
        text-align: center;
        color: {accent_color};
        font-size: 2.8em;
        font-weight: 900;
        text-transform: uppercase;
        margin-bottom: 5px;
    }}
    .author-badge {{
        text-align: center;
        background: {accent_color};
        color: white;
        padding: 10px;
        border-radius: 10px;
        font-weight: bold;
        font-size: 1.4em;
        margin-bottom: 20px;
    }}
    </style>
    """, unsafe_allow_html=True)

# Encabezado con mayor visibilidad
st.markdown(f"<div class='author-badge'>SOFTWARE DESARROLLADO POR NICOLAS GIL SANCHEZ</div>", unsafe_allow_html=True)
st.markdown("<h5 style='text-align: center; color: gray;'>Aprendiz ADSO | Ficha 3312447</h5>", unsafe_allow_html=True)
st.markdown("<h1 class='header-title'>AUDIO2TASK ULTIMATE</h1>", unsafe_allow_html=True)

# --- LÓGICA TÉCNICA ---
def procesar_audio(archivo, lang_audio):
    audio = AudioSegment.from_file(archivo)
    ruta_wav = "temp.wav"
    audio.export(ruta_wav, format="wav")
    
    r = sr.Recognizer()
    audio_wav = AudioSegment.from_wav(ruta_wav)
    # Fragmentar para mayor eficiencia en archivos de 40min
    duracion_ms = 40 * 1000 
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

col1, col2 = st.columns([1, 1.8])

with col1:
    st.subheader("📥 Configuración de Entrada")
    archivo = st.file_uploader("Sube Audio o Video (MP3, WAV, MP4, M4A)", type=["mp3", "wav", "m4a", "mp4"])
    
    # Selector de Flujo de Idioma
    modo = st.selectbox("🌐 Elige el flujo de trabajo:", [
        "Audio Español ➡️ Texto Español",
        "Audio Inglés ➡️ Texto Español (Traducción)",
        "Audio Inglés ➡️ Texto Inglés",
        "Audio Español ➡️ Texto Inglés (Traducción)"
    ])
    
    # Mapeo de idiomas según la elección
    lang_map = {
        "Audio Español ➡️ Texto Español": ("es-ES", "español"),
        "Audio Inglés ➡️ Texto Español (Traducción)": ("en-US", "español"),
        "Audio Inglés ➡️ Texto Inglés": ("en-US", "inglés"),
        "Audio Español ➡️ Texto Inglés (Traducción)": ("es-ES", "inglés")
    }
    lang_audio, lang_target = lang_map[modo]

    if archivo:
        st.audio(archivo)
        if st.button("🚀 INICIAR PROCESAMIENTO"):
            with st.spinner("Analizando y traduciendo..."):
                st.session_state['texto_crudo'] = procesar_audio(archivo, lang_audio)

if 'texto_crudo' in st.session_state:
    with col2:
        st.markdown('<div class="report-container">', unsafe_allow_html=True)
        st.subheader("📝 Resultados Profesionales")
        
        prompt = f"""
        Actúa como un experto lingüista y gestor de proyectos. 
        Analiza el siguiente texto: '{st.session_state['texto_crudo']}'
        
        INSTRUCCIÓN DE IDIOMA: Debes entregar todo el análisis en {lang_target.upper()}.
        
        CONTENIDO A ENTREGAR:
        1. TRANSCRIPCIÓN LIMPIA Y CORREGIDA.
        2. RESUMEN EJECUTIVO (Puntos principales).
        3. TABLA DE TAREAS (Responsable, Tarea, Fecha Límite, Prioridad).
        4. ANÁLISIS DE SENTIMIENTO Y TONO.
        """
        
        res = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama-3.3-70b-versatile")
        analisis = res.choices[0].message.content
        st.markdown(analisis)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Funciones Útiles Adicionales
        st.write("")
        col_pdf, col_voice = st.columns(2)
        
        with col_voice:
            if st.checkbox("🔊 Narrar resultados"):
                gTTS(analisis.replace("|",""), lang=lang_audio[:2]).save("v.mp3")
                st.audio("v.mp3")

        with col_pdf:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=10)
            # Limpiar caracteres especiales para el PDF
            clean_txt = analisis.encode('ascii', 'ignore').decode('ascii').replace('**', '').replace('###', '')
            pdf.multi_cell(0, 10, txt=clean_txt)
            st.download_button("📥 Descargar Acta (PDF)", pdf.output(dest='S').encode('latin-1', 'replace'), "Acta.pdf", "application/pdf")

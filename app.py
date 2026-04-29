import streamlit as st
import speech_recognition as sr
from groq import Groq
import os
from datetime import datetime
from fpdf import FPDF
import re

# 1. Configuración de la página y Estilo Profesional (CSS)
st.set_page_config(page_title="Audio2Task Pro", page_icon="🎙️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #007bff; color: white; }
    .stDownloadButton>button { border-radius: 20px; background-color: #28a745; color: white; }
    .report-container { background-color: white; padding: 30px; border-radius: 15px; border: 1px solid #e6e9ef; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN DE LIMPIEZA PARA PDF (Evita el UnicodeEncodeError) ---
def limpiar_para_pdf(texto):
    """Limpia emojis y caracteres extraños que rompen la librería FPDF básica"""
    # Eliminar emojis y caracteres no ASCII
    texto_limpio = texto.encode('ascii', 'ignore').decode('ascii')
    # Limpiar formato Markdown para que sea legible en el PDF
    texto_limpio = texto_limpio.replace('###', '').replace('**', '').replace('|', ' ').replace('-', '•')
    # Eliminar múltiples espacios en blanco
    texto_limpio = re.sub(r' +', ' ', texto_limpio)
    return texto_limpio

# 2. Lógica para Generación de PDF Profesional
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Acta de Reunion Inteligente - Audio2Task', 0, 1, 'C')
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Generado el: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'R')
        self.ln(10)

def generar_pdf(transcripcion, analitica):
    pdf = PDF()
    pdf.add_page()
    
    # 1. Sección Transcripción
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(0, 123, 255)
    pdf.cell(0, 10, '1. TRANSCRIPCION DEL AUDIO', 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(0, 0, 0)
    
    # Limpieza específica para la transcripción
    pdf.multi_cell(0, 7, limpiar_para_pdf(transcripcion))
    
    pdf.ln(10)
    
    # 2. Sección Análisis e IA
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(0, 123, 255)
    pdf.cell(0, 10, '2. RESUMEN Y MATRIZ DE TAREAS', 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(0, 0, 0)
    
    # Limpieza específica para el análisis de la IA
    pdf.multi_cell(0, 7, limpiar_para_pdf(analitica))
    
    # El uso de 'latin-1' con 'replace' asegura que el programa no se detenga por errores
    return pdf.output(dest='S').encode('latin-1', errors='replace')

# 3. Funciones de Audio
def transcribir_audio(archivo):
    r = sr.Recognizer()
    with sr.AudioFile(archivo) as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        audio = r.record(source)
    try:
        return r.recognize_google(audio, language="es-ES")
    except:
        return "No se pudo detectar voz clara en el archivo."

# 4. Interfaz de Usuario
st.title("🎙️ Audio2Task Pro: Gestión Inclusiva")
st.write(f"Sesión activa: {datetime.now().strftime('%d/%m/%Y')}")

# Funciones Inclusivas (Accesibilidad)
with st.expander("⚙️ Opciones de Accesibilidad"):
    fuente_size = st.select_slider("Tamaño de texto para lectura", options=["Pequeño", "Normal", "Grande"], value="Normal")
    if fuente_size == "Grande":
        st.markdown("<style>p, li { font-size: 20px !important; }</style>", unsafe_allow_html=True)

# Cliente Groq
client = Groq(api_key="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")

col_input, col_output = st.columns([1, 2])

with col_input:
    st.subheader("📥 Carga de Datos")
    uploaded_file = st.file_uploader("Subir archivo .wav", type=["wav"])
    boton = st.button("🚀 Iniciar Análisis")
    
    if uploaded_file:
        st.audio(uploaded_file)

if uploaded_file and boton:
    with st.spinner("IA analizando timbre de voz y compromisos..."):
        # PASO 1: Transcripción
        texto_voz = transcribir_audio(uploaded_file)
        
        with col_output:
            st.markdown('<div class="report-container">', unsafe_allow_html=True)
            
            st.subheader("📝 Transcripción del Audio")
            st.info(texto_voz)
            
            st.markdown("---")
            
            # PASO 2: IA para Resumen y Tabla
            prompt = f"""
            Actúa como un experto en productividad. Analiza: '{texto_voz}'
            1. Genera un RESUMEN EJECUTIVO potente.
            2. Genera una TABLA DE TAREAS (Responsable, Tarea, Fecha Límite, Prioridad).
            Usa nombres detectados como Nicolás o Marco. Hoy es Miércoles 22 de Abril de 2026.
            Responde en formato Markdown claro.
            """
            
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.3
            )
            
            resultado_ia = chat_completion.choices[0].message.content
            st.markdown(resultado_ia)
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.write("") 
            
            # PASO 3: Descarga PDF (Corregido)
            try:
                pdf_data = generar_pdf(texto_voz, resultado_ia)
                st.download_button(
                    label="📥 Descargar Acta Completa en PDF",
                    data=pdf_data,
                    file_name=f"Acta_Audio2Task_{datetime.now().strftime('%H%M%S')}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Error al generar el PDF: {e}")
                # Opción de respaldo en texto si el PDF falla
                st.download_button("Descargar en Texto (Respaldo)", resultado_ia, file_name="acta.txt")
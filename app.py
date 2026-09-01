import os
import streamlit as st
from google import genai
from pypdf import PdfReader

# 1. Configuración de la página
st.set_page_config(page_title="FranPy - Tutor de Python", page_icon="🐍")

# 2. Configuración segura de la API Key
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ No se encontró la API Key de Gemini. Configúrala en los Secrets de Streamlit o como variable de entorno.")
    st.stop()

client = genai.Client(api_key=api_key)

# 3. Extraer texto del PDF
@st.cache_data
def cargar_contenido_pdf(ruta_pdf):
    texto_acumulado = ""
    try:
        lector = PdfReader(ruta_pdf)
        for pagina in lector.pages:
            texto_extraido = pagina.extract_text()
            if texto_extraido:
                texto_acumulado += texto_extraido + "\n"
    except Exception:
        pass
    return texto_acumulado

nombre_pdf = "capitulos.pdf" 
contenido_material = cargar_contenido_pdf(nombre_pdf)

# 4. Mantener el historial del chat en la sesión
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- PANEL DE CONTROL (BARRA LATERAL) ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/python.png", width=80)
    
    # Contador de mensajes de la sesión actual (Límite preventivo de 80)
    num_mensajes = sum(1 for m in st.session_state.messages if m["role"] == "user")
    st.markdown("---")
    st.metric(label="Tus mensajes en esta sesión", value=f"{num_mensajes} / 80")

    st.markdown("---")
    st.subheader("📚 Material de Estudio")
    if os.path.exists(nombre_pdf):
        with open(nombre_pdf, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()
        st.download_button(
            label="📄 Descargar Capítulos (PDF)",
            data=pdf_bytes,
            file_name="Capitulos_Python_Franco_Hilt.pdf",
            mime="application/pdf"
        )
    else:
        st.info("Sube tu archivo PDF al repositorio para habilitar la descarga.")

    st.markdown("---")
    if st.button("🗑️ Reiniciar conversación", type="primary"):
        st.session_state.messages = []
        st.rerun()

# Título principal de la app
st.title("🐍 FranPy: Tu Tutor Personal")
st.write("¡Hola! Estoy aquí para guiarte paso a paso y ayudarte a encontrar la solución por ti mismo.")

# 5. Definir el System Prompt integrando tu material
system_prompt = f"""
Eres FranPy, un profesor de programación en Python paciente, motivador y amigable, enfocado en estudiantes de secundaria.

MATERIAL DE ESTUDIO OFICIAL DEL PROFESOR (Usa esto como tu referencia principal de explicaciones y ejemplos):
{{
{contenido_material}
}}

Reglas estrictas que debes seguir:
1. Prioriza los conceptos, ejemplos y la estructura explicada en el material de estudio oficial del profesor provisto arriba.
2. NUNCA des el código completamente resuelto de los ejercicios o tareas.
3. Usa el método socrático: haz preguntas orientadoras y pistas paso a paso para que el alumno descubra la solución por sí mismo.
4. Tienes libertad para ayudar con dudas generales de sintaxis de Python o errores de código que los alumnos presenten, manteniendo siempre el nivel secundario.
5. Explica los errores usando analogías sencillas y cotidianas y celebra los pequeños avances del estudiante.
"""

# Mostrar historial de mensajes
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Control de Límite de mensajes por sesión
LIMITE_MENSAJES = 80

if num_mensajes >= LIMITE_MENSAJES:
    st.warning("⚠️ Has alcanzado el límite de mensajes recomendados para esta sesión. Por favor, usa el botón **'Reiniciar conversación'** en el panel lateral para continuar practicando.")
else:
    # Entrada normal del usuario
    user_input = st.chat_input("¿Qué duda tienes sobre tu código de Python?")
    
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Pensando una pista para ti..."):
                try:
                    # Traducimos los roles de Streamlit ('assistant' -> 'model') para que Gemini los acepte
                    chat_history = []
                    for m in st.session_state.messages[:-1]:
                        gemini_role = "model" if m["role"] == "assistant" else "user"
                        chat_history.append({"role": gemini_role, "parts": [{"text": m["content"]}]})
                    
                    response = client.models.generate_content(
                        model='gemini-1.5-flash',
                        contents=chat_history if chat_history else user_input,
                        config={
                            'system_instruction': system_prompt,
                            'temperature': 0.7,
                        }
                    )
                    
                    bot_response = response.text
                    st.markdown(bot_response)
                    st.session_state.messages.append({"role": "assistant", "content": bot_response})
                    
                except Exception as e:
                    error_str = str(e)
                    if "429" in error_str or "ResourceExhausted" in error_str:
                        st.warning("⏳ FranPy está recibiendo muchas consultas al mismo tiempo. Espera 10 segundos y vuelve a enviar tu mensaje.")
                    else:
                        st.error(f"Ocurrió un error técnico: {error_str}")
        
        st.rerun()

# Pie de página con humor
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>🐍 Un error de sintaxis no te define como persona (todavía) — F.H</div>", 
    unsafe_allow_html=True
)

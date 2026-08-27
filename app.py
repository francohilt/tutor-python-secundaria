import os
import streamlit as st
from google import genai

st.set_page_config(page_title="FranPy - Tutor de Python", page_icon="🐍")

st.title("🐍 FranPy: Tu Tutor Personal")
st.write("¡Hola! Estoy aquí para ayudarte a aprender a programar desde cero paso a paso, guiándote para que encuentres la solución por ti mismo.")
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ No se encontró la API Key de Gemini. Configúrala en los Secrets de Streamlit o como variable de entorno.")
    st.stop()

client = genai.Client(api_key=api_key)

with st.sidebar:
    st.image("https://img.icons8.com/color/96/python.png", width=80)
    st.title("Panel de Control")
    st.write("Tu asistente personal de programación.")
    st.markdown("---")
    st.markdown("**Desarrollado por:**<br>Prof. Franco Hilt", unsafe_allow_html=True)    
    st.markdown("---")
    if st.button("🗑️ Reiniciar conversación", type="primary"):
        st.session_state.messages = []
        st.rerun()
        
system_prompt = """
Eres un profesor de programación en Python paciente, motivador y amigable, enfocado en estudiantes de escuela secundaria.
Reglas estrictas que debes seguir:
1. NUNCA des el código completamente resuelto de los ejercicios o tareas.
2. Usa el método socrático: haz preguntas orientadoras y pistas paso a paso para que el alumno descubra la solución por sí mismo.
3. Limítate estrictamente a conceptos básicos de secundaria: variables, tipos de datos, condicionales (if/else), bucles (while/for) y funciones simples. No hables de temas avanzados a menos que el alumno lo pida de forma expresa.
4. Explica los errores y conceptos técnicos usando analogías sencillas de la vida cotidiana.
5. Celebra los pequeños avances del estudiante para mantener su motivación alta.
"""

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_input := st.chat_input("¿Qué duda tienes sobre tu código de Python?"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Pensando una pista para ti..."):
            try:
                chat_history = [{"role": m["role"], "parts": [{"text": m["content"]}]} for m in st.session_state.messages]
                response = client.models.generate_content(
                    model='gemini-3.6-flash', 
                    contents=chat_history,
                    config={
                        'system_instruction': system_prompt,
                        'temperature': 0.7,
                    }
                )
                
                bot_response = response.text
                st.markdown(bot_response)
                
                st.session_state.messages.append({"role": "model", "content": bot_response})
                
            except Exception as e:
                st.error(f"Ocurrió un error al conectar con la IA: {e}")

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>Creado con ❤️ por el Prof. Franco Hilt para clases de programación</div>", 
    unsafe_allow_html=True
)

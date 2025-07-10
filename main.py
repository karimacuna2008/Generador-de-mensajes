import streamlit as st
from openai import OpenAI

# ————— Configuración general —————
st.set_page_config(page_title="Generador de Prompt Dinámico", layout="centered")
st.title("🖋️ Generador de Prompt Dinámico")

# ————— Cliente OpenAI —————
MODEL_NAME = "gpt-4.1-mini"

# Lee la API key que configuraste en Streamlit Share
api_key = st.secrets["OPENAI_API_KEY"]
client  = OpenAI(api_key=api_key)

# ————— Parámetros en la barra lateral —————
with st.sidebar:
    st.header("⚙️ Configuración del Prompt")
    tipo_mensaje     = st.radio("Tipo de mensaje", ["Correo", "Mensaje de Whatsapp/Mensajería instantánea"])
    incluir_disculpa = st.radio("¿Incluir disculpa?", ["Sí", "No"])
    tipo_disculpa    = None
    if incluir_disculpa == "Sí":
        tipo_disculpa = st.radio("Tipo de disculpa", ["Error propio", "Error ajeno"])
    longitud = st.radio(
        "Longitud máxima",
        {
            "Corto (40 palabras)": "40 palabras",
            "Normal (70 palabras)": "70 palabras",
            "Largo (100 palabras)": "100 palabras",
        }
    )

# ————— Campos de contenido del mensaje —————
st.subheader("✏️ Contenido del mensaje")
st.write(f"Api {api_key}")
motivo      = st.text_area("Motivo del mensaje TEST", placeholder="Describe brevemente el motivo...")
acciones    = st.text_area("Acciones en curso", placeholder="¿Qué se está haciendo para resolverlo?")
solucion    = st.text_area("Solución / Próximos pasos", placeholder="¿Qué solución o pasos sigue?")
guia        = st.text_input("Número de guía (opcional)")
datos_extra = st.text_input("Datos extra (opcional)")

# ————— Construye el prompt —————
def build_prompt() -> str:
    p = (
        f"Eres un asistente que redacta mensajes al cliente en un tono formal y muy amable.\n"
        f"El mensaje será un {tipo_mensaje}.\n"
        f"La longitud máxima del mensaje debe ser de {longitud}.\n\n"
        "Deberás generar un único mensaje en español que incluya:\n"
        "1. Una breve explicación del motivo.\n"
        "2. Una descripción de las acciones en curso o lo que se está haciendo para resolver el problema.\n"
        "3. La solución que se aplicará o los próximos pasos a seguir.\n"
        "4. Si se proporciona número de guía, menciona cuál es.\n"
        "5. Debes mencionar los datos extra, donde consideres que deba ir mejor en el texto.\n"
    )
    if incluir_disculpa == "Sí":
        if tipo_disculpa == "Error ajeno":
            apology = 'Al inicio incluye una disculpa corta, por ejemplo "Lamentamos los inconvenientes".'
        else:
            apology = (
                'Al inicio incluye una disculpa un poco más larga, '
                'por ejemplo: "Lamentamos que este error haya sido un inconveniente; '
                'estamos implementando medidas para evitarlo en el futuro."'
            )
    else:
        apology = "No incluyas ninguna disculpa."
    p += f"6. {apology}\n\n"
    #p += (
    #    "Será un mensaje por whatsapp o mensajería, así que será de corrido "
    #    "y un poco menos formal que un correo.\nInicia con un saludo."
    #)
    return p

# ————— Mostrar el prompt generado —————
if st.button("🔎 Ver Prompt generado"):
    txt = build_prompt()
    st.subheader("📝 Prompt final para la API")
    st.code(txt, language="markdown")

    st.subheader("📋 Contenido ingresado")
    st.markdown(
        f"- **Motivo:** {motivo or '_(vacío)_'}  \n"
        f"- **Acciones en curso:** {acciones or '_(vacío)_'}  \n"
        f"- **Solución / Próximos pasos:** {solucion or '_(vacío)_'}  \n"
        f"- **Número de guía:** {guia or 'N/A'}  \n"
        f"- **Datos extra:** {datos_extra or 'N/A'}"
    )

# ————— Llamada a la API para generar el mensaje —————
if st.button("📨 Generar mensaje con OpenAI"):
    prompt_text = build_prompt()
    user_input  = (
        f"Motivo: {motivo}\n"
        f"Acciones: {acciones}\n"
        f"Solución: {solucion}\n"
        f"Número de guía: {guia or 'N/A'}\n"
        f"Datos extra: {datos_extra or 'N/A'}"
    )
    with st.spinner("Generando mensaje…"):
        resp = client.responses.create(
            model=MODEL_NAME,
            instructions=prompt_text,
            input=user_input,
        )
    st.subheader("💬 Mensaje generado")
    st.write(resp.output_text)

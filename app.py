import streamlit as st
import os
import tempfile
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from agent.agent import AgenteFacturas

# ── CONFIG ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Agente de Facturas 🧾",
    page_icon="🧾",
    layout="wide"
)

# ── ESTADO ───────────────────────────────────────────────────────
if "agente" not in st.session_state:
    st.session_state.agente = AgenteFacturas()

if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

if "facturas_cargadas" not in st.session_state:
    st.session_state.facturas_cargadas = False

# ── HEADER ───────────────────────────────────────────────────────
st.title("🧾 Agente de Facturas")
st.caption("Sube tus facturas o boletas y pregúntame lo que quieras sobre tus gastos.")

# ── SIDEBAR — CARGA DE ARCHIVOS ──────────────────────────────────
with st.sidebar:
    st.header("📁 Cargar Facturas")

    archivos = st.file_uploader(
        "Sube tus facturas (PDF o imagen)",
        type=["pdf", "jpg", "jpeg", "png"],
        accept_multiple_files=True,
        help="Puedes subir varias facturas a la vez"
    )

    if archivos and st.button("⚡ Procesar Facturas", type="primary"):
        with st.spinner("Analizando facturas con IA..."):
            # Guardar archivos temporalmente
            with tempfile.TemporaryDirectory() as tmpdir:
                for archivo in archivos:
                    ruta = os.path.join(tmpdir, archivo.name)
                    with open(ruta, "wb") as f:
                        f.write(archivo.getbuffer())

                n = st.session_state.agente.cargar_archivos(tmpdir)

            if n > 0:
                st.session_state.facturas_cargadas = True
                st.success(f"✅ {n} factura(s) procesadas")

                # Mostrar tabla resumen
                facturas = st.session_state.agente.facturas
                st.subheader("Facturas procesadas")
                for f in facturas:
                    st.write(f"• **{f.proveedor}** — S/ {f.total:.2f}")
            else:
                st.error("No se pudo procesar ninguna factura.")

    st.divider()

    # Exportar Excel
    if st.session_state.facturas_cargadas:
        if st.button("📊 Exportar a Excel"):
            ruta = "output/facturas.xlsx"
            os.makedirs("output", exist_ok=True)
            st.session_state.agente.exportar(ruta)
            with open(ruta, "rb") as f:
                st.download_button(
                    "⬇️ Descargar Excel",
                    data=f,
                    file_name="facturas.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    st.divider()
    st.caption("Stack: LangChain · GPT-4o · Streamlit · openpyxl")

# ── CHAT ─────────────────────────────────────────────────────────
# Mostrar historial
for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Sugerencias rápidas si hay facturas cargadas
if st.session_state.facturas_cargadas and not st.session_state.mensajes:
    st.subheader("💡 Puedes preguntarme:")
    col1, col2, col3 = st.columns(3)
    sugerencias = [
        "¿Cuánto gasté en total?",
        "¿Cuál es mi top 3 de proveedores?",
        "¿Hay facturas duplicadas?",
        "¿Cuánto gasté en Servicios?",
        "Dame un resumen general",
        "Busca facturas de internet",
    ]
    for i, sug in enumerate(sugerencias):
        col = [col1, col2, col3][i % 3]
        with col:
            if st.button(sug, key=f"sug_{i}"):
                st.session_state.mensajes.append({"role": "user", "content": sug})
                with st.spinner("Analizando..."):
                    respuesta = st.session_state.agente.preguntar(sug)
                st.session_state.mensajes.append({"role": "assistant", "content": respuesta})
                st.rerun()

# Input del usuario
if prompt := st.chat_input(
    "Pregúntame sobre tus facturas..." if st.session_state.facturas_cargadas
    else "Primero sube tus facturas en el panel izquierdo 👈"
):
    if not st.session_state.facturas_cargadas:
        st.warning("Primero sube y procesa tus facturas.")
    else:
        # Mostrar mensaje del usuario
        st.session_state.mensajes.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Respuesta del agente
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                respuesta = st.session_state.agente.preguntar(prompt)
            st.markdown(respuesta)

        st.session_state.mensajes.append({"role": "assistant", "content": respuesta})
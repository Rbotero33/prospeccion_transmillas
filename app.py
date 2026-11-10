"""
Prospección comercial B2B con IA — Transmillas
Ejecutar:  streamlit run app.py
"""

import streamlit as st

import config
from core import db, ia_local
from paginas import cargar, contacto, prospectos, tablero, usabilidad
from ui import asistente, nav
from ui import estilos as ui

st.set_page_config(page_title="Transmillas · Prospección B2B", page_icon=":material/local_shipping:",
                   layout="wide")
db.inicializar()
ui.aplicar()


@st.cache_data(ttl=10, show_spinner=False)
def ia_disponible():
    return ia_local.disponible()


# --------------------------------------------------------------------------- páginas

MENU = [
    ("tablero", "Tablero", ":material/space_dashboard:", tablero.pagina),
    ("cargar", "Cargar empresas", ":material/domain_add:", cargar.pagina),
    ("prospectos", "Prospectos priorizados", ":material/leaderboard:", prospectos.pagina),
    ("contacto", "Contacto y seguimiento", ":material/forum:", contacto.pagina),
    ("usabilidad", "Pruebas de usabilidad", ":material/timer:", usabilidad.pagina),
]
nav.PAGINAS = {
    clave: st.Page(funcion, title=titulo, icon=icono, url_path=clave, default=(clave == "tablero"))
    for clave, titulo, icono, funcion in MENU
}
actual = st.navigation(list(nav.PAGINAS.values()), position="hidden")
st.session_state["pagina_actual"] = next(c for c, t, _, _ in MENU if t == actual.title)
st.session_state["ia_ok"] = ia_disponible()

# --------------------------------------------------------------------------- barra lateral

with st.sidebar:
    ui.marca()
    for clave, titulo, icono, _ in MENU:
        activo = actual.title == titulo
        with st.container(key="nav_activo" if activo else f"nav_{clave}"):
            st.page_link(nav.PAGINAS[clave], label=titulo, icon=icono)
    ui.etiqueta_lateral("Sesión")
    st.text_input("Asesor comercial", value="Asesor Transmillas", key="asesor")
    ui.estado_ia(st.session_state["ia_ok"], config.OLLAMA_MODELO)

# --------------------------------------------------------------------------- contenido

actual.run()
asistente.flotante()

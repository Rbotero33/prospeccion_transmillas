"""Asistente de IA flotante: un botón en la esquina que abre un chat sobre los prospectos."""

import pandas as pd
import streamlit as st

import config
from core import ia_local
from paginas import comun
from ui import estilos as ui

CAMPOS = ["razon_social", "ciudad", "sector", "ciiu", "tamano", "frecuencia", "regiones", "puntaje",
          "prioridad", "estado", "contacto_nombre", "contacto_cargo", "descripcion", "justificacion"]
PAGINAS_CON_EMPRESA = ("prospectos", "contacto")

SUGERENCIAS = {
    "empresa": [
        "Redacta 3 preguntas para la primera llamada con esta empresa.",
        "¿Qué servicio de Transmillas le ofrecerías primero y por qué?",
        "Resume en 3 líneas por qué es o no es un buen prospecto.",
    ],
    "grupo": [
        "¿Con cuáles 3 empresas empezarías esta semana y por qué?",
        "Agrupa estas empresas por el servicio de Transmillas que más les serviría.",
        "¿Qué datos nos faltan de estas empresas para priorizarlas mejor?",
    ],
}
SIN_RESPUESTA = ("No pude obtener respuesta de la IA local. Verifique que Ollama esté en ejecución "
                 "e intente de nuevo.")


# --------------------------------------------------------------------------- estado

def _alternar():
    st.session_state["chat_abierto"] = not st.session_state.get("chat_abierto", False)


def _limpiar():
    st.session_state["chat_historial"] = []


def _pedir(texto):
    st.session_state["chat_pendiente"] = texto


# --------------------------------------------------------------------------- contexto

def _opciones(df):
    """Sobre qué empresas conversa el asistente."""
    ss = st.session_state
    opciones = {}
    pid = ss.get("prospecto_actual")
    if (ss.get("pagina_actual") in PAGINAS_CON_EMPRESA and not df.empty and pid in set(df["id"])):
        nombre = df.loc[df["id"] == pid, "razon_social"].iloc[0]
        opciones["empresa"] = f"En pantalla: {nombre}"
    opciones["A"] = "Prospectos de prioridad A"
    opciones["AB"] = "Prospectos de prioridad A y B"
    return opciones


def _contexto(df, modo):
    if df.empty:
        return "No hay prospectos cargados todavía."
    if modo == "empresa":
        seleccion = df[df["id"] == st.session_state.get("prospecto_actual")]
    elif modo == "A":
        seleccion = df[df["prioridad"] == "A"].head(10)
    else:
        seleccion = df[df["prioridad"].isin(["A", "B"])].head(12)
    if seleccion.empty:
        return "No hay prospectos en este grupo."
    return "\n".join(
        "- " + "; ".join(f"{c}: {r[c]}" for c in CAMPOS if pd.notna(r[c]) and str(r[c]).strip())
        for _, r in seleccion.iterrows())


# --------------------------------------------------------------------------- interfaz

def _quitar_espera(trozos, espera):
    """Borra los puntos de 'escribiendo' cuando llega el primer fragmento de la respuesta."""
    primero = True
    for trozo in trozos:
        if primero:
            espera.empty()
            primero = False
        yield trozo


def _responder(cuerpo, peticion, contexto):
    historial = st.session_state["chat_historial"]
    historial.append({"role": "user", "content": peticion})
    with cuerpo:
        with st.chat_message("user", avatar=":material/person:"):
            st.markdown(peticion)
        with st.chat_message("assistant", avatar=":material/smart_toy:"):
            espera = st.empty()
            espera.html('<div class="tm-dots" aria-label="Escribiendo"><i></i><i></i><i></i></div>')
            try:
                respuesta = st.write_stream(_quitar_espera(ia_local.chatear_stream(historial, contexto), espera))
            except Exception:
                respuesta = ""
            if not isinstance(respuesta, str) or not respuesta.strip():
                espera.empty()
                respuesta = SIN_RESPUESTA
                st.markdown(respuesta)
    historial.append({"role": "assistant", "content": respuesta})


def _panel(ia_ok):
    ss = st.session_state
    df = comun.prospectos()
    with st.container(key="tm_chat"):
        with st.container(key="tm_chat_head"):
            a, b = st.columns([7, 1], vertical_alignment="center")
            estado = (f'<div class="tm-chat-s on"><i></i>IA local · {ui.e(config.OLLAMA_MODELO)}</div>' if ia_ok
                      else '<div class="tm-chat-s"><i></i>IA local inactiva</div>')
            a.html(f'<div class="tm-chat-h"><div class="tm-chat-a">{ui.icono("robot", 21)}</div><div>'
                   f'<div class="tm-chat-n">Asistente Transmillas</div>{estado}</div></div>')
            b.button("", icon=":material/restart_alt:", key="chat_limpiar", on_click=_limpiar,
                     help="Nueva conversación")

        with st.container(key="tm_chat_ctx"):
            opciones = _opciones(df)
            if ss.get("chat_empresa_vista") != ss.get("prospecto_actual"):
                ss["chat_empresa_vista"] = ss.get("prospecto_actual")
                if "empresa" in opciones:
                    ss["chat_contexto"] = "empresa"
            if ss.get("chat_contexto") not in opciones:
                ss["chat_contexto"] = next(iter(opciones))
            modo = st.selectbox("Conversar sobre", list(opciones), format_func=opciones.get,
                                key="chat_contexto", label_visibility="collapsed")

        with st.container(key="tm_chat_body"):
            cuerpo = st.container(height=300, border=False)
        with cuerpo:
            bienvenida = st.empty()
            if not ss["chat_historial"] and not ss.get("chat_pendiente"):
                with bienvenida.container():
                    if ia_ok:
                        st.html('<div class="tm-chat-hi"><b>Hola.</b> Puedo analizar los prospectos, sugerir a '
                                'quién contactar y redactar mensajes. Escriba su petición o elija una:</div>')
                        with st.container(key="tm_chat_sug"):
                            grupo = "empresa" if modo == "empresa" else "grupo"
                            for i, texto in enumerate(SUGERENCIAS[grupo]):
                                st.button(texto, key=f"chat_sug_{grupo}_{i}", icon=":material/bolt:",
                                          on_click=_pedir, args=(texto,), width="stretch")
                    else:
                        st.html('<div class="tm-chat-hi"><b>La IA local está inactiva.</b> Inicie Ollama en este '
                                'equipo para conversar con el asistente.</div>')
            for mensaje in ss["chat_historial"]:
                avatar = ":material/smart_toy:" if mensaje["role"] == "assistant" else ":material/person:"
                with st.chat_message(mensaje["role"], avatar=avatar):
                    st.markdown(mensaje["content"])

        with st.container(key="tm_chat_in"):
            escrito = st.chat_input("Escriba su petición…", key="chat_entrada", disabled=not ia_ok)

        peticion = ss.pop("chat_pendiente", None) or escrito
        if peticion and ia_ok:
            bienvenida.empty()
            _responder(cuerpo, peticion, _contexto(df, modo))


@st.fragment
def flotante():
    """Botón flotante + panel de chat. Al ser un fragmento, abrir o escribir no recarga la página."""
    ss = st.session_state
    ss.setdefault("chat_abierto", False)
    ss.setdefault("chat_historial", [])
    ia_ok = comun.ia_activa()
    if ss["chat_abierto"]:
        _panel(ia_ok)
    with st.container(key="tmfab_abierto" if ss["chat_abierto"] else "tmfab_cerrado"):
        st.button("", icon=":material/close:" if ss["chat_abierto"] else ":material/smart_toy:",
                  key="asistente_boton", on_click=_alternar,
                  help="Cerrar asistente" if ss["chat_abierto"] else "Asistente de IA")

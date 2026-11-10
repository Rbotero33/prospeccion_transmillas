"""Pruebas de usabilidad: cronómetro por tarea, cuestionario SUS y resultados."""

import time

import streamlit as st

from core import db, usabilidad
from ui import estilos as ui


def pagina():
    ui.encabezado("Pruebas de usabilidad")
    with st.container(key="card_usabilidad"):
        t_reg, t_sus, t_res = st.tabs([":material/timer: Registrar tareas", ":material/fact_check: Cuestionario SUS",
                                       ":material/insights: Resultados"])

        with t_reg:
            a, b = st.columns(2)
            participante = a.text_input("Participante", st.session_state.get("participante", ""),
                                        icon=":material/person:")
            st.session_state["participante"] = participante
            rol = b.text_input("Rol", "Gerente de cuenta", icon=":material/badge:")
            tarea = st.selectbox("Tarea", usabilidad.TAREAS)
            inicio = st.session_state.get("t_inicio")
            x, y, _ = st.columns([1, 1, 2])
            if x.button("Iniciar tarea", type="primary", icon=":material/play_arrow:", width="stretch",
                        disabled=inicio is not None or not participante):
                st.session_state["t_inicio"] = time.time()
                st.session_state["t_tarea"] = tarea
                st.rerun()
            if y.button("Terminar tarea", icon=":material/stop:", width="stretch", disabled=inicio is None):
                st.session_state["t_segundos"] = round(time.time() - inicio, 1)
                st.session_state["t_inicio"] = None
                st.rerun()
            if inicio is not None:
                st.info(f"En curso: {st.session_state['t_tarea']}", icon=":material/timer:")
            if st.session_state.get("t_segundos") is not None:
                with st.form("resultado_tarea", border=False):
                    st.html(f'<div class="tm-note"><b>{ui.e(st.session_state["t_tarea"])}</b><br>'
                            f'Tiempo: {st.session_state["t_segundos"]} s</div>')
                    exito = st.segmented_control("¿Completó la tarea?", ["Sí", "No"], default="Sí") or "Sí"
                    errores = st.number_input("Errores (clics equivocados, pidió ayuda, se devolvió)", 0, 50, 0)
                    notas = st.text_area("Observaciones")
                    if st.form_submit_button("Guardar resultado", type="primary", icon=":material/save:"):
                        db.guardar_prueba(participante, rol, st.session_state["t_tarea"],
                                          st.session_state["t_segundos"], exito == "Sí", errores, notas)
                        st.session_state["t_segundos"] = None
                        st.toast("Resultado guardado.", icon=":material/check_circle:")
                        st.rerun()

        with t_sus:
            with st.form("sus", border=False):
                quien = st.text_input("Participante", st.session_state.get("participante", ""),
                                      icon=":material/person:")
                st.caption("1 = totalmente en desacuerdo · 5 = totalmente de acuerdo")
                respuestas = [st.slider(f"{i}. {pregunta}", 1, 5, 3)
                              for i, pregunta in enumerate(usabilidad.PREGUNTAS_SUS, 1)]
                if st.form_submit_button("Guardar cuestionario", type="primary", icon=":material/save:"):
                    puntaje = usabilidad.puntaje_sus(respuestas)
                    db.guardar_sus(quien, respuestas, puntaje)
                    st.success(f"SUS = {puntaje:.1f} ({usabilidad.interpretar_sus(puntaje)})",
                               icon=":material/check_circle:")

        with t_res:
            pruebas = db.listar_pruebas()
            sus = db.listar_sus()
            if pruebas.empty and sus.empty:
                ui.vacio("cronometro", "Aún no hay pruebas registradas")
            tarjetas = []
            if not pruebas.empty:
                tarjetas += [
                    ("usuarios", "Participantes", pruebas["participante"].nunique(),
                     f"{len(pruebas)} intento" + ("" if len(pruebas) == 1 else "s")),
                    ("reloj", "Tiempo medio por tarea", f"{pruebas['segundos'].mean():.0f} s", ""),
                    ("check", "Tasa de éxito", f"{pruebas['exito'].mean():.0%}", "Tareas completadas"),
                    ("x", "Tasa de error", f"{(pruebas['errores'] > 0).mean():.0%}",
                     "Intentos con al menos un error"),
                ]
            if not sus.empty:
                promedio = sus["puntaje"].mean()
                tarjetas.append(("tendencia", "SUS promedio", f"{promedio:.1f}",
                                 usabilidad.interpretar_sus(promedio)))
            if tarjetas:
                ui.kpis(tarjetas)
            if not pruebas.empty:
                st.dataframe(usabilidad.resumen(pruebas), hide_index=True, width="stretch",
                             column_config={"tarea": st.column_config.TextColumn("Tarea", width="large"),
                                            "intentos": "Intentos", "tiempo_medio_s": "Tiempo medio (s)",
                                            "tasa_exito": "Tasa de éxito", "errores_promedio": "Errores promedio"})
                st.download_button("Descargar pruebas (CSV)", pruebas.to_csv(index=False).encode("utf-8"),
                                   "pruebas_usabilidad.csv", icon=":material/download:")
            if not sus.empty:
                st.dataframe(sus[["participante", "puntaje", "fecha"]], hide_index=True, width="stretch",
                             column_config={"participante": "Participante", "puntaje": "SUS", "fecha": "Fecha"})

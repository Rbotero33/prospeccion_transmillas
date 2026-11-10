"""Contacto y seguimiento: correo aprobado por el asesor, respuestas, WhatsApp e historial."""

import streamlit as st

import config
from core import db, mensajes
from paginas import comun
from ui import estilos as ui
from ui import nav


def _etapas(estado):
    if estado == "Descartado":
        actual = -1
    else:
        actual = comun.ETAPA_DE.get(estado, 0)
    pasos = []
    for i, nombre in enumerate(comun.ETAPAS):
        clase = "hecho" if i < actual else "actual" if i == actual else ""
        marca = ui.icono("ok", 14) if i < actual else str(i + 1)
        pasos.append(f'<div class="tm-step {clase}"><div class="dot">{marca}</div>{nombre}</div>')
    return f'<div class="tm-steps">{"".join(pasos)}</div>'


def pagina():
    df = comun.prospectos()
    df = df[df["prioridad"] != "—"] if not df.empty else df
    ui.encabezado("Contacto y seguimiento")
    if df.empty:
        ui.vacio("enviar", "Sin prospectos clasificados", "Cargue y clasifique empresas para iniciar el contacto.")
        _, centro, _ = st.columns([2, 1.2, 2])
        centro.page_link(nav.PAGINAS["cargar"], label="Cargar empresas", icon=":material/upload_file:")
        return

    asesor = comun.asesor()
    ia_ok = comun.ia_activa()

    a, b = st.columns([4, 1], vertical_alignment="bottom")
    solo_a = b.toggle("Solo prioridad A")
    if solo_a:
        df = df[df["prioridad"] == "A"]
    if df.empty:
        ui.vacio("estrella", "Sin prospectos en prioridad A", "Desactive el filtro para ver los demás.")
        return
    ids = df["id"].astype(int).tolist()
    etiquetas = {int(r["id"]): comun.etiqueta(r) for _, r in df.iterrows()}
    actual = st.session_state.get("prospecto_actual")
    pid = a.selectbox("Prospecto", ids, index=ids.index(actual) if actual in ids else 0,
                      format_func=etiquetas.get)
    st.session_state["prospecto_actual"] = pid
    p = db.obtener(pid)

    # ------------------------------------------------------------------ resumen
    with st.container(key="card_resumen"):
        chips = "".join([
            ui.chip((p.get("ciudad") or "").title(), "pin"), ui.chip(p.get("sector") or "", "capas"),
            ui.chip(p.get("tamano") or "", "empresa"), ui.estado(p["estado"]),
        ])
        datos = "".join(
            f'<div class="tm-kv">{ui.icono(ico, 15)}<span>{ui.e(valor)}</span></div>'
            for ico, valor in [("usuario", p.get("contacto_nombre") or "Sin contacto"),
                               ("correo", p.get("correo") or "Sin correo"),
                               ("telefono", p.get("telefono") or "Sin teléfono")])
        st.html(
            f'<div style="display:flex;gap:18px;justify-content:space-between;flex-wrap:wrap">'
            f'<div style="display:flex;gap:14px;align-items:flex-start;min-width:0">{ui.prioridad(p["prioridad"], grande=True)}'
            f'<div style="min-width:0"><div class="tm-name" style="margin-bottom:6px">{ui.e(p["razon_social"])}</div>'
            f'<div class="tm-chips">{chips}</div></div></div><div>{datos}</div></div>'
            f'<div style="margin-top:16px">{_etapas(p["estado"])}</div>')

    # ------------------------------------------------------------------ acciones
    with st.container(key="card_acciones"):
        tab_correo, tab_estado, tab_wa, tab_hist = st.tabs([
            ":material/mail: Correo", ":material/reply: Registrar respuesta", ":material/chat: WhatsApp",
            ":material/history: Historial"])

        with tab_correo:
            tipo = st.segmented_control("Mensaje", ["Primer contacto", "Seguimiento (48 h)"],
                                        default="Primer contacto") or "Primer contacto"
            clave = f"borrador_{p['id']}_{tipo}"
            con_ia = ia_ok and tipo == "Primer contacto"
            instrucciones = st.text_input(
                "Instrucciones para la IA (opcional)", icon=":material/auto_awesome:",
                placeholder="Ej.: más formal, menciona cadena de frío y crédito para empresas",
                disabled=not con_ia)
            g1, g2, _ = st.columns([1, 1, 1.4])
            if g1.button("Generar con plantilla", icon=":material/description:", width="stretch"):
                asunto, cuerpo = (mensajes.correo_plantilla(p, asesor) if tipo == "Primer contacto"
                                  else mensajes.seguimiento_plantilla(p, asesor))
                st.session_state[clave] = (asunto, cuerpo, "Plantilla")
            if g2.button("Personalizar con IA", icon=":material/auto_awesome:", width="stretch",
                         disabled=not con_ia):
                with st.spinner("La IA está redactando..."):
                    st.session_state[clave] = mensajes.correo_ia(p, asesor, instrucciones)
            if clave in st.session_state:
                asunto, cuerpo, origen = st.session_state[clave]
                asunto = st.text_input("Asunto", asunto)
                cuerpo = st.text_area("Mensaje", cuerpo, height=290)
                st.caption(f"Generado con: {origen}")
                if not p.get("correo"):
                    st.warning("Este prospecto no tiene correo. Complételo en Prospectos priorizados.",
                               icon=":material/alternate_email:")
                aprobado = st.checkbox("Revisé el mensaje y apruebo enviarlo en nombre de Transmillas")
                e1, e2, _ = st.columns([1, 1, 1.4])
                e1.link_button("Abrir en mi correo", mensajes.enlace_correo(p.get("correo"), asunto, cuerpo),
                               icon=":material/open_in_new:", disabled=not aprobado, width="stretch")
                if e2.button("Marcar como enviado", type="primary", icon=":material/done_all:",
                             disabled=not aprobado, width="stretch"):
                    db.guardar_mensaje(p["id"], "Correo", asunto, cuerpo, origen, asesor)
                    nuevo = "Contactado (correo)" if tipo == "Primer contacto" else "Seguimiento enviado"
                    db.cambiar_estado(p["id"], nuevo, f"Enviado por {asesor}")
                    del st.session_state[clave]
                    st.toast("Correo registrado como enviado.", icon=":material/done_all:")
                    st.rerun()

        with tab_estado:
            with st.form("estado", border=False):
                nuevo = st.selectbox("Nuevo estado", config.ESTADOS, index=config.ESTADOS.index(p["estado"]))
                nota = st.text_area("Nota (qué respondió, volumen, rutas, próxima acción)")
                if st.form_submit_button("Guardar", type="primary", icon=":material/save:"):
                    db.cambiar_estado(p["id"], nuevo, nota)
                    st.toast("Estado actualizado.", icon=":material/check_circle:")
                    st.rerun()

        with tab_wa:
            if p["estado"] not in config.ESTADOS_WHATSAPP_PERMITIDO:
                st.info("WhatsApp disponible cuando el prospecto haya respondido o autorizado el contacto.",
                        icon=":material/lock:")
            elif not p.get("telefono"):
                st.warning("Falta el teléfono del prospecto.", icon=":material/call:")
            else:
                texto = st.text_area("Mensaje", mensajes.whatsapp_texto(p, asesor), height=140)
                w1, w2, _ = st.columns([1, 1, 1.4])
                w1.link_button("Abrir WhatsApp", mensajes.enlace_whatsapp(p["telefono"], texto),
                               icon=":material/open_in_new:", width="stretch")
                if w2.button("Registrar mensaje", icon=":material/done_all:", width="stretch"):
                    db.guardar_mensaje(p["id"], "WhatsApp", "", texto, "Plantilla", asesor)
                    db.registrar_evento(p["id"], "WhatsApp enviado", texto[:120])
                    st.toast("Mensaje de WhatsApp registrado.", icon=":material/done_all:")
                    st.rerun()

        with tab_hist:
            eventos = db.eventos_de(p["id"])
            if eventos.empty:
                st.html('<div class="tm-row-d">Sin eventos registrados.</div>')
            else:
                linea = "".join(
                    f'<div class="tm-ev"><div class="tm-ev-t">{ui.e(ev.tipo)}</div>'
                    + (f'<div class="tm-ev-d">{ui.e(ev.detalle)}</div>' if ev.detalle else "")
                    + f'<div class="tm-ev-f">{ui.e(ev.fecha)}</div></div>' for ev in eventos.itertuples())
                st.html(f'<div class="tm-time">{linea}</div>')
            enviados = db.mensajes_de(p["id"])
            if not enviados.empty:
                with st.expander(f"Mensajes enviados ({len(enviados)})", icon=":material/outbox:"):
                    st.dataframe(enviados, hide_index=True, width="stretch")

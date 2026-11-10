"""Prospectos priorizados: filtros, tabla y ficha con el desglose del puntaje."""

import json

import streamlit as st

import config
from core import db, proceso
from paginas import comun
from ui import estilos as ui
from ui import nav

CRITERIOS = {"ruta": "Ruta", "frecuencia": "Frecuencia", "tamano": "Tamaño", "sector": "Sector",
             "contacto": "Contacto"}
TEXTO_PRIORIDAD = {"A": "Contactar primero", "B": "Contactar después", "C": "Mantener en base"}


def _color_prioridad(valor):
    if valor in ui.PRIORIDAD_COLOR:
        return (f"background-color: {ui.PRIORIDAD_COLOR[valor]}; color: {ui.PRIORIDAD_TEXTO[valor]}; "
                "font-weight: 700; text-align: center;")
    return "color: #66758a; text-align: center;"


def pagina():
    df = comun.prospectos()
    if df.empty:
        ui.encabezado("Prospectos priorizados")
        ui.vacio("objetivo", "No hay prospectos", "Cargue y clasifique empresas para ver la lista priorizada.")
        _, centro, _ = st.columns([2, 1.2, 2])
        centro.page_link(nav.PAGINAS["cargar"], label="Cargar empresas", icon=":material/upload_file:")
        return

    n_a = int((df["prioridad"] == "A").sum())
    ui.encabezado("Prospectos priorizados",
                  ui.chip(f"{len(df)} empresas", "empresa") + ui.chip(f"{n_a} en prioridad A", "estrella", suave=True))

    # ------------------------------------------------------------------ filtros
    with st.container(key="card_filtros"):
        f = st.columns([1.4, 1.7, 1.1, 1.3, 1.3], vertical_alignment="bottom")
        buscar = f[0].text_input("Buscar", placeholder="Empresa o NIT", icon=":material/search:")
        hay_clasificadas = bool(df["prioridad"].isin(["A", "B", "C"]).any())
        prioridades = f[1].pills("Prioridad", ["A", "B", "C", "Pendientes"], selection_mode="multi",
                                 default=["A", "B", "C"] if hay_clasificadas else ["Pendientes"])
        ciudades = f[2].multiselect("Ciudad", sorted(df["ciudad_txt"].dropna().unique()), placeholder="Todas")
        sectores = f[3].multiselect("Sector", sorted(df["sector"].dropna().unique()), placeholder="Todos")
        estados = f[4].multiselect("Estado", config.ESTADOS, placeholder="Todos")

    elegidas = ["—" if p == "Pendientes" else p for p in (prioridades or [])]
    vista = df[df["prioridad"].isin(elegidas)] if elegidas else df
    if buscar.strip():
        texto = buscar.strip().lower()
        vista = vista[vista["razon_social"].str.lower().str.contains(texto, regex=False)
                      | vista["nit"].fillna("").astype(str).str.contains(texto, regex=False)]
    if ciudades:
        vista = vista[vista["ciudad_txt"].isin(ciudades)]
    if sectores:
        vista = vista[vista["sector"].isin(sectores)]
    if estados:
        vista = vista[vista["estado"].isin(estados)]
    vista = vista.reset_index(drop=True)

    if vista.empty:
        ui.vacio("lista", "Sin resultados", "Ningún prospecto coincide con los filtros.")
        return

    # ------------------------------------------------------------------ tabla
    columnas = ["prioridad", "puntaje", "razon_social", "ciudad_txt", "sector", "tamano", "frecuencia",
                "regiones", "estado"]
    tabla = vista[columnas]
    estilo = tabla.style
    estilo = (estilo.map if hasattr(estilo, "map") else estilo.applymap)(_color_prioridad, subset=["prioridad"])
    evento = st.dataframe(
        estilo, hide_index=True, width="stretch", height=min(40 + 35 * len(tabla), 390),
        on_select="rerun", selection_mode="single-row", key="tabla_prospectos",
        column_config={
            "prioridad": st.column_config.TextColumn("Prioridad", width=80),
            "puntaje": st.column_config.ProgressColumn("Puntaje", min_value=0, max_value=100, format="%.1f",
                                                       width=130),
            "razon_social": st.column_config.TextColumn("Empresa", width="large"),
            "ciudad_txt": "Ciudad", "sector": "Sector", "tamano": "Tamaño", "frecuencia": "Frecuencia",
            "regiones": "Destinos detectados", "estado": "Estado",
        })
    a, b = st.columns([4, 1], vertical_alignment="center")
    a.caption(f"{len(vista)} de {len(df)} empresas · seleccione una fila para ver su ficha")
    b.download_button("Descargar CSV", vista.drop(columns=["ciudad_txt"]).to_csv(index=False).encode("utf-8"),
                      "prospectos_transmillas.csv", "text/csv", icon=":material/download:", width="stretch")

    # ------------------------------------------------------------------ prospecto seleccionado
    filas = evento.selection.rows
    if filas and filas[0] < len(vista):
        pid = int(vista.iloc[filas[0]]["id"])
    elif st.session_state.get("prospecto_actual") in set(vista["id"]):
        pid = int(st.session_state["prospecto_actual"])
    else:
        pid = int(vista.iloc[0]["id"])
    st.session_state["prospecto_actual"] = pid
    p = db.obtener(pid)
    _ficha(p)


def _ficha(p):
    clasificado = bool(p.get("detalle_puntaje"))
    izq, der = st.columns([1, 1.3], gap="medium")

    with izq, st.container(key="card_ficha"):
        chips = "".join([
            ui.chip((p.get("ciudad") or "").title(), "pin"),
            ui.chip(p.get("sector") or "Sin sector", "capas"),
            ui.chip(p.get("tamano") or "Tamaño sin dato", "empresa"),
            ui.estado(p["estado"]),
        ])
        st.html(f'<div class="tm-name">{ui.e(p["razon_social"])}</div><div class="tm-chips">{chips}</div>')
        if clasificado:
            st.html(
                f'<div style="display:flex;align-items:center;gap:14px;margin-top:6px">'
                f'{ui.prioridad(p["prioridad"], grande=True)}<div class="tm-score" style="margin:0"><b>{p["puntaje"]:.1f}</b>'
                f'<span>/ 100 · {ui.e(TEXTO_PRIORIDAD.get(p["prioridad"], ""))}</span></div></div>'
                f'<div style="margin-top:12px">{ui.medidor(p["puntaje"])}</div>')
        contacto = "".join(
            f'<div class="tm-kv">{ui.icono(ico, 15)}<span>{ui.e(valor)}</span></div>'
            for ico, valor in [
                ("usuario", " · ".join(x for x in [p.get("contacto_nombre"), p.get("contacto_cargo")] if x)),
                ("correo", p.get("correo")), ("telefono", p.get("telefono")), ("web", p.get("sitio_web")),
            ] if valor)
        st.html(contacto or '<div class="tm-row-d">Sin datos de contacto.</div>')
        if st.button("Preparar contacto", type="primary", icon=":material/send:", width="stretch",
                     disabled=not clasificado):
            st.switch_page(nav.PAGINAS["contacto"])

    with der, st.container(key="card_desglose"):
        ui.titulo_tarjeta("Desglose del puntaje", "barras",
                          f"Método: {p['metodo']}" if clasificado else None)
        if not clasificado:
            st.html('<div class="tm-row-d" style="padding:12px 0">Este prospecto aún no está clasificado.</div>')
            st.page_link(nav.PAGINAS["cargar"], label="Ir a clasificar", icon=":material/auto_awesome:")
        else:
            detalle = json.loads(p["detalle_puntaje"])
            filas = []
            for clave, d in detalle.items():
                maximo = round(d["peso"] * 100, 1)
                filas.append(
                    f'<div class="tm-crit"><div class="tm-crit-top"><div class="tm-crit-n">'
                    f'{CRITERIOS.get(clave, clave)}<small>peso {d["peso"]:.0%}</small></div>'
                    f'<div class="tm-crit-v">{d["aporte"]:g} <small>/ {maximo:g}</small></div></div>'
                    f'{ui.medidor(d["aporte"], maximo)}<div class="tm-crit-r">{ui.e(d["razon"])}</div></div>')
            st.html("".join(filas))
            st.html(f'<div class="tm-note"><b>Justificación.</b> {ui.e(p["justificacion"])}</div>')

    with st.expander("Editar datos de contacto y descripción", icon=":material/edit:"):
        with st.form("editar", border=False):
            a, b = st.columns(2)
            correo = a.text_input("Correo", p.get("correo") or "")
            tel = b.text_input("Teléfono", p.get("telefono") or "")
            nombre = a.text_input("Nombre del contacto", p.get("contacto_nombre") or "")
            cargo = b.text_input("Cargo", p.get("contacto_cargo") or "")
            web = a.text_input("Sitio web", p.get("sitio_web") or "")
            desc = st.text_area("Descripción", p.get("descripcion") or "")
            if st.form_submit_button("Guardar y recalcular puntaje", type="primary", icon=":material/save:"):
                db.actualizar(p["id"], correo=correo, telefono=tel, contacto_nombre=nombre,
                              contacto_cargo=cargo, sitio_web=web, descripcion=desc)
                proceso.clasificar_y_puntuar([p["id"]], usar_ia=comun.ia_activa())
                st.rerun()

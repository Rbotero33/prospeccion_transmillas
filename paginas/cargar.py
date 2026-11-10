"""Cargar empresas (datos abiertos, archivo o manual) y clasificarlas."""

import time

import streamlit as st

import config
from core import db, fuentes, proceso
from paginas import comun
from ui import estilos as ui
from ui import nav


def pagina():
    ui.encabezado("Cargar empresas")

    with st.container(key="card_fuentes"):
        ui.titulo_tarjeta("Fuente de empresas", "empresa")
        t1, t2, t3 = st.tabs([":material/public: Datos abiertos", ":material/upload_file: Archivo CSV / Excel",
                              ":material/edit_note: Agregar a mano"])

        with t1:
            st.markdown("Empresas de **agroindustria, materiales de construcción y metalmecánica** · "
                        "Supersociedades, *10.000 Empresas más Grandes del País* (datos.gov.co).")
            col_a, col_b = st.columns(2)
            ciudades = col_a.multiselect("Ciudades", config.CIUDADES_OBJETIVO, default=config.CIUDADES_OBJETIVO,
                                         format_func=str.title, placeholder="Elija ciudades")
            anio = col_b.number_input("Año de corte", 2021, 2030, config.DATOS_GOV_ANIO)
            d1, d2 = st.columns(2)
            if d1.button("Descargar de datos.gov.co", type="primary", icon=":material/cloud_download:",
                         width="stretch"):
                try:
                    with st.spinner("Consultando datos.gov.co..."):
                        filas = fuentes.descargar_datos_gov(ciudades, int(anio))
                    nuevos, act = db.guardar_prospectos(filas)
                    st.success(f"{len(filas)} empresas encontradas: {nuevos} nuevas, {act} actualizadas.",
                               icon=":material/check_circle:")
                except Exception as error:
                    st.error(f"No se pudo descargar ({error}). Revise la conexión a internet.",
                             icon=":material/wifi_off:")
            if d2.button("Cargar copia guardada (Supersociedades 2025)", icon=":material/inventory_2:",
                         width="stretch"):
                nuevos, act = db.guardar_prospectos(
                    fuentes.leer_archivo("data/empresas_semilla.csv", "datos.gov.co Supersociedades 2025"))
                st.success(f"{nuevos} empresas nuevas, {act} actualizadas.", icon=":material/check_circle:")

        with t2:
            archivo = st.file_uploader("Archivo", type=["csv", "xlsx"])
            fuente = st.text_input("Nombre de la fuente", "EMIS / lista propia")
            if archivo and st.button("Importar archivo", type="primary", icon=":material/upload:"):
                try:
                    nuevos, act = db.guardar_prospectos(fuentes.leer_archivo(archivo, fuente))
                    st.success(f"{nuevos} empresas nuevas y {act} actualizadas.", icon=":material/check_circle:")
                except Exception as error:
                    st.error(str(error), icon=":material/error:")

        with t3:
            with st.form("manual", clear_on_submit=True, border=False):
                a, b = st.columns(2)
                rs = a.text_input("Razón social *")
                nit = b.text_input("NIT")
                ciudad = a.selectbox("Ciudad", config.CIUDADES_OBJETIVO, format_func=str.title)
                ciiu = b.text_input("CIIU (4 dígitos)")
                web = a.text_input("Sitio web")
                correo = b.text_input("Correo")
                tel = a.text_input("Teléfono")
                contacto = b.text_input("Nombre del contacto")
                desc = st.text_area("Descripción (qué venden, a quién, a dónde despachan)")
                if st.form_submit_button("Agregar empresa", type="primary", icon=":material/add_business:"):
                    if not rs.strip():
                        st.error("La razón social es obligatoria.", icon=":material/error:")
                    else:
                        db.guardar_prospectos([{
                            "razon_social": rs, "nit": nit or None, "ciudad": ciudad,
                            "ciiu": int(ciiu) if ciiu.strip().isdigit() else None, "sitio_web": web,
                            "correo": correo, "telefono": tel, "contacto_nombre": contacto,
                            "descripcion": desc, "fuente": "Manual"}])
                        st.success(f"{rs} agregada.", icon=":material/check_circle:")

    df = comun.prospectos()
    pendientes = df[df["prioridad"] == "—"] if not df.empty else df
    ia_ok = comun.ia_activa()

    with st.container(key="card_clasificar"):
        ui.titulo_tarjeta("Clasificar y puntuar", "estrella")
        st.html(f'<div class="tm-chips" style="margin:4px 0 2px">'
                f'{ui.chip(f"{len(df)} empresas en la base", "empresa", suave=True)}'
                f'{ui.chip(f"{len(pendientes)} sin clasificar", "reloj")}</div>')
        a, b, c = st.columns([1.4, 1.6, 1], vertical_alignment="bottom")
        alcance = a.segmented_control("Empresas a clasificar", ["Solo las nuevas", "Todas"],
                                      default="Solo las nuevas") or "Solo las nuevas"
        usar_ia = b.toggle("Leer las descripciones con IA local", value=ia_ok, disabled=not ia_ok)
        if c.button("Clasificar", type="primary", icon=":material/auto_awesome:", disabled=df.empty,
                    width="stretch"):
            ids = (pendientes if alcance == "Solo las nuevas" else df)["id"].tolist()
            if not ids:
                st.info("No hay empresas nuevas por clasificar.", icon=":material/info:")
            else:
                barra = st.progress(0.0, "Clasificando...")
                inicio = time.time()
                proceso.clasificar_y_puntuar(
                    ids, usar_ia=usar_ia,
                    al_avanzar=lambda i, t, n: barra.progress(i / t, f"{i}/{t} · {n}"))
                barra.empty()
                st.session_state["aviso_clasificar"] = (
                    f"{len(ids)} empresas clasificadas en {time.time() - inicio:.1f} s.")
                st.rerun()
        aviso = st.session_state.pop("aviso_clasificar", None)
        if aviso:
            st.success(aviso, icon=":material/check_circle:")
            st.page_link(nav.PAGINAS["prospectos"], label="Ver prospectos priorizados",
                         icon=":material/arrow_forward:")

    with st.expander("Completar datos con el sitio web de la empresa", icon=":material/language:"):
        sin_desc = (df[(df["sitio_web"].fillna("") != "") & (df["descripcion"].fillna("") == "")]
                    if not df.empty else df)
        st.write(f"{len(sin_desc)} empresas con sitio web y sin descripción.")
        if st.button("Leer sitios web", icon=":material/travel_explore:", disabled=sin_desc.empty):
            for _, fila in sin_desc.iterrows():
                texto = fuentes.leer_descripcion_web(fila["sitio_web"])
                if texto:
                    db.actualizar(int(fila["id"]), descripcion=texto)
            st.success("Listo. Vuelva a clasificar para usar la nueva información.", icon=":material/check_circle:")

    with st.expander("Administrar base", icon=":material/database:"):
        confirmar = st.checkbox("Confirmo que quiero borrar todos los prospectos")
        if st.button("Borrar todos los prospectos", icon=":material/delete:", disabled=not confirmar):
            db.borrar_todo()
            st.session_state.pop("prospecto_actual", None)
            st.session_state["aviso_borrado"] = True
            st.rerun()
        if st.session_state.pop("aviso_borrado", False):
            st.warning("Base de prospectos vacía.", icon=":material/delete:")

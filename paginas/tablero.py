"""Tablero: indicadores, embudo y siguientes contactos."""

import streamlit as st

import config
from paginas import comun
from ui import estilos as ui
from ui import graficos, nav


def pagina():
    df = comun.prospectos()
    ciudades = "".join(ui.chip(c.title(), "pin") for c in config.CIUDADES_OBJETIVO)
    ui.encabezado("Tablero", ciudades)

    if df.empty:
        ui.vacio("bandeja", "Aún no hay empresas", "Cargue la primera lista para ver el embudo de prospección.")
        _, centro, _ = st.columns([2, 1.2, 2])
        centro.page_link(nav.PAGINAS["cargar"], label="Cargar empresas", icon=":material/upload_file:")
        return

    total = len(df)
    prioridad_a = int((df["prioridad"] == "A").sum())
    contactadas = int(df["estado"].isin(config.ESTADOS[2:8]).sum())
    respondieron = int(df["estado"].isin(config.ESTADOS[4:8]).sum())
    reuniones = int(df["estado"].isin(["Reunión / cotización", "Cliente"]).sum())
    clientes = int((df["estado"] == "Cliente").sum())

    ui.kpis([
        ("empresa", "Empresas identificadas", total, f"{df['ciudad_txt'].nunique()} ciudades"),
        ("estrella", "Prioridad A", prioridad_a, f"{prioridad_a / total:.0%} de la base"),
        ("enviar", "Contactadas", contactadas, f"{contactadas / total:.0%} de la base"),
        ("mensaje", "Respondieron", respondieron,
         f"{respondieron / contactadas:.0%} de respuesta" if contactadas else "Sin contactos aún"),
        ("calendario", "Reuniones y cotizaciones", reuniones, ""),
        ("check", "Clientes nuevos", clientes, ""),
    ])

    izq, der = st.columns(2, gap="medium")
    with izq, st.container(key="card_embudo"):
        ui.titulo_tarjeta("Embudo de prospección", "embudo", "Empresas en cada etapa")
        st.altair_chart(graficos.embudo([
            ("Identificadas", total), ("Prioridad A", prioridad_a), ("Contactadas", contactadas),
            ("Respondieron", respondieron), ("Reunión o cotización", reuniones), ("Clientes", clientes),
        ]), theme=None, width="stretch")
    with der, st.container(key="card_ciudades"):
        ui.titulo_tarjeta("Prioridad por ciudad", "barras", "Empresas clasificadas A, B y C")
        clasificadas = df[df["prioridad"].isin(["A", "B", "C"])]
        if clasificadas.empty:
            ui.vacio("capas", "Sin clasificar", "Clasifique las empresas para ver su prioridad.")
        else:
            conteo = (clasificadas.groupby(["ciudad_txt", "prioridad"]).size()
                      .reset_index(name="empresas").rename(columns={"ciudad_txt": "ciudad"}))
            st.altair_chart(graficos.prioridad_por_ciudad(conteo), theme=None, width="stretch")
            with st.expander("Ver datos"):
                st.dataframe(conteo.pivot_table(index="ciudad", columns="prioridad", values="empresas",
                                                fill_value=0).reset_index(), hide_index=True, width="stretch")

    izq, der = st.columns(2, gap="medium")
    with izq, st.container(key="card_sectores"):
        ui.titulo_tarjeta("Sectores", "capas", "Puntaje promedio de cada sector (0 a 100)")
        sectores = (df.groupby("sector", dropna=False)
                    .agg(empresas=("id", "count"), promedio=("puntaje", "mean"))
                    .reset_index().sort_values("promedio", ascending=False))
        filas = "".join(
            f'<div class="tm-row"><div><div class="tm-row-n">{ui.e(s.sector or "Sin clasificar")}</div>'
            f'<div class="tm-row-d">{s.empresas} empresas</div></div>{ui.medidor(round(s.promedio, 1))}'
            f'<div class="tm-row-v">{s.promedio:.1f}</div></div>' for s in sectores.itertuples())
        st.html(f'<div class="tm-rows">{filas}</div>')
    with der, st.container(key="card_siguientes"):
        ui.titulo_tarjeta("Siguientes contactos", "objetivo", "Mejores prospectos que aún no se han contactado")
        pendientes = df[df["estado"].isin(config.ESTADOS[:2]) & df["prioridad"].isin(["A", "B"])].head(5)
        if pendientes.empty:
            st.html('<div class="tm-row-d" style="padding:14px 0">No hay prospectos A o B pendientes de contacto.</div>')
        else:
            items = "".join(
                f'<div class="tm-item">{ui.prioridad(r.prioridad)}<div class="tm-item-b">'
                f'<div class="tm-row-n">{ui.e(r.razon_social)}</div>'
                f'<div class="tm-row-d">{ui.e(r.ciudad_txt)} · {ui.e(r.sector)}</div></div>'
                f'<div class="tm-row-v">{r.puntaje:.1f}</div></div>' for r in pendientes.itertuples())
            st.html(f'<div class="tm-rows">{items}</div>')
            st.page_link(nav.PAGINAS["contacto"], label="Ir a contacto y seguimiento",
                         icon=":material/arrow_forward:")

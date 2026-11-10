"""Gráficos del tablero (Altair). Un solo tono para magnitudes y una rampa ordenada para A/B/C."""

import altair as alt
import pandas as pd

from ui.estilos import AZUL, PRIORIDAD_COLOR

FUENTE = "Inter, system-ui, -apple-system, 'Segoe UI', sans-serif"
TINTA, TINTA2, TENUE = "#0f1b2d", "#48566a", "#66758a"
REJILLA, EJE = "#e9edf3", "#c9d1dc"
ETIQUETA_PRIORIDAD = {"A": "A · primero", "B": "B · después", "C": "C · en base"}


def _acabado(grafico, alto):
    return (grafico.properties(height=alto, background="transparent")
            .configure_view(stroke=None)
            .configure_axis(labelFont=FUENTE, titleFont=FUENTE, labelFontSize=12, labelColor=TENUE,
                            titleColor=TENUE, gridColor=REJILLA, gridWidth=1, domainColor=EJE, tickColor=EJE)
            .configure_legend(labelFont=FUENTE, titleFont=FUENTE, labelFontSize=12, titleFontSize=12,
                              labelColor=TINTA2, titleColor=TENUE, symbolType="square", symbolSize=110,
                              symbolStrokeWidth=0, orient="top", direction="horizontal", titleOrient="left",
                              padding=0, offset=10))


def embudo(etapas):
    """etapas: lista de (nombre, cantidad) en orden."""
    df = pd.DataFrame(etapas, columns=["etapa", "empresas"])
    anterior = df["empresas"].shift(1)
    df["paso"] = [("—" if pd.isna(a) or a == 0 else f"{100 * v / a:.0f} % de la etapa anterior")
                  for v, a in zip(df["empresas"], anterior)]
    maximo = max(int(df["empresas"].max()), 1)
    base = alt.Chart(df).encode(
        y=alt.Y("etapa:N", sort=None, title=None,
                axis=alt.Axis(ticks=False, domain=False, labelPadding=12, labelColor=TINTA, labelFontSize=13,
                              labelLimit=190)),
        x=alt.X("empresas:Q", title=None, scale=alt.Scale(domain=[0, maximo * 1.12], nice=False),
                axis=alt.Axis(format="d", tickMinStep=1, tickCount=5, ticks=False, domain=False, labelPadding=8)),
        tooltip=[alt.Tooltip("etapa:N", title="Etapa"), alt.Tooltip("empresas:Q", title="Empresas"),
                 alt.Tooltip("paso:N", title="Conversión")],
    )
    barras = base.mark_bar(size=22, cornerRadiusEnd=4, color=AZUL)
    valores = base.mark_text(align="left", dx=7, font=FUENTE, fontSize=12.5, fontWeight=600,
                             color=TINTA).encode(text=alt.Text("empresas:Q", format="d"))
    return _acabado(barras + valores, 40 * len(df) + 30)


def prioridad_por_ciudad(df):
    """df: columnas ciudad, prioridad (A/B/C), empresas."""
    df = df.copy()
    df["grupo"] = df["prioridad"].map(ETIQUETA_PRIORIDAD)
    df["orden"] = df["prioridad"].map({"A": 0, "B": 1, "C": 2})
    totales = df.groupby("ciudad", as_index=False)["empresas"].sum()
    maximo = max(int(totales["empresas"].max()), 1)
    orden_ciudades = totales.sort_values("empresas", ascending=False)["ciudad"].tolist()
    eje_y = alt.Y("ciudad:N", title=None, sort=orden_ciudades,
                  axis=alt.Axis(ticks=False, domain=False, labelPadding=12, labelColor=TINTA, labelFontSize=13))
    escala_x = alt.Scale(domain=[0, maximo * 1.12], nice=False)
    barras = alt.Chart(df).mark_bar(size=24, stroke="#ffffff", strokeWidth=2).encode(
        y=eje_y,
        x=alt.X("empresas:Q", title=None, stack="zero", scale=escala_x,
                axis=alt.Axis(format="d", tickMinStep=1, tickCount=5, ticks=False, domain=False, labelPadding=8)),
        color=alt.Color("grupo:N", title="Prioridad",
                        scale=alt.Scale(domain=list(ETIQUETA_PRIORIDAD.values()),
                                        range=[PRIORIDAD_COLOR[k] for k in ETIQUETA_PRIORIDAD])),
        order=alt.Order("orden:Q"),
        tooltip=[alt.Tooltip("ciudad:N", title="Ciudad"), alt.Tooltip("grupo:N", title="Prioridad"),
                 alt.Tooltip("empresas:Q", title="Empresas")],
    )
    valores = alt.Chart(totales).mark_text(align="left", dx=7, font=FUENTE, fontSize=12.5, fontWeight=600,
                                           color=TINTA).encode(
        y=alt.Y("ciudad:N", sort=orden_ciudades, title=None), x=alt.X("empresas:Q", scale=escala_x),
        text=alt.Text("empresas:Q", format="d"))
    return _acabado(barras + valores, 52 * df["ciudad"].nunique() + 84)

"""Funciones compartidas por las páginas."""

import pandas as pd
import streamlit as st

from core import db

ETAPAS = ["Nuevo", "Contactado", "Respondió", "Reunión", "Cliente"]
ETAPA_DE = {
    "Nuevo": 0, "Aprobado para contacto": 0,
    "Contactado (correo)": 1, "Seguimiento enviado": 1,
    "Respondió": 2, "Autorizó WhatsApp": 2,
    "Reunión / cotización": 3,
    "Cliente": 4,
}


def prospectos():
    df = db.listar_prospectos()
    if not df.empty:
        df["puntaje"] = df["puntaje"].fillna(0)
        df["prioridad"] = df["prioridad"].fillna("—")
        df["ciudad_txt"] = df["ciudad"].fillna("").str.title()
    return df


def etiqueta(fila):
    pts = "sin puntaje" if pd.isna(fila["puntaje"]) else f"{fila['puntaje']:.1f} pts"
    return f"{fila['prioridad']} · {fila['razon_social']} · {fila['ciudad_txt']} · {pts}"


def asesor():
    return st.session_state.get("asesor") or "Asesor Transmillas"


def ia_activa():
    return bool(st.session_state.get("ia_ok"))

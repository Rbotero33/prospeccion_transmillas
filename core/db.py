"""Base de datos local (SQLite, viene con Python: no hay que instalar nada)."""

import json
import os
import sqlite3
from datetime import datetime

import pandas as pd

import config

CAMPOS_PROSPECTO = [
    "nit", "razon_social", "ciudad", "ciiu", "ingresos_millones", "sitio_web", "correo",
    "telefono", "contacto_nombre", "contacto_cargo", "descripcion", "fuente",
]


def _ahora():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def conectar():
    os.makedirs(os.path.dirname(config.DB_PATH), exist_ok=True)
    con = sqlite3.connect(config.DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def inicializar():
    with conectar() as con:
        con.executescript(
            """
            CREATE TABLE IF NOT EXISTS prospectos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nit TEXT UNIQUE,
                razon_social TEXT NOT NULL,
                ciudad TEXT, ciiu INTEGER, ingresos_millones REAL,
                sitio_web TEXT, correo TEXT, telefono TEXT,
                contacto_nombre TEXT, contacto_cargo TEXT,
                descripcion TEXT, fuente TEXT,
                sector TEXT, tamano TEXT, regiones TEXT, frecuencia TEXT,
                puntaje REAL, prioridad TEXT, detalle_puntaje TEXT,
                justificacion TEXT, metodo TEXT,
                estado TEXT DEFAULT 'Nuevo',
                creado TEXT, actualizado TEXT
            );
            CREATE TABLE IF NOT EXISTS eventos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prospecto_id INTEGER, fecha TEXT, tipo TEXT, detalle TEXT
            );
            CREATE TABLE IF NOT EXISTS mensajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prospecto_id INTEGER, canal TEXT, asunto TEXT, cuerpo TEXT,
                generado_por TEXT, aprobado_por TEXT, fecha TEXT
            );
            CREATE TABLE IF NOT EXISTS pruebas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                participante TEXT, rol TEXT, tarea TEXT,
                segundos REAL, exito INTEGER, errores INTEGER, notas TEXT, fecha TEXT
            );
            CREATE TABLE IF NOT EXISTS sus (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                participante TEXT, respuestas TEXT, puntaje REAL, fecha TEXT
            );
            """
        )


# --------------------------------------------------------------------------- prospectos

def guardar_prospectos(filas):
    """Inserta empresas nuevas; si el NIT ya existe, completa solo los campos vacíos.
    Devuelve (nuevos, actualizados)."""
    nuevos = actualizados = 0
    with conectar() as con:
        for f in filas:
            nit = str(f.get("nit") or "").strip() or None
            existente = None
            if nit:
                existente = con.execute("SELECT * FROM prospectos WHERE nit = ?", (nit,)).fetchone()
            if existente is None:
                valores = {c: f.get(c) for c in CAMPOS_PROSPECTO}
                valores["nit"] = nit
                cols = ", ".join(valores) + ", estado, creado, actualizado"
                marcas = ", ".join("?" for _ in valores) + ", 'Nuevo', ?, ?"
                cur = con.execute(f"INSERT INTO prospectos ({cols}) VALUES ({marcas})",
                                  (*valores.values(), _ahora(), _ahora()))
                con.execute("INSERT INTO eventos (prospecto_id, fecha, tipo, detalle) VALUES (?,?,?,?)",
                            (cur.lastrowid, _ahora(), "Identificado", f"Fuente: {f.get('fuente', '')}"))
                nuevos += 1
            else:
                cambios = {c: f.get(c) for c in CAMPOS_PROSPECTO
                           if f.get(c) not in (None, "") and not existente[c]}
                if cambios:
                    sets = ", ".join(f"{c} = ?" for c in cambios)
                    con.execute(f"UPDATE prospectos SET {sets}, actualizado = ? WHERE id = ?",
                                (*cambios.values(), _ahora(), existente["id"]))
                    actualizados += 1
    return nuevos, actualizados


def listar_prospectos():
    with conectar() as con:
        return pd.read_sql_query("SELECT * FROM prospectos ORDER BY puntaje DESC, razon_social", con)


def obtener(prospecto_id):
    with conectar() as con:
        fila = con.execute("SELECT * FROM prospectos WHERE id = ?", (prospecto_id,)).fetchone()
        return dict(fila) if fila else None


def actualizar(prospecto_id, **campos):
    if not campos:
        return
    if "detalle_puntaje" in campos and not isinstance(campos["detalle_puntaje"], str):
        campos["detalle_puntaje"] = json.dumps(campos["detalle_puntaje"], ensure_ascii=False)
    sets = ", ".join(f"{c} = ?" for c in campos)
    with conectar() as con:
        con.execute(f"UPDATE prospectos SET {sets}, actualizado = ? WHERE id = ?",
                    (*campos.values(), _ahora(), prospecto_id))


def cambiar_estado(prospecto_id, estado, detalle=""):
    actualizar(prospecto_id, estado=estado)
    registrar_evento(prospecto_id, f"Estado: {estado}", detalle)


def registrar_evento(prospecto_id, tipo, detalle=""):
    with conectar() as con:
        con.execute("INSERT INTO eventos (prospecto_id, fecha, tipo, detalle) VALUES (?,?,?,?)",
                    (prospecto_id, _ahora(), tipo, detalle))


def eventos_de(prospecto_id):
    with conectar() as con:
        return pd.read_sql_query(
            "SELECT fecha, tipo, detalle FROM eventos WHERE prospecto_id = ? ORDER BY id DESC",
            con, params=(prospecto_id,))


def todos_los_eventos():
    with conectar() as con:
        return pd.read_sql_query("SELECT * FROM eventos", con)


def borrar_todo():
    with conectar() as con:
        con.executescript("DELETE FROM prospectos; DELETE FROM eventos; DELETE FROM mensajes;")


# --------------------------------------------------------------------------- mensajes

def guardar_mensaje(prospecto_id, canal, asunto, cuerpo, generado_por, aprobado_por):
    with conectar() as con:
        con.execute(
            "INSERT INTO mensajes (prospecto_id, canal, asunto, cuerpo, generado_por, aprobado_por, fecha)"
            " VALUES (?,?,?,?,?,?,?)",
            (prospecto_id, canal, asunto, cuerpo, generado_por, aprobado_por, _ahora()))


def mensajes_de(prospecto_id):
    with conectar() as con:
        return pd.read_sql_query(
            "SELECT fecha, canal, asunto, cuerpo, generado_por, aprobado_por FROM mensajes"
            " WHERE prospecto_id = ? ORDER BY id DESC", con, params=(prospecto_id,))


# --------------------------------------------------------------------------- usabilidad

def guardar_prueba(participante, rol, tarea, segundos, exito, errores, notas):
    with conectar() as con:
        con.execute(
            "INSERT INTO pruebas (participante, rol, tarea, segundos, exito, errores, notas, fecha)"
            " VALUES (?,?,?,?,?,?,?,?)",
            (participante, rol, tarea, segundos, int(exito), int(errores), notas, _ahora()))


def listar_pruebas():
    with conectar() as con:
        return pd.read_sql_query("SELECT * FROM pruebas ORDER BY id", con)


def guardar_sus(participante, respuestas, puntaje):
    with conectar() as con:
        con.execute("INSERT INTO sus (participante, respuestas, puntaje, fecha) VALUES (?,?,?,?)",
                    (participante, json.dumps(respuestas), puntaje, _ahora()))


def listar_sus():
    with conectar() as con:
        return pd.read_sql_query("SELECT * FROM sus ORDER BY id", con)

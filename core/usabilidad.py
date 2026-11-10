"""Pruebas de usabilidad: tareas, métricas y cuestionario SUS (System Usability Scale).

Métricas que pide el informe final: tiempo medio de tarea, tasa de éxito y tasa de error.
El SUS es un cuestionario estándar de 10 preguntas que da un puntaje de 0 a 100
(alrededor de 68 se considera el promedio de la industria).
"""

TAREAS = [
    "T1. Cargar la lista de empresas y clasificarlas",
    "T2. Encontrar los prospectos con prioridad A de Barranquilla",
    "T3. Explicar por qué un prospecto tiene su puntaje (ver detalle)",
    "T4. Generar, revisar y aprobar el correo de primer contacto de un prospecto A",
    "T5. Registrar que un prospecto respondió y abrir WhatsApp para continuar",
    "T6. Consultar en el tablero cuántos prospectos han respondido",
]

PREGUNTAS_SUS = [
    "Creo que me gustaría usar este sistema con frecuencia.",
    "Encontré el sistema innecesariamente complejo.",
    "Pensé que el sistema era fácil de usar.",
    "Creo que necesitaría el apoyo de una persona técnica para poder usarlo.",
    "Encontré que las funciones del sistema estaban bien integradas.",
    "Pensé que había demasiada inconsistencia en el sistema.",
    "Imagino que la mayoría de las personas aprendería a usarlo muy rápido.",
    "Encontré el sistema muy engorroso de usar.",
    "Me sentí muy seguro(a) usando el sistema.",
    "Necesité aprender muchas cosas antes de poder empezar a usar el sistema.",
]


def puntaje_sus(respuestas):
    """respuestas: 10 valores de 1 a 5. Impares suman (r-1), pares suman (5-r); total x 2.5."""
    if len(respuestas) != 10:
        raise ValueError("El SUS tiene 10 respuestas.")
    total = 0
    for i, r in enumerate(respuestas, start=1):
        total += (r - 1) if i % 2 == 1 else (5 - r)
    return total * 2.5


def interpretar_sus(puntaje):
    if puntaje >= 80.3:
        return "Excelente"
    if puntaje >= 68:
        return "Bueno (sobre el promedio)"
    if puntaje >= 51:
        return "Aceptable con mejoras"
    return "Necesita rediseño"


def resumen(df):
    """Tabla por tarea con tiempo medio, tasa de éxito y errores promedio."""
    if df.empty:
        return df
    tabla = df.groupby("tarea").agg(
        intentos=("id", "count"),
        tiempo_medio_s=("segundos", "mean"),
        tasa_exito=("exito", "mean"),
        errores_promedio=("errores", "mean"),
    ).reset_index()
    tabla["tiempo_medio_s"] = tabla["tiempo_medio_s"].round(1)
    tabla["tasa_exito"] = (tabla["tasa_exito"] * 100).round(0).astype(int).astype(str) + " %"
    tabla["errores_promedio"] = tabla["errores_promedio"].round(2)
    return tabla

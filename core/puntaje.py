"""Puntaje de prospectos (lead scoring) explicable, basado en el Anexo E.2 del informe.

Puntaje = 10 x suma(peso del criterio x valor del criterio de 0 a 10)  ->  0 a 100
Prioridad: A (>= 70) contactar primero, B (>= 50) contactar después, C mantener en base.
"""

import config

VALOR_FRECUENCIA = {"diaria": 10, "semanal": 7, "mensual": 4, "ocasional": 1}


def tamano(ingresos_millones):
    if ingresos_millones in (None, ""):
        return "Sin dato", 6
    for limite, etiqueta, valor in config.TAMANOS:
        if float(ingresos_millones) <= limite:
            return etiqueta, valor
    return "Grande", 5


def valor_ruta(c):
    if c["regiones_transmillas"]:
        return 10, "despacha a zonas de Transmillas"
    if c["clientes_actuales"]:
        return 8, "vende a sectores que ya atiende Transmillas (petróleo, salud, minería)"
    if c["regiones_cercanas"]:
        return 5, "cobertura nacional o regiones cercanas"
    return 3, "sin información de destinos: confirmar en el primer contacto"


def valor_sector(sector):
    if sector in config.SECTORES:
        return 10, f"sector objetivo ({sector})"
    return 3, "fuera de los sectores objetivo"


def valor_contacto(p):
    tiene_correo = bool((p.get("correo") or "").strip())
    tiene_tel = bool((p.get("telefono") or "").strip())
    tiene_nombre = bool((p.get("contacto_nombre") or "").strip())
    if tiene_correo and (tiene_tel or tiene_nombre):
        return 10, "contacto completo"
    if tiene_correo or tiene_tel:
        return 5, "contacto parcial"
    if (p.get("sitio_web") or "").strip():
        return 2, "solo sitio web"
    return 0, "sin datos de contacto"


def calcular(p, c):
    """p = datos de la empresa, c = resultado del clasificador. Devuelve dict para guardar."""
    etiqueta_tamano, v_tamano = tamano(p.get("ingresos_millones"))
    v_ruta, r_ruta = valor_ruta(c)
    v_sector, r_sector = valor_sector(c["sector"])
    v_contacto, r_contacto = valor_contacto(p)
    valores = {
        "ruta": (v_ruta, r_ruta),
        "frecuencia": (VALOR_FRECUENCIA[c["frecuencia"]], f"frecuencia estimada {c['frecuencia']}"),
        "tamano": (v_tamano, f"empresa {etiqueta_tamano.lower()}"),
        "sector": (v_sector, r_sector),
        "contacto": (v_contacto, r_contacto),
    }
    detalle = {k: {"valor": v, "peso": config.PESOS[k], "aporte": round(10 * v * config.PESOS[k], 1),
                   "razon": r} for k, (v, r) in valores.items()}
    puntaje = round(sum(d["aporte"] for d in detalle.values()), 1)
    if puntaje >= config.UMBRAL_A:
        prioridad = "A"
    elif puntaje >= config.UMBRAL_B:
        prioridad = "B"
    else:
        prioridad = "C"
    return {
        "sector": c["sector"],
        "tamano": etiqueta_tamano,
        "regiones": ", ".join(c["regiones"]),
        "frecuencia": c["frecuencia"],
        "puntaje": puntaje,
        "prioridad": prioridad,
        "detalle_puntaje": detalle,
        "justificacion": c["justificacion"],
        "metodo": c["metodo"],
    }


PRIORIDAD_TEXTO = {"A": "A · contactar primero", "B": "B · contactar después", "C": "C · mantener en base"}

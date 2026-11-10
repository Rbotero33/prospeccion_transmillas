"""Clasificación de cada empresa: sector, regiones a las que despacha y frecuencia.

Dos métodos que se complementan:
  1. Reglas (siempre disponibles): código CIIU + palabras clave en la descripción.
  2. IA local (opcional, Ollama): lee la descripción y estima lo que las reglas no ven.
Las reglas dan una base explicable; la IA la mejora cuando hay texto para leer.
"""

import re

import config
from core import ia_local
from core.fuentes import normalizar


def sector_por_ciiu(ciiu):
    if ciiu is None:
        return None
    try:
        ciiu = int(ciiu)
    except (TypeError, ValueError):
        return None
    for nombre, datos in config.SECTORES.items():
        for desde, hasta in datos["ciiu"]:
            if desde <= ciiu <= hasta:
                return nombre
    return None


def _contiene(texto, palabras, palabra_completa=False):
    """Palabras de la lista que aparecen en el texto. Las raíces ('agricola', 'metal') se buscan
    al inicio de palabra; los lugares se buscan como palabra completa ('meta' no es 'metalmecánica')."""
    encontradas = []
    for p in palabras:
        clave = re.escape(normalizar(p).strip())
        patron = rf"\b{clave}\b" if palabra_completa else rf"\b{clave}"
        if re.search(patron, texto) and p not in encontradas:
            encontradas.append(p)
    return encontradas


def sector_por_texto(texto):
    mejor, aciertos = None, 0
    for nombre, datos in config.SECTORES.items():
        n = len(_contiene(texto, datos["palabras"]))
        if n > aciertos:
            mejor, aciertos = nombre, n
    return mejor


def clasificar_con_reglas(p):
    texto = normalizar(f"{p.get('razon_social', '')} {p.get('descripcion') or ''}")
    sector = sector_por_ciiu(p.get("ciiu")) or sector_por_texto(texto)

    destinos = _contiene(texto, config.DESTINOS_TRANSMILLAS + config.REGIONES_TRANSMILLAS, palabra_completa=True)
    cercanas = _contiene(texto, config.REGIONES_CERCANAS, palabra_completa=True)
    clientes = _contiene(texto, config.PALABRAS_CLIENTES_ACTUALES)
    frecuentes = _contiene(texto, config.PALABRAS_DESPACHOS_FRECUENTES)

    try:
        ciiu = int(float(p.get("ciiu")))
    except (TypeError, ValueError):
        ciiu = 0
    if frecuentes or 4600 <= ciiu <= 4699:
        frecuencia = "semanal"
    elif ciiu >= 1000 and ciiu < 3400:
        frecuencia = "mensual"   # manufactura: despacha, pero sin evidencia de frecuencia
    else:
        frecuencia = "ocasional"

    razones = []
    if sector:
        razones.append(f"sector {sector}" + (f" (CIIU {ciiu})" if ciiu else ""))
    if destinos:
        razones.append("menciona zonas de Transmillas: " + ", ".join(destinos[:4]))
    elif cercanas:
        razones.append("indica cobertura amplia: " + ", ".join(cercanas[:3]))
    if clientes:
        razones.append("relación con sectores de clientes actuales: " + ", ".join(clientes[:3]))
    if frecuentes:
        razones.append("señales de despachos frecuentes: " + ", ".join(frecuentes[:3]))

    return {
        "sector": sector or "Otro",
        "regiones": destinos or cercanas,
        "regiones_transmillas": bool(destinos),
        "regiones_cercanas": bool(cercanas) and not destinos,
        "clientes_actuales": bool(clientes),
        "frecuencia": frecuencia,
        "justificacion": "; ".join(razones) or "sin señales en la información disponible",
        "metodo": "Reglas",
    }


def clasificar(p, usar_ia=False):
    """Clasifica un prospecto. Si usar_ia es True e IA está disponible, combina ambos métodos."""
    base = clasificar_con_reglas(p)
    if not usar_ia or not (p.get("descripcion") or "").strip():
        return base
    try:
        ia = ia_local.clasificar_empresa({**p, "sector": base["sector"]})
    except Exception as error:  # la IA es opcional: si falla, quedan las reglas
        base["justificacion"] += f" (IA no disponible: {type(error).__name__})"
        return base

    regiones_ia = [normalizar(r) for r in ia.get("regiones", []) if r]
    en_red = [r for r in regiones_ia
              if _contiene(r, config.DESTINOS_TRANSMILLAS + config.REGIONES_TRANSMILLAS, palabra_completa=True)]
    frecuencias = ["ocasional", "mensual", "semanal", "diaria"]
    freq_ia = ia.get("frecuencia") if ia.get("frecuencia") in frecuencias else base["frecuencia"]
    # Se toma la estimación más alta entre reglas e IA, pero la IA nunca borra lo que dicen las reglas.
    frecuencia = max(base["frecuencia"], freq_ia, key=frecuencias.index)

    return {
        **base,
        "regiones": sorted(set(base["regiones"]) | set(regiones_ia)),
        "regiones_transmillas": base["regiones_transmillas"] or bool(en_red),
        "regiones_cercanas": base["regiones_cercanas"] or (bool(regiones_ia) and not en_red),
        "clientes_actuales": base["clientes_actuales"] or bool(ia.get("vende_a_petroleo_salud_o_mineria")),
        "frecuencia": frecuencia if ia.get("despacha_mercancia", True) else "ocasional",
        "justificacion": f"{base['justificacion']}. IA: {ia.get('justificacion', '')}".strip(),
        "metodo": "Reglas + IA local",
    }

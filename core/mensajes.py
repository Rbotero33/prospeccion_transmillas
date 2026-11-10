"""Mensajes de primer contacto (correo) y de seguimiento por WhatsApp.

Regla de diseño: la IA o la plantilla proponen, un humano aprueba y envía.
El primer contacto es por correo corporativo; WhatsApp solo después de que
la empresa responda o autorice (política de WhatsApp Business).
"""

from urllib.parse import quote

import config
from core import ia_local

GANCHO_SECTOR = {
    "Agroindustria": "insumos, alimentos y productos del agro",
    "Materiales de construcción": "materiales para obras y proyectos de construcción",
    "Metalmecánica": "piezas, repuestos y equipos metalmecánicos, incluso para el sector petrolero",
}


def correo_plantilla(p, asesor):
    nombre = (p.get("contacto_nombre") or "").strip() or "equipo de logística"
    gancho = GANCHO_SECTOR.get(p.get("sector"), "su mercancía")
    asunto = f"Envíos de {p.get('razon_social', '').title()} hacia el llano y los Santanderes"
    cuerpo = (
        f"Buenos días, {nombre}:\n\n"
        f"Le escribe {asesor} de {config.EMPRESA['nombre']}. Hace {config.EMPRESA['trayectoria_anios']} años "
        f"transportamos mensajería y carga terrestre hacia Bogotá, el llano (Villavicencio, Yopal, Tame, "
        f"Saravena, Arauca) y los Santanderes (Bucaramanga, Barrancabermeja, Cúcuta), con entrega en "
        f"{config.EMPRESA['promesa_entrega']}, rastreo de cada envío con foto y firma, y crédito para empresas.\n\n"
        f"Trabajamos con empresas que despachan {gancho} hacia estas regiones. Si {p.get('razon_social', '').title()} "
        f"tiene envíos hacia allá, con gusto le preparamos una cotización según su volumen.\n\n"
        f"¿Le parece si agendamos una llamada de 10 minutos esta semana?\n\n"
        f"Cordialmente,\n{asesor}\n{config.EMPRESA['nombre']}\n\n"
        f"Si prefiere no recibir más correos nuestros, responda con la palabra NO."
    )
    return asunto, cuerpo


def correo_ia(p, asesor, instrucciones=""):
    """Versión personalizada con IA local. Si falla, devuelve la plantilla."""
    asunto, plantilla = correo_plantilla(p, asesor)
    try:
        cuerpo = ia_local.redactar_correo(config.EMPRESA, p, asesor, instrucciones)
        if "no recibir" not in cuerpo.lower():
            cuerpo += "\n\nSi prefiere no recibir más correos nuestros, responda con la palabra NO."
        return asunto, cuerpo, "IA local"
    except Exception:
        return asunto, plantilla, "Plantilla (IA no disponible)"


def seguimiento_plantilla(p, asesor):
    nombre = (p.get("contacto_nombre") or "").strip() or "equipo de logística"
    asunto = f"Re: envíos de {p.get('razon_social', '').title()} hacia el llano y los Santanderes"
    cuerpo = (
        f"Hola, {nombre}. Le escribo de nuevo desde {config.EMPRESA['nombre']}. Si tienen despachos hacia "
        f"Arauca, Yopal, Bucaramanga, Cúcuta u otras ciudades del llano y los Santanderes, le preparamos "
        f"una tarifa para su volumen (base: {config.EMPRESA['tarifa_base']}). ¿Le parece si lo llamo?\n\n"
        f"{asesor}"
    )
    return asunto, cuerpo


def whatsapp_texto(p, asesor):
    nombre = (p.get("contacto_nombre") or "").strip() or ""
    saludo = f"Hola, {nombre}." if nombre else "Hola."
    return (f"{saludo} Soy {asesor}, de {config.EMPRESA['nombre']}. Gracias por responder. "
            f"Le escribo para coordinar la cotización de sus envíos hacia el llano y los Santanderes. "
            f"¿Qué día le queda bien hablar?")


def enlace_correo(destino, asunto, cuerpo):
    return f"mailto:{destino or ''}?subject={quote(asunto)}&body={quote(cuerpo)}"


def enlace_whatsapp(telefono, texto):
    digitos = "".join(ch for ch in str(telefono or "") if ch.isdigit())
    if len(digitos) == 10:      # celular colombiano sin indicativo
        digitos = "57" + digitos
    return f"https://wa.me/{digitos}?text={quote(texto)}"

"""Conexión con un modelo de lenguaje local y gratuito (Ollama).

Ollama corre en el mismo computador, no necesita clave ni internet después de
descargar el modelo. Si no está disponible, el resto del sistema usa reglas.
"""

import json

import requests

import config


def disponible():
    """True si Ollama está corriendo y tiene el modelo configurado."""
    try:
        r = requests.get(f"{config.OLLAMA_URL}/api/tags", timeout=2)
        modelos = [m.get("name", "") for m in r.json().get("models", [])]
        base = config.OLLAMA_MODELO.split(":")[0]
        return any(m == config.OLLAMA_MODELO or m.split(":")[0] == base for m in modelos)
    except (requests.RequestException, ValueError):
        return False


def _chat(sistema, usuario, formato_json=False, temperatura=0.2):
    cuerpo = {
        "model": config.OLLAMA_MODELO,
        "messages": [{"role": "system", "content": sistema}, {"role": "user", "content": usuario}],
        "stream": False,
        "options": {"temperature": temperatura, "num_ctx": 4096},
    }
    if formato_json:
        cuerpo["format"] = "json"
    r = requests.post(f"{config.OLLAMA_URL}/api/chat", json=cuerpo, timeout=config.OLLAMA_TIMEOUT)
    r.raise_for_status()
    return r.json()["message"]["content"]


SISTEMA_CLASIFICADOR = """Eres analista comercial de una transportadora colombiana.
Lees la información pública de una empresa y estimas si podría necesitar enviar mercancía.
Responde SOLO un JSON con estas claves:
- "despacha_mercancia": true o false
- "frecuencia": "diaria", "semanal", "mensual" u "ocasional"
- "regiones": lista de ciudades o regiones de Colombia a las que probablemente envía (puede ser vacía)
- "vende_a_petroleo_salud_o_mineria": true o false
- "justificacion": una frase corta en español explicando tu estimación
No inventes datos que no se deduzcan del texto; si no hay pistas, usa "ocasional" y lista vacía."""


def clasificar_empresa(empresa):
    """Devuelve un dict con la estimación del modelo o lanza una excepción."""
    texto = (
        f"Empresa: {empresa.get('razon_social')}\n"
        f"Ciudad: {empresa.get('ciudad')}\n"
        f"Código CIIU: {empresa.get('ciiu')}\n"
        f"Sector estimado: {empresa.get('sector')}\n"
        f"Descripción / sitio web: {empresa.get('descripcion') or 'sin descripción'}"
    )
    respuesta = _chat(SISTEMA_CLASIFICADOR, texto, formato_json=True)
    datos = json.loads(respuesta)
    if not isinstance(datos.get("regiones", []), list):
        datos["regiones"] = [str(datos.get("regiones"))]
    return datos


SISTEMA_REDACTOR = """Eres asesor comercial de {empresa}. Escribes correos B2B en español de Colombia,
cordiales, concretos y sin exagerar. Máximo 120 palabras. No prometas descuentos ni datos que no
te den. Termina con una pregunta para agendar una llamada corta y una línea para dejar de recibir correos."""


def redactar_correo(empresa, prospecto, asesor, instrucciones=""):
    """Pide al modelo una versión personalizada del correo de primer contacto.
    instrucciones: petición extra del asesor (p. ej. 'más formal, menciona cadena de frío')."""
    datos = (
        f"Datos de {empresa['nombre']}: {empresa['trayectoria_anios']} años; entrega en "
        f"{empresa['promesa_entrega']}; rutas: Bogotá, el llano (Villavicencio, Yopal, Tame, Saravena, "
        f"Arauca) y los Santanderes (Bucaramanga, Barrancabermeja, Cúcuta); crédito empresarial; "
        f"servicios: {', '.join(empresa['servicios'])}.\n"
        f"Prospecto: {prospecto.get('razon_social')} ({prospecto.get('ciudad')}), sector "
        f"{prospecto.get('sector')}. {prospecto.get('justificacion') or ''}\n"
        f"Contacto: {prospecto.get('contacto_nombre') or 'equipo de logística'}. Firma: {asesor}."
    )
    if instrucciones.strip():
        datos += f"\nInstrucciones adicionales del asesor: {instrucciones.strip()}"
    return _chat(SISTEMA_REDACTOR.format(empresa=empresa["nombre"]), datos, temperatura=0.5).strip()


SISTEMA_ASISTENTE = """Eres el asistente comercial de {empresa}, una transportadora colombiana con
{anios} años que entrega en {promesa} hacia Bogotá, el llano (Villavicencio, Yopal, Tame, Saravena,
Arauquita, Arauca) y los Santanderes (Bucaramanga, Barrancabermeja, Cúcuta). Tarifa base: {tarifa}.
Seguro: {seguro}. Servicios: {servicios}. Ofrece crédito a empresas.
Ayudas al asesor a analizar prospectos y preparar el contacto comercial B2B.
Reglas: responde en español de Colombia, de forma concreta; usa SOLO los datos que te den;
si algo no está en los datos, dilo y sugiere cómo averiguarlo; no inventes cifras, nombres ni contactos."""


def chatear_stream(mensajes, contexto):
    """Chat del asistente flotante. Devuelve la respuesta por partes (streaming) para que
    el texto aparezca a medida que el modelo lo genera.

    mensajes: historial [{"role": "user" | "assistant", "content": "..."}]
    contexto: texto con los datos de los prospectos sobre los que se conversa."""
    e = config.EMPRESA
    sistema = SISTEMA_ASISTENTE.format(
        empresa=e["nombre"], anios=e["trayectoria_anios"], promesa=e["promesa_entrega"],
        tarifa=e["tarifa_base"], seguro=e["seguro"], servicios=", ".join(e["servicios"]))
    sistema += f"\n\nDATOS DE LOS PROSPECTOS:\n{contexto}"
    cuerpo = {
        "model": config.OLLAMA_MODELO,
        "messages": [{"role": "system", "content": sistema}] + mensajes[-8:],
        "stream": True,
        "options": {"temperature": 0.4, "num_ctx": 4096},
    }
    with requests.post(f"{config.OLLAMA_URL}/api/chat", json=cuerpo, stream=True,
                       timeout=(5, config.OLLAMA_TIMEOUT)) as r:
        r.raise_for_status()
        for linea in r.iter_lines():
            if not linea:
                continue
            dato = json.loads(linea)
            trozo = dato.get("message", {}).get("content", "")
            if trozo:
                yield trozo
            if dato.get("done"):
                break

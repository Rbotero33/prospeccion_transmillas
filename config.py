"""
Configuración del prototipo de prospección B2B de Transmillas.

Todo lo que el equipo comercial podría querer ajustar está aquí:
datos de la empresa, sectores objetivo (por código CIIU), palabras clave,
pesos del puntaje y opciones de la IA local. No hace falta tocar el resto del código.
"""

# --------------------------------------------------------------------------- empresa

EMPRESA = {
    "nombre": "Transmillas Logística y Transportadora",
    "trayectoria_anios": 25,
    "promesa_entrega": "24 horas (máximo 48 horas en toda la red)",
    "tarifa_base": "$20.000 de 1 a 5 kg y $2.500 por kilo adicional",
    "seguro": "1 % del valor declarado (valor asegurado mínimo $100.000)",
    "servicios": [
        "paquetes y mensajería", "carga puerta a puerta", "transporte de carga",
        "transporte para empresas", "cadena de frío", "mudanzas", "carga urgente",
        "pago contraentrega",
    ],
    "credito_empresarial": True,
}

# Ciudades donde Transmillas entrega (sedes, oficinas virtuales y Cúcuta en operación).
DESTINOS_TRANSMILLAS = [
    "bogota", "villavicencio", "yopal", "tame", "saravena", "arauquita", "arauca",
    "bucaramanga", "barrancabermeja", "cucuta",
]
# Regiones relacionadas (si una empresa menciona estas zonas, probablemente envía allá).
REGIONES_TRANSMILLAS = [
    "llano", "llanos orientales", "orinoquia", "casanare", "meta", "arauca",
    "santander", "santanderes", "norte de santander", "magdalena medio",
]
# Zonas que también dan puntos parciales (cobertura nacional, pero no son la ruta fuerte).
REGIONES_CERCANAS = ["boyaca", "cundinamarca", "cesar", "todo el pais", "nivel nacional", "cobertura nacional"]

CIUDADES_OBJETIVO = ["MEDELLÍN", "BARRANQUILLA"]

# --------------------------------------------------------------------------- sectores

# Rangos de CIIU Rev. 4 A.C. (en el dataset de Supersociedades el CIIU es numérico,
# por eso 0111 aparece como 111). Cada tupla es (desde, hasta) inclusive.
SECTORES = {
    "Agroindustria": {
        "ciiu": [(111, 322), (1011, 1090), (2012, 2012), (2021, 2021), (4620, 4620), (4653, 4653)],
        "palabras": ["agro", "agricola", "agropecuari", "fertiliz", "abono", "semilla", "pecuari",
                     "ganad", "concentrado", "alimento para animales", "palma", "arroz", "cafe",
                     "cacao", "insumos agricolas", "veterinari", "riego", "agroquimic"],
    },
    "Materiales de construcción": {
        "ciiu": [(1630, 1630), (2310, 2310), (2391, 2399), (2221, 2221), (4663, 4663), (4752, 4752)],
        "palabras": ["cemento", "concreto", "ladrillo", "ceramic", "vidrio", "construcc", "ferreter",
                     "acabados", "tuberia", "pvc", "agregados", "cal ", "drywall", "pintura",
                     "materiales de construccion", "prefabricad"],
    },
    "Metalmecánica": {
        "ciiu": [(2410, 2432), (2511, 2599), (2811, 2829), (2930, 2930), (3311, 3320)],
        "palabras": ["metalmecanic", "acero", "metal", "soldadura", "mecanizado", "torno", "forja",
                     "estructuras metalicas", "valvula", "maquinaria", "repuesto", "herramienta",
                     "tornilleria", "fundicion", "galvaniz", "tuberia de acero"],
    },
}

# Sectores de los clientes actuales de Transmillas: si la empresa les vende a ellos,
# es muy probable que despache hacia las mismas zonas (petróleo en Arauca/Casanare, salud, etc.).
PALABRAS_CLIENTES_ACTUALES = [
    "petrol", "oil", "gas", "hidrocarburo", "pozo", "perforacion", "sismic", "energia",
    "mineria", "hospital", "clinica", "laboratorio", "ips", "eps",
]

# Pistas de que la empresa despacha mercancía con frecuencia.
PALABRAS_DESPACHOS_FRECUENTES = [
    "distribuidor", "distribucion", "mayorista", "despachos", "envios", "entregas",
    "a todo el pais", "a nivel nacional", "cobertura nacional", "red de distribucion",
    "sucursales", "puntos de venta", "proveedor de",
]

# --------------------------------------------------------------------------- puntaje

# Mismos criterios del Anexo E.2 del informe, ajustados al nuevo segmento.
# Los pesos deben sumar 1.0. Puntaje final = 10 x suma(peso x valor de 0 a 10).
PESOS = {
    "ruta": 0.35,        # ¿despacha hacia donde llega Transmillas?
    "frecuencia": 0.25,  # ¿qué tanto despacha?
    "tamano": 0.20,      # pyme mediana = mejor ajuste
    "sector": 0.15,      # afinidad del sector objetivo
    "contacto": 0.05,    # calidad de los datos de contacto
}

UMBRAL_A = 70  # contactar primero
UMBRAL_B = 50  # contactar después; por debajo = mantener en base

# Tamaño por ingresos operacionales anuales en MILLONES de pesos (rangos aproximados,
# ajústenlos con la clasificación oficial que use Transmillas).
TAMANOS = [  # (ingresos hasta, etiqueta, valor del criterio)
    (1_000, "Micro", 4),
    (20_000, "Pequeña", 7),
    (120_000, "Mediana", 10),
    (float("inf"), "Grande", 5),  # suelen tener contratos con las transportadoras grandes
]

# --------------------------------------------------------------------------- IA local

# La IA corre gratis en el computador con Ollama (https://ollama.com).
# Si Ollama no está instalado, el sistema funciona igual con reglas y plantillas.
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODELO = "llama3.2:3b"   # liviano (~2 GB). Alternativa: "qwen2.5:7b" si el PC tiene 16 GB de RAM.
OLLAMA_TIMEOUT = 120             # segundos

# --------------------------------------------------------------------------- datos abiertos

# "10.000 Empresas más Grandes del País" — Supersociedades, Portal de Datos Abiertos.
DATOS_GOV_DATASET = "https://www.datos.gov.co/resource/6cat-2gcs.json"
DATOS_GOV_ANIO = 2025

# --------------------------------------------------------------------------- seguimiento

ESTADOS = [
    "Nuevo", "Aprobado para contacto", "Contactado (correo)", "Seguimiento enviado",
    "Respondió", "Autorizó WhatsApp", "Reunión / cotización", "Cliente", "Descartado",
]
# WhatsApp solo se habilita cuando el prospecto ya respondió o dio su autorización
# (política de WhatsApp Business: se necesita aceptación previa).
ESTADOS_WHATSAPP_PERMITIDO = ["Respondió", "Autorizó WhatsApp", "Reunión / cotización", "Cliente"]

DB_PATH = "data/prospeccion.db"

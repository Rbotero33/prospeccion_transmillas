"""Fuentes de empresas: datos abiertos de Supersociedades y archivos CSV/Excel propios."""

import re
import unicodedata

import pandas as pd
import requests

import config


def normalizar(texto):
    """minúsculas y sin tildes, para comparar textos."""
    texto = unicodedata.normalize("NFKD", str(texto or "")).encode("ascii", "ignore").decode()
    return texto.lower().strip()


def ingresos_a_millones(valor, unidad="billones"):
    """El dataset de Supersociedades trae textos como '$ 0.24' en billones de pesos."""
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return None
    texto = str(valor).replace("$", "").replace(" ", "")
    if texto.count(",") and texto.count("."):
        texto = texto.replace(".", "").replace(",", ".")
    else:
        texto = texto.replace(",", ".")
    try:
        numero = float(texto)
    except ValueError:
        return None
    factor = {"billones": 1_000_000, "millones": 1, "pesos": 1 / 1_000_000}[unidad]
    return round(numero * factor, 1)


def _filtro_ciiu():
    rangos = []
    for sector in config.SECTORES.values():
        for desde, hasta in sector["ciiu"]:
            rangos.append(f"ciiu = {desde}" if desde == hasta else f"ciiu between {desde} and {hasta}")
    return "(" + " OR ".join(rangos) + ")"


def descargar_datos_gov(ciudades=None, anio=None, limite=2000):
    """Descarga empresas de los sectores objetivo desde datos.gov.co (gratis, sin clave).

    Dataset: '10.000 Empresas más Grandes del País' (Supersociedades).
    Ojo: solo trae las empresas más grandes; para pymes hay que complementar
    con EMIS, la Cámara de Comercio o listas propias.
    """
    ciudades = ciudades or config.CIUDADES_OBJETIVO
    anio = anio or config.DATOS_GOV_ANIO
    filtro_ciudades = " OR ".join(
        f"upper(ciudad_domicilio) like '%{normalizar(c).upper()[:6]}%'" for c in ciudades)
    where = f"a_o_de_corte = {anio} AND ({filtro_ciudades}) AND {_filtro_ciiu()}"
    respuesta = requests.get(config.DATOS_GOV_DATASET,
                             params={"$where": where, "$limit": limite}, timeout=60)
    respuesta.raise_for_status()
    filas = []
    for r in respuesta.json():
        filas.append({
            "nit": str(r.get("nit", "")).split(".")[0],
            "razon_social": r.get("raz_n_social", "").strip(),
            "ciudad": r.get("ciudad_domicilio", ""),
            "ciiu": int(float(r["ciiu"])) if r.get("ciiu") else None,
            "ingresos_millones": ingresos_a_millones(r.get("ingresos_operacionales")),
            "fuente": f"datos.gov.co Supersociedades {anio}",
        })
    return filas


# Nombres de columnas aceptados al importar un archivo (en minúsculas y sin tildes).
SINONIMOS = {
    "nit": ["nit", "identificacion", "nit empresa"],
    "razon_social": ["razon_social", "razon social", "empresa", "nombre", "raz_n_social", "company name"],
    "ciudad": ["ciudad", "ciudad_domicilio", "municipio", "city"],
    "ciiu": ["ciiu", "codigo ciiu", "actividad", "actividad economica"],
    "ingresos_millones": ["ingresos_millones", "ingresos (millones)", "ingresos"],
    "sitio_web": ["sitio_web", "sitio web", "web", "pagina web", "website"],
    "correo": ["correo", "email", "e-mail", "correo electronico"],
    "telefono": ["telefono", "celular", "phone", "tel"],
    "contacto_nombre": ["contacto_nombre", "contacto", "nombre contacto"],
    "contacto_cargo": ["contacto_cargo", "cargo"],
    "descripcion": ["descripcion", "description", "productos", "que hace", "resumen"],
}


def leer_archivo(archivo, nombre_fuente):
    """Lee un CSV o Excel (por ejemplo, una exportación de EMIS) y lo convierte a filas."""
    nombre = getattr(archivo, "name", str(archivo)).lower()
    if nombre.endswith((".xlsx", ".xls")):
        df = pd.read_excel(archivo)
    else:
        df = pd.read_csv(archivo, sep=None, engine="python", dtype=str)
    columnas = {}
    for col in df.columns:
        clave = normalizar(col)
        for campo, nombres in SINONIMOS.items():
            if clave in nombres and campo not in columnas.values():
                columnas[col] = campo
                break
    df = df.rename(columns=columnas)
    if "razon_social" not in df.columns:
        raise ValueError("El archivo necesita una columna con el nombre de la empresa "
                         "(razon_social, empresa o nombre).")
    filas = []
    for _, r in df.iterrows():
        fila = {c: (None if pd.isna(r.get(c)) else r.get(c)) for c in SINONIMOS if c in df.columns}
        if fila.get("nit"):
            fila["nit"] = re.sub(r"[^0-9]", "", str(fila["nit"]).split(".")[0].split("-")[0]) or None
        if fila.get("ciiu"):
            digitos = re.sub(r"[^0-9]", "", str(fila["ciiu"]))[:4]
            fila["ciiu"] = int(digitos) if digitos else None
        if fila.get("ingresos_millones") is not None:
            fila["ingresos_millones"] = ingresos_a_millones(fila["ingresos_millones"], "millones")
        fila["fuente"] = nombre_fuente
        filas.append(fila)
    return filas


def leer_descripcion_web(url, timeout=10):
    """Lee el título y la descripción de la página principal de una empresa,
    respetando robots.txt. Devuelve un texto corto o '' si no se puede."""
    from urllib import robotparser
    from urllib.parse import urlparse

    if not url:
        return ""
    if not url.startswith("http"):
        url = "https://" + url
    base = "{0.scheme}://{0.netloc}".format(urlparse(url))
    robots = robotparser.RobotFileParser(base + "/robots.txt")
    try:
        robots.read()
        if not robots.can_fetch("ProspeccionTransmillas", url):
            return ""
    except Exception:
        pass
    try:
        html = requests.get(url, timeout=timeout,
                            headers={"User-Agent": "ProspeccionTransmillas/0.1 (prototipo académico)"}).text
    except requests.RequestException:
        return ""
    partes = re.findall(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    partes += re.findall(r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']', html, re.I | re.S)
    partes += re.findall(r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\'](.*?)["\']', html, re.I | re.S)
    texto = " ".join(re.sub(r"\s+", " ", p).strip() for p in partes)
    return texto[:800]

# Prospección comercial B2B con IA — Transmillas

App web local (Python + Streamlit) que **identifica, prioriza y ayuda a contactar** empresas de
agroindustria, materiales de construcción y metalmecánica en **Medellín y Barranquilla** que podrían
enviar carga hacia la red de Transmillas (Bogotá, el llano y los Santanderes).

Costo: **$0**. Sin claves de API. La IA corre en el computador con Ollama y es opcional: sin ella la app funciona con reglas y plantillas.

## 1. Instalación en Linux (VS Code)

```bash
cd prospeccion_transmillas          # la carpeta que contiene app.py
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
Se abre en `http://localhost:8501`. Para detenerla: `Ctrl + C` en la terminal.

### IA local (opcional, gratis)
En la terminal del sistema (no la de VS Code):
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2:3b
```
Al recargar la app, la barra lateral muestra **IA local activa**. El modelo se cambia en `config.py` (`OLLAMA_MODELO`).

## 2. Cómo se usa

| Sección | Qué hace |
|---|---|
| **Tablero** | Indicadores, embudo de prospección, prioridad por ciudad, sectores y siguientes contactos |
| **Cargar empresas** | Datos abiertos (Supersociedades, datos.gov.co), archivo CSV/Excel o registro manual. Luego **Clasificar** |
| **Prospectos priorizados** | Filtros y tabla. Al seleccionar una fila se abre la ficha con el desglose del puntaje |
| **Contacto y seguimiento** | Correo (plantilla o IA) que el asesor aprueba, registro de respuestas, WhatsApp e historial |
| **Pruebas de usabilidad** | Cronómetro por tarea, cuestionario SUS y resultados |
| **Asistente (botón de la esquina)** | Chat con la IA local sobre la empresa en pantalla o sobre los prospectos A y B |

WhatsApp solo se habilita cuando la empresa respondió o autorizó el contacto.

## 3. Cómo funciona el puntaje

`Puntaje = 10 × Σ (peso × valor de 0 a 10)`

| Criterio | Peso | Cómo se estima |
|---|---|---|
| Ruta | 35 % | 10 si menciona destinos de Transmillas; 8 si vende a petróleo, salud o minería; 5 si tiene cobertura nacional; 3 sin información |
| Frecuencia | 25 % | Diaria 10 · semanal 7 · mensual 4 · ocasional 1 |
| Tamaño | 20 % | Mediana 10 · pequeña 7 · grande 5 · micro 4 (rangos en `config.py`) |
| Sector | 15 % | 10 si el CIIU o el texto corresponde a un sector objetivo |
| Contacto | 5 % | Completo 10 · parcial 5 · solo web 2 · nada 0 |

**A ≥ 70** contactar primero · **B ≥ 50** contactar después · **C** mantener en la base.

## 4. Estructura

```
app.py                 arranque: navegación, barra lateral y asistente flotante
config.py              datos de Transmillas, sectores/CIIU, palabras clave, pesos y modelo de IA
paginas/               una página por archivo (tablero, cargar, prospectos, contacto, usabilidad)
ui/estilos.py          sistema de diseño: colores, iconos y componentes
ui/graficos.py         gráficos del tablero (Altair)
ui/asistente.py        chat flotante de la IA
core/                  lógica: fuentes, clasificador, puntaje, mensajes, IA local, base de datos
.streamlit/config.toml tema (colores, tipografía) y opciones del servidor
static/                tipografía Inter (licencia OFL), incluida para que funcione sin internet
data/                  copia de Supersociedades 2025, archivo de pruebas y base SQLite
```

## 5. Cambiar la identidad visual

- **Colores de la interfaz:** variables `--tm-...` al inicio de `ui/estilos.py` y sección `[theme]` de `.streamlit/config.toml`.
- **Colores de prioridad A/B/C:** `PRIORIDAD_COLOR` en `ui/estilos.py` (los usan las insignias, la tabla y los gráficos).
- **Nombre y lema de la barra lateral:** función `marca()` en `ui/estilos.py`.

## 6. Datos y aspectos legales

- El dataset abierto solo trae empresas grandes. Para pymes, importe una lista propia (por ejemplo, de EMIS o de la Cámara de Comercio) desde **Archivo CSV / Excel**.
- `data/empresas_ficticias_demo.csv` es solo para pruebas internas; sus nombres terminan en "(ficticia)".
- El nombre, correo y celular de una persona son datos personales (Ley 1581 de 2012): use fuentes públicas o autorizadas y respete las solicitudes de baja.
- WhatsApp Business exige que la persona acepte antes de recibir el primer mensaje; por eso el primer contacto es por correo.

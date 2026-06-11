# Vision AI Pipeline

Pipeline de **visión por computador** que detecta y sigue objetos en tiempo real sobre un flujo de vídeo (webcam, fichero o RTSP) y, cuando identifica situaciones potencialmente relevantes (objetos que quedan estáticos), delega en un **agente de IA generativa** que describe la escena, evalúa el nivel de riesgo y emite una alerta.

Combina:

- **YOLOv8** ([ultralytics](https://github.com/ultralytics/ultralytics)) para detección de objetos.
- **DeepSORT** ([deep-sort-realtime](https://github.com/levan92/deep_sort_realtime)) para seguimiento multi-objeto con IDs persistentes.
- **LangChain + LangGraph** orquestando un agente con un modelo de visión de **Groq** (`llama-4-scout`) para analizar la escena y razonar sobre el riesgo.
- **FastAPI** para exponer los eventos vía API REST + WebSocket.

> ⚠️ El proyecto está en desarrollo activo (organizado por sprints). Algunos módulos descritos en el roadmap todavía no están implementados — ver [Estado del proyecto](#estado-del-proyecto).

---

## Arquitectura

```
┌──────────────┐   frames   ┌───────────────┐  detecciones  ┌──────────┐  tracks  ┌────────────────┐
│ VideoSource  │──────────▶ │ YOLODetector  │─────────────▶ │ Tracker  │────────▶ │ EventDetector  │
│ (cam/file/   │            │ (YOLOv8)      │               │(DeepSORT)│          │ (objetos       │
│  RTSP)       │            └───────────────┘               └──────────┘          │  estáticos)    │
└──────────────┘                                                                  └───────┬────────┘
                                                                                          │ static_objects
                                                                                          ▼
                                                          ┌─────────────────────────────────────────┐
                                                          │  Agente de alerta (LangGraph)             │
                                                          │                                           │
                                                          │  analyze_scene → decide_risk → ┬─ high/med │
                                                          │   (SceneAnalyzer/Groq Vision)  │  └─ low ──┐│
                                                          │                                send_alert  ││
                                                          │                                  ignore ◀──┘│
                                                          └─────────────────┬─────────────────────────┘
                                                                            │ alert_message
                                                                            ▼
                                                                 ┌────────────────────┐
                                                                 │  FastAPI (api.py)   │
                                                                 │  /events /status    │
                                                                 │  /stream (WebSocket)│
                                                                 └────────────────────┘
```

### Flujo del pipeline ([src/run_pipeline.py](src/run_pipeline.py))

1. Se abre la fuente de vídeo y se lee frame a frame.
2. Cada frame se redimensiona y pasa por **YOLODetector** → lista de `Detection`.
3. **Tracker** (DeepSORT) asigna un ID estable a cada objeto entre frames.
4. **EventDetector** mantiene el historial de posiciones de cada track y detecta los que llevan estáticos un nº de frames (posible objeto abandonado, persona inmóvil, etc.).
5. Si hay objetos estáticos —y respetando un intervalo mínimo entre análisis (`analysis_interval = 10s`)— se invoca el **agente de IA**.
6. El agente describe la escena, decide el riesgo y genera (o no) un `alert_message`.

### El agente de alerta ([src/alert_agent.py](src/alert_agent.py))

Implementado como un grafo de estados con **LangGraph**:

| Nodo            | Función                                                                            |
| --------------- | --------------------------------------------------------------------------------- |
| `analyze_scene` | Envía el frame al modelo de visión Groq y obtiene una descripción textual.        |
| `decide_risk`   | Pide al LLM que clasifique el riesgo en `low` / `medium` / `high`.                 |
| `send_alert`    | (riesgo medio/alto) Compone el mensaje de alerta.                                  |
| `ignore`        | (riesgo bajo) No hace nada.                                                        |

El enrutado entre `send_alert` e `ignore` se decide mediante una **arista condicional** según el `risk_level`.

---

## Estructura del repositorio

```
vision-ai-pipeline/
├── src/
│   ├── capture/
│   │   └── video_source.py      # Abstracción de fuente de vídeo (webcam/fichero/RTSP)
│   ├── detection/
│   │   ├── detection.py         # Dataclass Detection (bbox, center, area)
│   │   ├── yolo_detector.py     # Wrapper de YOLOv8
│   │   ├── tracker.py           # Tracking con DeepSORT + anotación
│   │   └── event_detector.py    # Detección de objetos estáticos
│   ├── scene_analyzer.py        # Descripción de escena (Groq Vision)
│   ├── alert_agent.py           # Agente LangGraph de análisis de riesgo
│   ├── run_pipeline.py          # Punto de entrada del pipeline
│   ├── api.py                   # API FastAPI + WebSocket
│   └── utils.py                 # Paleta de colores para anotaciones
├── requirements.txt
└── README.md
```

---

## Requisitos

- **Python 3.10+**
- Una **API key de Groq** (para `scene_analyzer` y `alert_agent`).
- Pesos de YOLOv8 (`yolov8n.pt`) — `ultralytics` los descarga automáticamente la primera vez.

## Instalación

```bash
# 1. Clonar el repositorio
git clone <url-del-repo>
cd vision-ai-pipeline

# 2. Crear y activar un entorno virtual
python -m venv .venv
.venv\Scripts\activate        # Windows (PowerShell)
# source .venv/bin/activate   # Linux/macOS

# 3. Instalar dependencias
pip install -r requirements.txt
```

### Configuración

Crea un fichero `.env` en la raíz del proyecto con tu clave de Groq:

```env
GROQ_API_KEY=tu_api_key_aqui
```

`load_dotenv()` la carga automáticamente en `scene_analyzer.py` y `alert_agent.py`.

---

## Uso

### Ejecutar el pipeline directamente

```bash
cd src
python run_pipeline.py
```

Por defecto procesa `test.mp4`. Se abre una ventana de OpenCV con las detecciones anotadas; pulsa **`q`** para salir. Las alertas generadas se imprimen por consola.

Para usar la webcam o ajustar parámetros, edita la llamada en `run_pipeline.py` o invócala desde tu propio script:

```python
from run_pipeline import run_pipeline

run_pipeline(
    video_source=0,            # 0 = webcam, ruta a fichero, o URL RTSP
    model_path="yolov8n.pt",   # cualquier modelo YOLOv8
    confidence=0.3,            # umbral de confianza
)
```

### Ejecutar la API

```bash
cd src
uvicorn api:app --reload
```

| Endpoint        | Método    | Descripción                                            |
| --------------- | --------- | ------------------------------------------------------ |
| `/events`       | GET       | Lista de alertas acumuladas.                           |
| `/status`       | GET       | Estado del pipeline y nº total de eventos.             |
| `/stream`       | WebSocket | Canal de streaming (esqueleto, en desarrollo).         |

El pipeline arranca en un hilo en segundo plano al iniciar la aplicación (`@app.on_event("startup")`).

---

## Parámetros principales

| Componente       | Parámetro          | Por defecto | Significado                                                  |
| ---------------- | ------------------ | ----------- | ----------------------------------------------------------- |
| `YOLODetector`   | `confidence`       | `0.5`       | Umbral mínimo de confianza para una detección.              |
| `Tracker`        | `max_age`          | `30`        | Frames que un track sobrevive sin detecciones.              |
| `EventDetector`  | `static_threshold` | `30`        | Nº de frames de historial para evaluar si un objeto está quieto. |
| `EventDetector`  | `max_distance`     | `10`        | Distancia (px) por debajo de la cual se considera estático. |
| `run_pipeline`   | `analysis_interval`| `10` (s)    | Tiempo mínimo entre invocaciones al agente de IA.           |

---

## Estado del proyecto

El desarrollo está organizado por sprints (ver historial de commits):

- ✅ **Sprint 1–2** — Captura de vídeo, detección YOLOv8, tracking DeepSORT y detección de eventos (objetos estáticos).
- ✅ **Sprint 3** — Descripción de escena con Groq Vision y agente de riesgo con LangGraph.
- 🚧 **Sprint 4** — API FastAPI (en curso) y dashboard con Streamlit.

### Tareas pendientes

- [ ] Almacenar los eventos y avisos en base de datos (SQLite previsto).
- [ ] Integrar bot de Telegram para notificaciones.
- [ ] Completar el canal WebSocket `/stream` (actualmente emite un mensaje placeholder).
- [ ] Dashboard de Streamlit.
- [ ] Tests automatizados (`pytest` ya está en dependencias).

> Algunos módulos que aparecen en `folder_structure.txt` (`storage/event_store.py`, `notifier/telegram_bot.py`, `dashboard/app.py`, `Dockerfile`, etc.) corresponden al diseño objetivo y **aún no están implementados**.

---

## Stack tecnológico

| Área                  | Tecnología                                              |
| --------------------- | ------------------------------------------------------- |
| Visión por computador | OpenCV, YOLOv8 (ultralytics), DeepSORT                  |
| IA generativa         | LangChain, LangGraph, Groq (`llama-4-scout-17b`)        |
| API / backend         | FastAPI, Uvicorn, WebSockets                            |
| Dashboard (previsto)  | Streamlit                                               |
| Notificaciones (prev.)| python-telegram-bot                                     |
| Utilidades            | python-dotenv, pydantic, pillow, numpy                 |
| Testing               | pytest, pytest-asyncio                                  |

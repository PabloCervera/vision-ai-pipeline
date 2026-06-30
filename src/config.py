"""
Rutas centralizadas del proyecto.
Resuelve la ubicación de los datos generados en ejecución de forma relativa a la raíz
del proyecto (y no al directorio de trabajo), de modo que el pipeline, la API y la base
de datos escriban siempre en el mismo sitio independientemente de desde dónde se lancen.
"""

from pathlib import Path

# Raíz del proyecto (carpeta que contiene a src/).
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Datos generados en ejecución, todos bajo data/.
DATA_DIR = PROJECT_ROOT / "data"
UPLOADS_DIR = DATA_DIR / "uploads"   # vídeos subidos por el usuario
FRAMES_DIR = DATA_DIR / "frames"     # capturas de los eventos detectados
DB_PATH = DATA_DIR / "events.db"     # base de datos SQLite de eventos

# Garantiza que los directorios existan antes de escribir en ellos.
for _dir in (UPLOADS_DIR, FRAMES_DIR):
    _dir.mkdir(parents=True, exist_ok=True)

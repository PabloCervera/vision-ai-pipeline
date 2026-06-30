"""
Módulo para manejar el almacenamiento de eventos en una base de datos SQLite.
Este módulo define la clase EventStore, que proporciona métodos para almacenar y recuperar eventos de una base
de datos SQLite. Cada evento contiene información sobre el momento en que ocurrió, 
el ID del objeto rastreado, el mensaje de alerta y el nivel de riesgo asociado.
"""

import sqlite3

from config import DB_PATH


class EventStore:
    """
    Clase para manejar el almacenamiento de eventos en una base de datos SQLite.
    Esta clase proporciona métodos para almacenar y recuperar eventos de una base de datos SQLite.
    Cada evento contiene información sobre el momento en que ocurrió,
    el ID del objeto rastreado, el mensaje de alerta y el nivel de riesgo asociado.
    """

    def __init__(self, db_path=DB_PATH):
        """
        Inicializa la conexión a la base de datos SQLite y crea la tabla de eventos si no existe.
        """
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._create_table()

    def _create_table(self):
        """Crea la tabla de eventos si no existe."""
        
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                track_id TEXT NOT NULL,
                alert TEXT NOT NULL,
                risk_level TEXT NOT NULL, 
                frame_path TEXT NOT NULL
            )
        """)
        self._conn.commit()
        
    def add_event(self, track_id, alert, risk_level, timestamp, frame_path):
        """Añade un nuevo evento a la base de datos."""
        self._conn.execute("""
            INSERT INTO events (timestamp, track_id, alert, risk_level, frame_path)
            VALUES (?, ?, ?, ?, ?)
        """, (timestamp, track_id, alert, risk_level, frame_path))
        self._conn.commit()
        
    def get_all_events(self):
        """Recupera todos los eventos de la base de datos."""
        cursor = self._conn.execute("SELECT * FROM events ORDER BY id DESC")
        return [dict(row) for row in cursor.fetchall()]
    
    def clear_events(self):
        """Elimina todos los eventos de la base de datos."""
        self._conn.execute("DELETE FROM events")
        self._conn.commit()
        
    def get_recent_events(self, limit=20):
        """Recupera los eventos más recientes, limitados en cantidad."""
        cursor = self._conn.execute("SELECT * FROM events ORDER BY id DESC LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()]
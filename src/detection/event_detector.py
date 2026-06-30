"""
Módulo para detectar eventos específicos basados en el historial de posiciones de los objetos trackeados.
Este módulo define la clase EventDetector, que encapsula la lógica para analizar el historial de posiciones
"""

import math

class EventDetector:
    """
    Detecta eventos específicos basados en el historial de posiciones de los objetos.
    Esta clase mantiene un historial de posiciones para cada objeto trackeado y analiza este historial
    """
    def __init__(self, static_threshold=30, max_distance=10):
        """
        Inicializa el detector de eventos con los parámetros necesarios.
        """
        self.positions = {}
        self.static_counts = {}   # frames consecutivos que cada track lleva inmóvil
        self.static_threshold = static_threshold
        self.max_distance = max_distance

    def update(self, tracks):
        """
        Actualiza el historial de posiciones y devuelve los objetos estáticos detectados.

        Cada objeto estático se devuelve con metadatos para fundamentar el análisis de
        riesgo posterior: identificador, clase, centro y nº de frames que lleva inmóvil.

        """
        static_objects = []
        for track in tracks:
            if not track.is_confirmed():
                continue

            track_id = track.track_id
            x1, y1, x2, y2 = map(int, track.to_ltrb())
            center = ((x1 + x2) // 2, (y1 + y2) // 2)

            history = self.positions.setdefault(track_id, [])
            history.append(center)
            if len(history) > self.static_threshold:
                history.pop(0)

            is_static = False
            if len(history) == self.static_threshold:
                first, last = history[0], history[-1]
                distance = math.hypot(last[0] - first[0], last[1] - first[1])
                is_static = distance < self.max_distance

            if is_static:
                self.static_counts[track_id] = self.static_counts.get(track_id, self.static_threshold - 1) + 1
                static_objects.append({
                    "track_id": track_id,
                    "class_name": track.get_det_class(),
                    "center": center,
                    "static_frames": self.static_counts[track_id],
                })
            else:
                self.static_counts.pop(track_id, None)

        return static_objects

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
        self.static_threshold = static_threshold
        self.max_distance = max_distance

    def update(self, tracks):
        """
        Actualiza el historial de posiciones con los nuevos tracks y detecta eventos basados en el movimiento.
        """
        static_objects = []
        for track in tracks:
            if track.is_confirmed():
                track_id = track.track_id
                x1, y1, x2, y2 = map(int, track.to_ltrb())
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                if track_id not in self.positions:
                    self.positions[track_id] = []
                self.positions[track_id].append((center_x, center_y))
                if len(self.positions[track_id]) > self.static_threshold:
                    self.positions[track_id].pop(0)
                if len(self.positions[track_id]) == self.static_threshold:
                    first = self.positions[track_id][0]
                    last = self.positions[track_id][-1]
                    distance = math.sqrt((last[0] - first[0]) ** 2 + (last[1] - first[1]) ** 2)
                    if distance < self.max_distance:
                        static_objects.append({"track_id": track_id, "center": (center_x, center_y)})
        
        return static_objects
        
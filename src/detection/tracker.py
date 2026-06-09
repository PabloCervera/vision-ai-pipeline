"""
Módulo para manejar el tracking de objetos detectados en los frames.
Este módulo define la clase Tracker, que encapsula la lógica para realizar el seguimiento de objetos a
partir de las detecciones realizadas por el modelo YOLO.
"""

import cv2
from deep_sort_realtime.deepsort_tracker import DeepSort
from utils import COLORS

class Tracker:
    """
    Clase para manejar el tracking de objetos detectados en los frames.
    Esta clase encapsula la lógica para realizar el seguimiento de objetos a partir de las detecciones realizadas por el modelo YOLO.
    """
    
    def __init__(self, max_age=30):
        self.tracker = DeepSort(max_age=max_age)
    
    def update(self, detections, frame):
        """
        Actualiza el tracker con las nuevas detecciones.
        Args:
            detections (List[Detection]): Lista de objetos detectados con su clase, confianza y coordenadas.
            frame (numpy.ndarray): El frame de video actual.
        Returns:
            List[Track]: Lista de objetos trackeados con su ID, clase, confianza y coordenadas.
        """
        raw = [
            [[det.x1, det.y1, det.x2 - det.x1, det.y2 - det.y1], det.confidence, det.class_name]
            for det in detections
        ]
        tracks = self.tracker.update_tracks(raw, frame=frame)
        return tracks
    
    def annotate(self, frame, tracks):
        """
        Anota el frame con los objetos trackeados.
        Args:
            frame (numpy.ndarray): El frame de video actual.
            tracks (List[Track]): Lista de objetos trackeados.
        Returns:
            numpy.ndarray: El frame anotado con los objetos trackeados.
        """
        frame = frame.copy()
        for track in tracks:
            if track.is_confirmed():
                x1, y1, x2, y2 = map(int, track.to_ltrb())
                track_id = track.track_id
                class_name = track.get_det_class()
                confidence = track.get_det_conf() or 0.0
                label = f"{class_name} {confidence:.2f} ID:{track_id}"
                track_id = int(track.track_id)
                color = COLORS[track_id % len(COLORS)]
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        return frame
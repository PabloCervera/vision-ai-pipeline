"""
Módulo para manejar la detección de objetos utilizando el modelo YOLO.
Este módulo define la clase YOLODetector, que encapsula la lógica para cargar el modelo YOLO y realizar detecciones en imágenes.
"""

import cv2
from ultralytics import YOLO
from detection.detection import Detection

class YOLODetector:
    """
    Clase para manejar la detección de objetos utilizando el modelo YOLO.
    Esta clase encapsula la lógica para cargar el modelo YOLO y realizar detecciones en imágenes.
    """
    
    COLORS = [
        (0, 255, 0),    # verde
        (0, 0, 255),    # rojo
        (255, 0, 0),    # azul
        (0, 255, 255),  # amarillo
        (255, 0, 255),  # magenta
        (255, 165, 0),  # naranja
    ]
    
    def __init__(self, model_path="yolov8n.pt", confidence=0.5):
        self.confidence = confidence
        self._model = YOLO(model_path)
        
    def detect(self, image):
        """
        Detecta objetos en la imagen utilizando el modelo YOLO.
        Args:
            image (np.ndarray): Frame en formato BGR (alto x ancho x 3).
        Returns:
            List[Detection]: Lista de objetos detectados con su clase, confianza y coordenadas.
        """
        results = self._model(image, conf=self.confidence, verbose=False)
        detections = []
        for result in results:
            for box in result.boxes:
                detections.append(Detection(
                    class_id=int(box.cls[0]),
                    class_name=self._model.names[int(box.cls[0])],
                    confidence=float(box.conf[0]),
                    x1=int(box.xyxy[0][0]),
                    y1=int(box.xyxy[0][1]),
                    x2=int(box.xyxy[0][2]),
                    y2=int(box.xyxy[0][3])
                ))
        return detections
    
    def annotate(self, frame, detections):
        """
        Anota la imagen con las detecciones realizadas.
        Args:
            frame (np.ndarray): Frame en formato BGR (alto x ancho x 3).
            detections (List[Detection]): Lista de objetos detectados con su clase, confianza y coordenadas.
        Returns:
            np.ndarray: Imagen anotada con las detecciones.
        """
        frame = frame.copy()
        for det in detections:
            color = self.COLORS[det.class_id % len(self.COLORS)]
            cv2.rectangle(frame, (det.x1, det.y1), (det.x2, det.y2), color, 2)
            cv2.putText(frame, f"{det.class_name} {det.confidence:.2f}", (det.x1, det.y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        return frame
    
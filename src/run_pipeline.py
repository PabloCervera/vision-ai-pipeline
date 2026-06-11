import cv2
import time
from detection.yolo_detector import YOLODetector
from capture.video_source import VideoSource, VideoSourceError
from detection.tracker import Tracker
from detection.event_detector import EventDetector
from alert_agent import agent

def run_pipeline(video_source=0, model_path="yolov8n.pt", confidence=0.5):
    """
    Función principal para ejecutar la pipeline de visión por computadora.
    Esta función abre la fuente de video, carga el modelo YOLO y procesa cada frame para detectar objetos.
    
    Args:
        video_source: Fuente de video (puede ser un índice de cámara o una ruta de archivo).
        model_path: Ruta al modelo YOLO a utilizar.
        confidence: Umbral de confianza para las detecciones.
    """
    detector = YOLODetector(model_path=model_path, confidence=confidence)
    tracker = Tracker(max_age=30)
    event_detector = EventDetector(static_threshold=30)
    
    last_analysis_time = 0
    analysis_interval = 10 
        
    with VideoSource(video_source) as source:
        while True:
            try:
                frame = source.read()   
                frame = cv2.resize(frame, (1708, 960))
                detections = detector.detect(frame)
                tracks = tracker.update(detections, frame)
                annotated_frame = tracker.annotate(frame, tracks)
                    
                cv2.imshow("Detections", annotated_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
                static_objects = event_detector.update(tracks)
                if static_objects:
                    now = time.time()
                    if now - last_analysis_time > analysis_interval:
                        result = agent.invoke({
                            "frame": frame,
                            "static_objects": static_objects,
                            "scene_description": "",
                            "risk_level": "",
                            "alert_message": ""
                        })
                        print(result["alert_message"])
                        last_analysis_time = now
                    
                
            except VideoSourceError as e:
                print(f"Error al procesar el frame: {e}")
                break
        cv2.destroyAllWindows()
            
if __name__ == "__main__":
    run_pipeline(video_source="test.mp4", confidence=0.3)
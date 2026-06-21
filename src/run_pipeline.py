import cv2
import time
import os
from detection.yolo_detector import YOLODetector
from capture.video_source import VideoSource, VideoSourceError
from detection.tracker import Tracker
from detection.event_detector import EventDetector
from alert_agent import agent
from datetime import datetime


def run_pipeline(video_source=0, events=None, latest_frame=None, model_path="yolov8n.pt", confidence=0.5):
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
    folder_path = "../data/event_frames/"
    
    os.makedirs(folder_path, exist_ok=True)
        
    with VideoSource(video_source) as source:
        while True:
            try:
                frame = source.read()   
                frame = cv2.resize(frame, (1708, 960))
                detections = detector.detect(frame)
                tracks = tracker.update(detections, frame)
                annotated_frame = tracker.annotate(frame, tracks)
                if latest_frame is not None:
                    latest_frame[0] = annotated_frame.copy()
                    
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

                        if events is not None:
                            if result["risk_level"] in ("medium", "high"):
                                for obj in static_objects:
                                    timestamp = datetime.now().isoformat()
                                    filename = f"{obj['track_id']}_{timestamp.replace(':', '-')}.jpg"
                                    cv2.imwrite(folder_path + filename, frame)
                                    events.add_event(track_id=obj["track_id"], alert=result["alert_message"], risk_level=result["risk_level"], timestamp=timestamp, frame_path=folder_path + filename)
                        last_analysis_time = now
                    
            except VideoSourceError as e:
                print(f"Error al procesar el frame: {e}")
                break
        cv2.destroyAllWindows()
            
if __name__ == "__main__":
    run_pipeline(video_source="test.mp4", confidence=0.3)
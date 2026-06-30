import cv2
import os
import time
from detection.yolo_detector import YOLODetector
from capture.video_source import VideoSource, VideoSourceError
from detection.tracker import Tracker
from detection.event_detector import EventDetector
from ai.alert_agent import agent
from config import FRAMES_DIR
from datetime import datetime


def run_pipeline(video_source=0, events=None, latest_frame=None, stop_event=None, video=None, progress=None, model_path="yolov8n.pt", confidence=0.5, show_window=False):
    """
    Función principal para ejecutar la pipeline de visión por computadora.
    Esta función abre la fuente de video, carga el modelo YOLO y procesa cada frame para detectar objetos.

    El bucle termina cuando se activa `stop_event` (p. ej. desde el endpoint /stop) o cuando
    se acaba el vídeo. La ventana de OpenCV es opcional y solo tiene sentido en modo standalone.

    Args:
        video_source: Fuente de video (puede ser un índice de cámara o una ruta de archivo).
        events: EventStore donde registrar los eventos detectados (opcional).
        latest_frame: Lista de un elemento donde publicar el último frame anotado (opcional).
        stop_event: threading.Event para detener el bucle desde fuera (opcional).
        video: Identificador del vídeo al que asociar los eventos. Si es None, se deriva de video_source.
        progress: dict compartido donde publicar el avance (claves processed/total/percent) (opcional).
        model_path: Ruta al modelo YOLO a utilizar.
        confidence: Umbral de confianza para las detecciones.
        show_window: Si es True, muestra una ventana de OpenCV con el vídeo anotado (pulsa 'q' para salir).
                     Por defecto False: pensado para ejecución bajo la API, donde los frames se sirven
                     vía /latest_frame y /stream y el control se hace con stop_event.
    """
    if video is None:
        video = os.path.basename(str(video_source)) if isinstance(video_source, str) else str(video_source)

    detector = YOLODetector(model_path=model_path, confidence=confidence)
    tracker = Tracker(max_age=30)
    event_detector = EventDetector(static_threshold=30)
    
    last_analysis_time = 0
    analysis_interval = 10

    with VideoSource(video_source) as source:
        total_frames = source.frame_count()
        processed_frames = 0
        if progress is not None:
            progress.update({"processed": 0, "total": total_frames, "percent": 0.0})

        while stop_event is None or not stop_event.is_set():
            try:
                frame = source.read()
                processed_frames += 1
                if progress is not None:
                    progress["processed"] = processed_frames
                    progress["percent"] = round(processed_frames / total_frames * 100, 1) if total_frames else 0.0
                frame = cv2.resize(frame, (1708, 960))
                detections = detector.detect(frame)
                tracks = tracker.update(detections, frame)
                annotated_frame = tracker.annotate(frame, tracks)
                if latest_frame is not None:
                    latest_frame[0] = annotated_frame.copy()

                if show_window:
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
                                    frame_path = str(FRAMES_DIR / filename)
                                    cv2.imwrite(frame_path, frame)
                                    events.add_event(track_id=obj["track_id"], alert=result["alert_message"], risk_level=result["risk_level"], timestamp=timestamp, frame_path=frame_path, video=video)
                        last_analysis_time = now
                    
            except VideoSourceError as e:
                print(f"Error al procesar el frame: {e}")
                if progress is not None and total_frames:
                    progress.update({"processed": total_frames, "percent": 100.0})
                break
        if show_window:
            cv2.destroyAllWindows()

if __name__ == "__main__":
    run_pipeline(video_source=0, confidence=0.3, show_window=True)
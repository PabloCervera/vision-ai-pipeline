import cv2
from detection.yolo_detector import YOLODetector
from capture.video_source import VideoSource, VideoSourceError

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
    
    with VideoSource(video_source) as source:
        while True:
            try:
                frame = source.read()   
                frame = cv2.resize(frame, (1708, 960))             
                detections = detector.detect(frame)
                frame = detector.annotate(frame, detections)
                    
                cv2.imshow("Detections", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
            except VideoSourceError as e:
                print(f"Error al procesar el frame: {e}")
                break
            
if __name__ == "__main__":
    run_pipeline(video_source="test.mp4", confidence=0.3)
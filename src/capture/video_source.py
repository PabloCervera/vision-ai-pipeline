"""
Módulo para manejar la fuente de video (cámara o archivo).
Este módulo define la clase VideoSource, que encapsula la lógica de abrir y cerrar la fuente de video.
También define la excepción VideoSourceError para manejar errores relacionados con la fuente de video.
"""

import cv2

class VideoSourceError(Exception):
    """Excepción personalizada para errores relacionados con la fuente de video."""
    pass

class VideoSource:
    """
    Clase para manejar la fuente de video (cámara o archivo).
    Esta clase encapsula la lógica de abrir y cerrar la fuente de video, y proporciona una interfaz sencilla para acceder a los frames.
    """
    def __init__(self, source=0):
        """
        Inicializa la fuente de video.
        """
        self.source = source
        self._cap = None  # aún no abrimos nada

    def open(self):
        """
        Abre la fuente de video.
        Si ya está abierta, la cierra primero.
        
        Returns:
            VideoSource: la propia instancia, para poder encadenar llamadas.

        Raises:
            VideoSourceError: si no se puede abrir la fuente.
        """
        
        self._cap = cv2.VideoCapture(self.source)
        if not self._cap.isOpened():
            raise VideoSourceError(f"No se pudo abrir: {self.source}")
        return self

    def close(self):
        """Libera los recursos de la fuente de vídeo."""
        if self._cap:
            self._cap.release()
            
    def read(self): 
        """
        Lee un frame de la fuente de video.
        
        Returns:
            Tuple[bool, np.ndarray]: Un booleano que indica si se leyó correctamente y el frame leído (en formato BGR).

        Raises:
            VideoSourceError: si la fuente no está abierta o no se pudo leer un frame.
        """
        if not self._cap or not self._cap.isOpened():
            raise VideoSourceError("La fuente de video no está abierta.")
        ret, frame = self._cap.read()
        if not ret:
            raise VideoSourceError("No se pudo leer un frame de la fuente.")
        return frame

    def __enter__(self):
        return self.open()

    def __exit__(self, *_):
        self.close()
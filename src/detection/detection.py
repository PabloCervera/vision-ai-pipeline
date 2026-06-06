"""
Módulo para manejar las detecciones de objetos.
Este módulo define la clase Detection, que representa una detección de objeto con su clase, confianza y coordenadas.
"""

from dataclasses import dataclass

@dataclass
class Detection:
    """
    Clase para representar una detección de objeto.
    Esta clase utiliza el decorador @dataclass para simplificar la definición de la clase y proporcionar métodos útiles como __init__ y __repr__ automáticamente.
    """
    class_id: int
    class_name: str
    confidence: float
    x1: int
    y1: int
    x2: int
    y2: int
    
    @property
    def bbox(self):
        """Devuelve las coordenadas del bounding box como una tupla."""
        return (self.x1, self.y1, self.x2, self.y2)
    
    @property
    def center(self):
        """Devuelve el centro del bounding box."""
        return ((self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2)
    
    @property
    def area(self):
        """Devuelve el área del bounding box."""
        return (self.x2 - self.x1) * (self.y2 - self.y1)
    
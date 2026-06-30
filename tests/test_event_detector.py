"""Tests de EventDetector: detección de objetos estáticos a partir del historial de tracks.

Se usa un stub mínimo de track (FakeTrack) que imita la interfaz que consume
EventDetector.update(): is_confirmed(), track_id y to_ltrb().
"""

from detection.event_detector import EventDetector


class FakeTrack:
    """Track de prueba con la interfaz mínima que usa EventDetector."""

    def __init__(self, track_id, ltrb, confirmed=True, det_class="person"):
        self.track_id = track_id
        self._ltrb = ltrb
        self._confirmed = confirmed
        self._det_class = det_class

    def is_confirmed(self):
        return self._confirmed

    def to_ltrb(self):
        return self._ltrb

    def get_det_class(self):
        return self._det_class


def test_objeto_estatico_se_detecta():
    detector = EventDetector(static_threshold=3, max_distance=10)
    quieto = FakeTrack("1", (0, 0, 10, 10))  # centro siempre en (5, 5)

    # Hasta acumular static_threshold frames no se evalúa
    assert detector.update([quieto]) == []
    assert detector.update([quieto]) == []

    estaticos = detector.update([quieto])
    assert len(estaticos) == 1
    assert estaticos[0]["track_id"] == "1"
    assert estaticos[0]["center"] == (5, 5)
    # Metadatos de grounding: clase del objeto y frames que lleva inmóvil
    assert estaticos[0]["class_name"] == "person"
    assert estaticos[0]["static_frames"] == 3  # = static_threshold en el primer disparo


def test_static_frames_se_incrementa():
    detector = EventDetector(static_threshold=3, max_distance=10)
    quieto = FakeTrack("1", (0, 0, 10, 10))

    detector.update([quieto])
    detector.update([quieto])
    assert detector.update([quieto])[0]["static_frames"] == 3  # primer disparo
    assert detector.update([quieto])[0]["static_frames"] == 4  # un frame más inmóvil


def test_objeto_en_movimiento_no_se_detecta():
    detector = EventDetector(static_threshold=3, max_distance=10)

    # El centro se desplaza muy por encima de max_distance entre frames
    detector.update([FakeTrack("1", (0, 0, 10, 10))])      # centro (5, 5)
    detector.update([FakeTrack("1", (50, 50, 60, 60))])    # centro (55, 55)
    estaticos = detector.update([FakeTrack("1", (100, 100, 110, 110))])  # centro (105, 105)

    assert estaticos == []


def test_historial_insuficiente_no_detecta():
    detector = EventDetector(static_threshold=3, max_distance=10)
    quieto = FakeTrack("1", (0, 0, 10, 10))

    assert detector.update([quieto]) == []
    assert detector.update([quieto]) == []  # solo 2 frames < static_threshold


def test_track_no_confirmado_se_ignora():
    detector = EventDetector(static_threshold=3, max_distance=10)
    no_confirmado = FakeTrack("1", (0, 0, 10, 10), confirmed=False)

    for _ in range(5):
        assert detector.update([no_confirmado]) == []

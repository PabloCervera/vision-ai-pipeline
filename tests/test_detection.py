"""Tests de la dataclass Detection: propiedades derivadas del bounding box."""

from detection.detection import Detection


def _detection():
    return Detection(class_id=0, class_name="person", confidence=0.9, x1=10, y1=20, x2=30, y2=60)


def test_bbox():
    assert _detection().bbox == (10, 20, 30, 60)


def test_center():
    # center = ((x1 + x2) // 2, (y1 + y2) // 2)
    assert _detection().center == (20, 40)


def test_area():
    # area = (x2 - x1) * (y2 - y1) = 20 * 40
    assert _detection().area == 800

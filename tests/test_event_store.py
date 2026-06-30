"""Tests de EventStore: persistencia, filtrado y borrado de eventos por vídeo.

Se usa una base de datos SQLite en memoria (:memory:) para no tocar disco.
"""

import pytest

from database.event_store import EventStore


@pytest.fixture
def store():
    return EventStore(db_path=":memory:")


def _add(store, track_id, video, risk="high"):
    store.add_event(
        track_id=track_id,
        alert=f"alerta {track_id}",
        risk_level=risk,
        timestamp=f"2026-06-30T10:0{track_id}:00",
        frame_path=f"/frames/{track_id}.jpg",
        video=video,
    )


def test_add_and_get_all(store):
    _add(store, "1", "A.mp4")
    events = store.get_all_events()
    assert len(events) == 1
    assert events[0]["track_id"] == "1"
    assert events[0]["video"] == "A.mp4"


def test_filter_by_video(store):
    _add(store, "1", "A.mp4")
    _add(store, "2", "B.mp4")
    _add(store, "3", "A.mp4")

    assert len(store.get_all_events()) == 3
    eventos_a = store.get_all_events(video="A.mp4")
    assert {e["track_id"] for e in eventos_a} == {"1", "3"}
    assert len(store.get_all_events(video="B.mp4")) == 1


def test_clear_by_video_preserva_el_resto(store):
    _add(store, "1", "A.mp4")
    _add(store, "2", "B.mp4")

    store.clear_events(video="A.mp4")

    restantes = store.get_all_events()
    assert len(restantes) == 1
    assert restantes[0]["video"] == "B.mp4"


def test_clear_all(store):
    _add(store, "1", "A.mp4")
    _add(store, "2", "B.mp4")

    store.clear_events()

    assert store.get_all_events() == []


def test_recent_respeta_el_limite(store):
    for i in range(1, 6):
        _add(store, str(i), "A.mp4")

    recientes = store.get_recent_events(limit=3)
    assert len(recientes) == 3
    # ORDER BY id DESC -> los últimos insertados primero
    assert [e["track_id"] for e in recientes] == ["5", "4", "3"]


def test_recent_filtra_por_video(store):
    _add(store, "1", "A.mp4")
    _add(store, "2", "B.mp4")
    _add(store, "3", "A.mp4")

    recientes_a = store.get_recent_events(limit=10, video="A.mp4")
    assert {e["track_id"] for e in recientes_a} == {"1", "3"}

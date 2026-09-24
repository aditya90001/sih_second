import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.geospatial import haversine_distance
from app.main import app
from app.rag.engine import HybridRAGEngine


def test_haversine_same_point_is_zero():
    assert haversine_distance(27.35, 95.32, 27.35, 95.32) == 0


def test_rag_filters_metadata():
    engine = HybridRAGEngine()
    engine.add_documents([
        {
            "text": "mud loss at 2800 m",
            "metadata": {"event_type": "MUD_LOSS"},
        },
        {
            "text": "stuck pipe at 3100 m",
            "metadata": {"event_type": "STUCK_PIPE"},
        },
    ])

    results = engine.hybrid_search("mud loss", {"event_type": "MUD_LOSS"})

    assert len(results) == 1
    assert results[0]["metadata"]["event_type"] == "MUD_LOSS"


def test_health_endpoint():
    response = TestClient(app).get("/api/v1/health")
    assert response.status_code == 200

import pytest
from app.core.geospatial import haversine_distance

def test_haversine_same_point():
    assert haversine_distance(27.35, 95.32, 27.35, 95.32) == 0.0

def test_haversine_known_distance():
    # Roughly 111 km per degree latitude
    dist = haversine_distance(0.0, 0.0, 1.0, 0.0)
    assert 110.0 < dist < 112.0
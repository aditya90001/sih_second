import pytest
from app.extraction.event_extractor import EventExtractor

def test_event_extractor_mud_loss():
    extractor = EventExtractor()
    sample_text = "At 2875 m, severe mud loss was encountered while drilling Formation B. LCM treatment was performed."
    
    extracted = extractor.extract_structured_event(sample_text)
    
    assert extracted["depth"] == 2875.0
    assert extracted["formation"] == "Formation B"
    assert extracted["event_type"] == "MUD_LOSS"
    assert extracted["severity"] == "HIGH"
    assert "LCM treatment" in extracted["mitigation"]
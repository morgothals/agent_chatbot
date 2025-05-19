import pytest
from validator import validate_intent, validate_entities, ValidationError

def test_validate_intent_ok():
    validate_intent("order_status")

def test_validate_intent_unknown():
    with pytest.raises(ValidationError):
        validate_intent("nonsuch_intent")

def test_validate_entities_ok():
    validate_entities("order_status", {"order_id": "A1003"})

def test_validate_entities_missing():
    with pytest.raises(ValidationError):
        validate_entities("order_status", {})

def test_validate_entities_pattern():
    with pytest.raises(ValidationError):
        validate_entities("order_status", {"order_id": "XYZ"})

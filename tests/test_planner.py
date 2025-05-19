import pytest
from planner import parse_user_input, plan

def test_parse_simple_intent(monkeypatch):
    # mock Gemini válasz
    fake = '{"intent":"order_status","entities":{"order_id":"A1003"}}'
    monkeypatch.setattr("planner.call_gemini_api", lambda **kw: fake)
    res = parse_user_input("Hol tart az A1003-as rendelésem?")
    assert res["intent"] == "order_status"
    assert res["entities"]["order_id"] == "A1003"

def test_plan_validation_error(monkeypatch):
    # parse_user_input valid de validator hibázik
    monkeypatch.setattr("planner.parse_user_input", lambda t: {"intent":"order_status","entities":{}})
    res = plan("Hol tart az A1003-as rendelésem?")
    assert "error" in res

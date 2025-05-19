import pytest
from planner import parse_user_input, plan

def test_parse_simple_intent(monkeypatch):
    fake = '{"intent":"order_status","entities":{"order_id":"A1003"}}'
    monkeypatch.setattr("planner.call_gemini_api", lambda **kw: fake)
    res = parse_user_input("Hol tart az A1003-as rendelésem?")
    assert res["intent"] == "order_status"
    assert res["entities"]["order_id"] == "A1003"

def test_parse_shipping_time(monkeypatch):
    fake = '{"intent":"shipping_time","entities":{"order_id":"A1005"}}'
    monkeypatch.setattr("planner.call_gemini_api", lambda **kw: fake)
    res = parse_user_input("Mikorra várható az A1005 szállítása?")
    assert res["intent"] == "shipping_time"
    assert res["entities"]["order_id"] == "A1005"

def test_parse_order_history(monkeypatch):
    fake = '{"intent":"order_history","entities":{}}'
    monkeypatch.setattr("planner.call_gemini_api", lambda **kw: fake)
    res = parse_user_input("Mik a rendeléseim állapotai?")
    assert res["intent"] == "order_history"
    assert res["entities"] == {}

def test_parse_cancel_order(monkeypatch):
    fake = '{"intent":"cancel_order","entities":{"order_id":"A1010"}}'
    monkeypatch.setattr("planner.call_gemini_api", lambda **kw: fake)
    res = parse_user_input("Törölném az A1010-es rendelést.")
    assert res["intent"] == "cancel_order"
    assert res["entities"]["order_id"] == "A1010"

def test_parse_product_info(monkeypatch):
    fake = '{"intent":"product_info","entities":{"product_id":"P200"}}'
    monkeypatch.setattr("planner.call_gemini_api", lambda **kw: fake)
    res = parse_user_input("Mondd el, mi az a P200 termék.")
    assert res["intent"] == "product_info"
    assert res["entities"]["product_id"] == "P200"

def test_plan_validation_error(monkeypatch):
    monkeypatch.setattr("planner.parse_user_input", lambda t: {"intent":"order_status","entities":{}})
    res = plan("Hol tart az A1003-as rendelésem?")
    assert "error" in res

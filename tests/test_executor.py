def test_invoke_order_status_valid(monkeypatch):
    from executor import invoke_order_status
    # monkeypatch nem kell, mert get_order_info tényleg olvassa az orders.json-t
    out = invoke_order_status("A1003")
    assert out["order_id"] == "A1003"
    assert "status" in out

def test_invoke_order_status_invalid():
    from executor import invoke_order_status
    out = invoke_order_status("XXXX")
    assert "error" in out
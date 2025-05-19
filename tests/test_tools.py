import pytest
from tools import get_order_info, load_memory, save_memory

def test_get_order_ok():
    info = get_order_info({"order_id":"A1003"})
    assert info["order_id"] == "A1003"
    assert "status" in info

def test_get_order_not_found():
    info = get_order_info({"order_id":"ZZZZ"})
    assert "error" in info

def test_memory_roundtrip(tmp_path):
    # ideiglenes memory.json
    from pathlib import Path
    p = tmp_path/"memory.json"
    Path("memory.json").rename(p) if Path("memory.json").exists() else None
    # üres memória
    mem = load_memory()
    assert isinstance(mem, dict) and "history" in mem
    mem["history"].append("x")
    save_memory(mem)
    assert load_memory()["history"][-1] == "x"
    p.rename("memory.json")

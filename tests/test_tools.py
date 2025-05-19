import pytest
from tools import get_order_info, load_memory, save_memory
import shutil
from pathlib import Path

def test_get_order_ok():
    info = get_order_info({"order_id": "A1003"})
    assert info["order_id"] == "A1003"
    assert "status" in info

def test_get_order_not_found():
    info = get_order_info({"order_id": "ZZZZ"})
    assert "error" in info

def test_memory_roundtrip(tmp_path):
    # Eredeti memory.json biztonsági mentése
    original = Path("memory.json")
    backup = tmp_path / "memory_orig.json"
    if original.exists():
        shutil.copy(original, backup)

    # Load–modify–save kör
    mem = load_memory()
    assert isinstance(mem, dict) and "history" in mem
    mem["history"].append("x")
    save_memory(mem)
    assert load_memory()["history"][-1] == "x"

    # Backup visszaállítása eredetire
    if backup.exists():
        shutil.copy(backup, original)

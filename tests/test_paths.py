"""Tests for path utilities."""

import sys
from pathlib import Path

from wifi_connector.utils import paths


def test_get_paths_dev_mode(monkeypatch):
    monkeypatch.delattr(sys, "frozen", raising=False)

    base_path = Path(paths.__file__).parent.parent.parent

    assert paths.get_vault_path() == base_path / "vault"
    assert paths.get_favorites_path() == base_path / "vault" / "fav.json"


def test_get_paths_frozen_mode(monkeypatch, tmp_path):
    exe_path = tmp_path / "app.exe"
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(exe_path))

    assert paths.get_vault_path() == exe_path.parent / "vault"
    assert paths.get_favorites_path() == exe_path.parent / "vault" / "fav.json"

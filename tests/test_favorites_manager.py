"""Tests for FavoritesManager."""

import json
from unittest.mock import MagicMock

import pytest

from wifi_connector.data.credentials_manager import (
    CenterCredentials,
    CredentialsManager,
)
from wifi_connector.data.favorites_manager import FavoritesManager


@pytest.fixture
def temp_favorites_path(tmp_path):
    return tmp_path / "fav.json"


@pytest.fixture
def centers():
    return [
        CenterCredentials("08000001", "Centre 1", "user1", "pass1"),
        CenterCredentials("08000002", "Centre 2", "user2", "pass2"),
        CenterCredentials("08000003", "Centre 3", "user3", "pass3"),
    ]


@pytest.fixture
def mock_credentials_manager(centers):
    manager = MagicMock(spec=CredentialsManager)
    manager.get_all_centers.return_value = centers

    center_map = {c.center_code: c for c in centers}

    def get_center_by_code(code):
        return center_map.get(code)

    manager.get_center_by_code.side_effect = get_center_by_code
    return manager


@pytest.fixture
def favorites_manager(temp_favorites_path, mock_credentials_manager):
    return FavoritesManager(temp_favorites_path, mock_credentials_manager)


def test_load_favorites_migrates_legacy_format(favorites_manager, temp_favorites_path):
    legacy_data = [
        {
            "center_code": "08000001",
            "center_name": "Centre 1",
            "username": "user1",
            "password": "pass1",
        },
        {
            "center_code": "08000002",
            "center_name": "Centre 2",
            "username": "user2",
            "password": "pass2",
        },
    ]
    temp_favorites_path.write_text(json.dumps(legacy_data, indent=2), encoding="utf-8")

    result = favorites_manager.load_favorites()

    assert result is True
    assert favorites_manager.is_favorite("08000001")
    assert favorites_manager.is_favorite("08000002")

    stored = json.loads(temp_favorites_path.read_text(encoding="utf-8"))
    assert stored == ["08000001", "08000002"]


def test_load_favorites_filters_obsolete_codes(favorites_manager, temp_favorites_path):
    temp_favorites_path.write_text(
        json.dumps(["08000001", "99999999"], indent=2), encoding="utf-8"
    )

    result = favorites_manager.load_favorites()

    assert result is True
    assert favorites_manager.is_favorite("08000001")
    assert not favorites_manager.is_favorite("99999999")

    stored = json.loads(temp_favorites_path.read_text(encoding="utf-8"))
    assert stored == ["08000001"]


def test_add_favorite_persists_only_codes(
    favorites_manager, temp_favorites_path, centers
):
    favorites_manager.add_favorite(centers[0])

    stored = json.loads(temp_favorites_path.read_text(encoding="utf-8"))

    assert stored == ["08000001"]


def test_get_favorites_resolves_codes(favorites_manager, temp_favorites_path):
    temp_favorites_path.write_text(
        json.dumps(["08000001", "08000003"], indent=2), encoding="utf-8"
    )

    favorites_manager.load_favorites()
    favorites = favorites_manager.get_favorites()

    assert [c.center_code for c in favorites] == ["08000001", "08000003"]


def test_load_favorites_invalid_format_returns_false(
    favorites_manager, temp_favorites_path
):
    temp_favorites_path.write_text(
        json.dumps({"center": "08000001"}, indent=2), encoding="utf-8"
    )

    result = favorites_manager.load_favorites()

    assert result is False


def test_add_favorite_skips_invalid_center(favorites_manager):
    invalid_center = CenterCredentials("99999999", "Missing", "user", "pass")

    favorites_manager.add_favorite(invalid_center)

    assert favorites_manager.get_favorites() == []


def test_add_favorite_skips_duplicate(favorites_manager, temp_favorites_path, centers):
    favorites_manager.add_favorite(centers[0])
    favorites_manager.add_favorite(centers[0])

    stored = json.loads(temp_favorites_path.read_text(encoding="utf-8"))

    assert stored == ["08000001"]


def test_remove_favorite_noop_when_missing(favorites_manager):
    favorites_manager.remove_favorite("08000001")

    assert favorites_manager.get_favorites() == []

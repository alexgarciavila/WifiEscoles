"""Tests unitarios para la clase Config."""

import json
import pytest
from pathlib import Path
from wifi_connector.core.config import Config


class TestConfigDefault:
    """Tests para el método Config.default()."""
    
    def test_default_has_expected_default_values(self):
        """Verifica que default() crea Config con los valores por defecto esperados."""
        config = Config.default()
        
        assert config.pause_duration == 0.5
        assert config.credential_dialog_wait_time == 1
        assert config.debug_mode is False


class TestConfigFromFile:
    """Tests para el método Config.from_file()."""
    
    def test_from_file_loads_valid_json(self, tmp_path):
        """Verifica la carga de configuración desde archivo JSON válido."""
        config_file = tmp_path / "config.json"
        config_data = {
            "pause_duration": 1.0,
            "debug_mode": True
        }
        config_file.write_text(json.dumps(config_data), encoding='utf-8')
        
        config = Config.from_file(str(config_file))
        
        assert config.pause_duration == 1.0
        assert config.debug_mode is True
    
    def test_from_file_raises_error_for_missing_file(self):
        """Verifica que from_file lanza FileNotFoundError para archivo inexistente."""
        with pytest.raises(FileNotFoundError):
            Config.from_file("nonexistent_config.json")
    
    def test_from_file_raises_error_for_unsupported_format(self, tmp_path):
        """Verifica que from_file lanza ValueError para archivos no JSON."""
        config_file = tmp_path / "config.txt"
        config_file.write_text("some text", encoding='utf-8')
        
        with pytest.raises(ValueError):
            Config.from_file(str(config_file))
    
    def test_from_file_uses_defaults_for_optional_fields(self, tmp_path):
        """Verifica que from_file usa valores por defecto para campos no especificados."""
        config_file = tmp_path / "config.json"
        config_data = {
            "debug_mode": True
        }
        config_file.write_text(json.dumps(config_data), encoding='utf-8')
        
        config = Config.from_file(str(config_file))
        
        assert config.debug_mode is True
        assert config.pause_duration == 0.5


class TestConfigValidation:
    """Tests para la validación de Config."""
    
    def test_validation_rejects_negative_pause_duration(self):
        """Verifica que pause_duration negativo lanza ValueError."""
        with pytest.raises(ValueError):
            Config(pause_duration=-1.0)
    
    def test_validation_rejects_negative_credential_dialog_wait_time(self):
        """Verifica que credential_dialog_wait_time negativo lanza ValueError."""
        with pytest.raises(ValueError):
            Config(credential_dialog_wait_time=-1)
    
    def test_validation_accepts_valid_config(self):
        """Verifica que configuración válida pasa la validación."""
        config = Config(
            pause_duration=0.5,
            credential_dialog_wait_time=2,
            debug_mode=False
        )
        assert config.pause_duration == 0.5

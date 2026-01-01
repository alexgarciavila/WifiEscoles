"""Tests unitarios para el módulo de tema oscuro.

Este módulo prueba la configuración del tema oscuro y sus constantes.
"""

import pytest
from unittest.mock import patch, MagicMock

from wifi_connector.utils.theme import (
    APPEARANCE_MODE,
    COLOR_THEME,
    THEME_SETUP_MAX_TIME_MS,
    setup_dark_theme
)


class TestThemeConstants:
    """Tests para las constantes del tema."""

    def test_appearance_mode_is_dark(self):
        """Verifica que el modo de apariencia sea 'dark'."""
        assert APPEARANCE_MODE == "dark"

    def test_color_theme_is_blue(self):
        """Verifica que el tema de colores sea 'blue'."""
        assert COLOR_THEME == "blue"

    def test_theme_setup_max_time_is_100ms(self):
        """Verifica que el tiempo máximo de configuración sea 100ms."""
        assert THEME_SETUP_MAX_TIME_MS == 100
        assert isinstance(THEME_SETUP_MAX_TIME_MS, int)


class TestSetupDarkTheme:
    """Tests para la función setup_dark_theme()."""

    @patch('wifi_connector.utils.theme.ctk')
    @patch('wifi_connector.utils.theme.Logger')
    def test_setup_calls_customtkinter_api(self, mock_logger, mock_ctk):
        """Verifica que setup_dark_theme() llama a la API de customTkinter."""
        setup_dark_theme()
        
        mock_ctk.set_appearance_mode.assert_called_once_with("dark")
        mock_ctk.set_default_color_theme.assert_called_once_with("blue")

    @patch('wifi_connector.utils.theme.ctk')
    @patch('wifi_connector.utils.theme.Logger')
    def test_setup_logs_success(self, mock_logger, mock_ctk):
        """Verifica que setup_dark_theme() registra mensaje de éxito."""
        setup_dark_theme()
        
        from wifi_connector.utils import translations as t
        mock_logger.info.assert_called_once_with(t.THEME_LOG_CONFIGURED)

    @patch('wifi_connector.utils.theme.ctk')
    @patch('wifi_connector.utils.theme.Logger')
    def test_setup_handles_import_error(self, mock_logger, mock_ctk):
        """Verifica que ImportError se propaga correctamente."""
        mock_ctk.set_appearance_mode.side_effect = ImportError("customtkinter not found")
        
        with pytest.raises(ImportError, match="customtkinter not found"):
            setup_dark_theme()
        
        mock_logger.critical.assert_called_once()
        assert "customTkinter no està instal\u00b7lat" in mock_logger.critical.call_args[0][0]

    @patch('wifi_connector.utils.theme.ctk')
    @patch('wifi_connector.utils.theme.Logger')
    def test_setup_handles_attribute_error(self, mock_logger, mock_ctk):
        """Verifica que AttributeError se propaga correctamente."""
        mock_ctk.set_appearance_mode.side_effect = AttributeError("API changed")
        
        with pytest.raises(AttributeError, match="API changed"):
            setup_dark_theme()
        
        mock_logger.error.assert_called_once()
        assert "Error en configurar el tema fosc" in mock_logger.error.call_args[0][0]

    @patch('wifi_connector.utils.theme.ctk')
    @patch('wifi_connector.utils.theme.Logger')
    def test_setup_handles_runtime_error(self, mock_logger, mock_ctk):
        """Verifica que RuntimeError se propaga correctamente."""
        mock_ctk.set_default_color_theme.side_effect = RuntimeError("Internal error")
        
        with pytest.raises(RuntimeError, match="Internal error"):
            setup_dark_theme()
        
        mock_logger.error.assert_called_once()
        assert "Error en configurar el tema fosc" in mock_logger.error.call_args[0][0]

    @patch('wifi_connector.utils.theme.ctk')
    @patch('wifi_connector.utils.theme.Logger')
    def test_setup_completes_without_exception(self, mock_logger, mock_ctk):
        """Verifica que setup_dark_theme() se completa sin excepciones en caso exitoso."""
        # No debe lanzar excepciones
        try:
            setup_dark_theme()
        except Exception as e:
            pytest.fail(f"setup_dark_theme() lanzó excepción inesperada: {e}")

"""Tests de integración para verificar cobertura del tema oscuro en toda la GUI.

Este módulo verifica que todas las ventanas y componentes GUI aplican
el tema oscuro correctamente.
"""

import pytest
from unittest.mock import patch, MagicMock

from wifi_connector.utils.theme import setup_dark_theme


class TestThemeCoverage:
    """Tests de integración para verificar cobertura del tema en todas las ventanas."""

    @patch('wifi_connector.utils.theme.ctk')
    def test_theme_setup_before_gui_import(self, mock_ctk):
        """Verifica que el tema se puede configurar antes de importar GUI."""
        # Setup tema
        setup_dark_theme()
        
        # Verificar que API fue llamada
        mock_ctk.set_appearance_mode.assert_called_once_with("dark")
        mock_ctk.set_default_color_theme.assert_called_once_with("blue")
        
        # Ahora importar GUI debería ser seguro
        try:
            from wifi_connector.gui.main_window import MainWindow
            from wifi_connector.gui.about import AboutWindow
        except Exception as e:
            pytest.fail(f"Fallo al importar GUI después de setup_dark_theme(): {e}")

    @patch('wifi_connector.utils.theme.ctk')
    def test_main_window_uses_customtkinter(self, mock_ctk):
        """Verifica que MainWindow usa widgets customTkinter."""
        setup_dark_theme()
        
        from wifi_connector.gui import main_window
        
        # Verificar que el módulo usa customtkinter import
        import inspect
        source = inspect.getsource(main_window)
        
        # Verificar que usa customtkinter (buscar en todo el módulo, no solo en la clase)
        assert 'import customtkinter' in source or 'from customtkinter' in source
        
        # Verificar que NO usa tkinter legacy directamente en lugares críticos
        # Note: El alias 'ctk' es customtkinter, no legacy tkinter
        assert 'import tkinter as tk' not in source.split('import customtkinter')[0]

    @patch('wifi_connector.utils.theme.ctk')
    def test_about_window_uses_customtkinter(self, mock_ctk):
        """Verifica que AboutWindow usa widgets customTkinter."""
        setup_dark_theme()
        
        from wifi_connector.gui.about import AboutWindow
        
        # AboutWindow debe heredar de CTkToplevel
        import inspect
        source = inspect.getsource(AboutWindow)
        
        # Verificar que usa customtkinter
        assert 'customtkinter' in source or 'ctk' in source
        assert 'CTkToplevel' in source or 'ctk.CTkToplevel' in source

    @patch('wifi_connector.utils.theme.ctk')
    def test_no_tkinter_legacy_widgets_in_gui(self, mock_ctk):
        """Verifica que no hay widgets tkinter legacy en módulos GUI."""
        setup_dark_theme()
        
        import inspect
        from wifi_connector.gui import main_window, about
        
        # Obtener código fuente de módulos GUI
        main_source = inspect.getsource(main_window)
        about_source = inspect.getsource(about)
        
        # Verificar que NO usan tkinter legacy (tk.Button, tk.Label, etc.)
        legacy_widgets = ['tk.Button', 'tk.Label', 'tk.Entry', 'tk.Frame', 'tk.Text']
        
        for widget in legacy_widgets:
            assert widget not in main_source, f"MainWindow usa widget legacy: {widget}"
            assert widget not in about_source, f"AboutWindow usa widget legacy: {widget}"

    @patch('wifi_connector.utils.theme.ctk')
    @patch('wifi_connector.utils.theme.Logger')
    def test_theme_setup_idempotent(self, mock_logger, mock_ctk):
        """Verifica que llamar setup_dark_theme() múltiples veces es seguro."""
        # Primera llamada
        setup_dark_theme()
        
        # Segunda llamada (debe ser idempotente)
        setup_dark_theme()
        
        # Verificar que API fue llamada dos veces pero sin errores
        assert mock_ctk.set_appearance_mode.call_count == 2
        assert mock_ctk.set_default_color_theme.call_count == 2
        assert mock_logger.info.call_count == 2

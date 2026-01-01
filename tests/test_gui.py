"""Unit tests for GUI components."""

import pytest
from unittest.mock import patch, MagicMock, call
import threading

from wifi_connector.gui.main_window import MainWindow
from wifi_connector.data.credentials_manager import CenterCredentials
from wifi_connector.core.profile_connector import ProfileConnector


@pytest.fixture
def mock_credentials_manager():
    """Provide a mock CredentialsManager."""
    mock = MagicMock()
    mock.load_credentials.return_value = True
    mock.get_all_centers.return_value = [
        CenterCredentials(
            center_code="08012345",
            center_name="Institut Example",
            username="user1@testgencat.cat",
            password="pass123"
        ),
        CenterCredentials(
            center_code="08023456",
            center_name="Escola Test",
            username="user2@testgencat.cat",
            password="pass456"
        )
    ]
    mock.search_centers.return_value = mock.get_all_centers.return_value
    return mock


@pytest.fixture
def mock_wifi_connector():
    """Provide a mock ProfileConnector."""
    mock = MagicMock()
    mock.connect.return_value = True
    mock.disconnect.return_value = True
    return mock


@pytest.fixture
def mock_ctk_modules():
    """Provide comprehensive mocks for all customtkinter components."""
    with patch('wifi_connector.gui.main_window.ctk.CTk') as mock_ctk, \
         patch('wifi_connector.gui.main_window.ctk.CTkFrame') as mock_frame, \
         patch('wifi_connector.gui.main_window.ctk.CTkLabel') as mock_label, \
         patch('wifi_connector.gui.main_window.ctk.CTkEntry') as mock_entry, \
         patch('wifi_connector.gui.main_window.ctk.CTkButton') as mock_button, \
         patch('wifi_connector.gui.main_window.ctk.CTkScrollableFrame') as mock_scroll, \
         patch('wifi_connector.gui.main_window.ctk.CTkFont') as mock_font, \
         patch('wifi_connector.gui.main_window.ctk.set_appearance_mode') as mock_appearance, \
         patch('wifi_connector.gui.main_window.ctk.set_default_color_theme') as mock_theme:
        
        # Configure mock window
        mock_window = MagicMock()
        mock_window.after = MagicMock(side_effect=lambda delay, func: func())
        mock_ctk.return_value = mock_window
        
        # Configure other mocks to return MagicMock instances
        mock_frame.return_value = MagicMock()
        mock_label.return_value = MagicMock()
        mock_entry.return_value = MagicMock()
        mock_button.return_value = MagicMock()
        mock_scroll.return_value = MagicMock()
        mock_font.return_value = MagicMock()
        
        yield {
            'ctk': mock_ctk,
            'frame': mock_frame,
            'label': mock_label,
            'entry': mock_entry,
            'button': mock_button,
            'scroll': mock_scroll,
            'font': mock_font,
            'window': mock_window
        }


class TestMainWindowInit:
    """Tests for MainWindow initialization."""
    
    @patch('wifi_connector.gui.main_window.CredentialsManager')
    def test_initializes_window_with_correct_properties(
        self,
        mock_creds_manager_class,
        mock_ctk_modules
    ):
        """Test that window is initialized with correct properties."""
        mock_creds_manager = MagicMock()
        mock_creds_manager.load_credentials.return_value = True
        mock_creds_manager.get_all_centers.return_value = []
        mock_creds_manager_class.return_value = mock_creds_manager
        
        main_window = MainWindow()
        
        mock_ctk_modules['window'].title.assert_called_once_with("Wifi de Centres Educatius de Catalunya")
        mock_ctk_modules['window'].geometry.assert_called_once_with("700x600")
        assert main_window.window == mock_ctk_modules['window']
    
    @patch('wifi_connector.gui.main_window.CredentialsManager')
    def test_initializes_credentials_manager(
        self,
        mock_creds_manager_class,
        mock_ctk_modules
    ):
        """Test that CredentialsManager is initialized."""
        mock_creds_manager = MagicMock()
        mock_creds_manager.load_credentials.return_value = True
        mock_creds_manager.get_all_centers.return_value = []
        mock_creds_manager_class.return_value = mock_creds_manager
        
        main_window = MainWindow()
        
        mock_creds_manager_class.assert_called_once()
        mock_creds_manager.load_credentials.assert_called_once()
    
    @patch('wifi_connector.gui.main_window.CredentialsManager')
    def test_loads_credentials_on_init(
        self,
        mock_creds_manager_class,
        mock_ctk_modules,
        mock_credentials_manager
    ):
        """Test that credentials are loaded on initialization."""
        mock_creds_manager_class.return_value = mock_credentials_manager
        
        main_window = MainWindow()
        
        mock_credentials_manager.load_credentials.assert_called_once()
        mock_credentials_manager.get_all_centers.assert_called()
    
    @patch('wifi_connector.gui.main_window.CredentialsManager')
    def test_handles_credentials_load_error(
        self,
        mock_creds_manager_class,
        mock_ctk_modules
    ):
        """Test that credentials load errors are handled gracefully."""
        mock_creds_manager = MagicMock()
        mock_creds_manager.load_credentials.side_effect = Exception("Load error")
        mock_creds_manager_class.return_value = mock_creds_manager
        
        # Should not raise exception
        main_window = MainWindow()
        
        assert main_window is not None


class TestUpdateStatus:
    """Tests for update_status() method."""
    
    @patch('wifi_connector.gui.main_window.CredentialsManager')
    def test_updates_status_with_success_color(
        self,
        mock_creds_manager_class,
        mock_ctk_modules
    ):
        """Test that success status uses green color."""
        mock_creds_manager = MagicMock()
        mock_creds_manager.load_credentials.return_value = True
        mock_creds_manager.get_all_centers.return_value = []
        mock_creds_manager_class.return_value = mock_creds_manager
        
        main_window = MainWindow()
        main_window.status_label = MagicMock()
        
        main_window.update_status("Success message", "success")
        
        main_window.status_label.configure.assert_called_once_with(
            text="Success message",
            text_color="#2ecc71"
        )
    
    @patch('wifi_connector.gui.main_window.CredentialsManager')
    def test_updates_status_with_error_color(
        self,
        mock_creds_manager_class,
        mock_ctk_modules
    ):
        """Test that error status uses red color."""
        mock_creds_manager = MagicMock()
        mock_creds_manager.load_credentials.return_value = True
        mock_creds_manager.get_all_centers.return_value = []
        mock_creds_manager_class.return_value = mock_creds_manager
        
        main_window = MainWindow()
        main_window.status_label = MagicMock()
        
        main_window.update_status("Error message", "error")
        
        main_window.status_label.configure.assert_called_once_with(
            text="Error message",
            text_color="#e74c3c"
        )
    
    @patch('wifi_connector.gui.main_window.CredentialsManager')
    def test_updates_status_with_info_color(
        self,
        mock_creds_manager_class,
        mock_ctk_modules
    ):
        """Test that info status uses blue color."""
        mock_creds_manager = MagicMock()
        mock_creds_manager.load_credentials.return_value = True
        mock_creds_manager.get_all_centers.return_value = []
        mock_creds_manager_class.return_value = mock_creds_manager
        
        main_window = MainWindow()
        main_window.status_label = MagicMock()
        
        main_window.update_status("Info message", "info")
        
        main_window.status_label.configure.assert_called_once_with(
            text="Info message",
            text_color="#3498db"
        )


class TestSearchFiltering:
    """Tests for search and filter functionality."""
    
    @patch('wifi_connector.gui.main_window.CredentialsManager')
    def test_filter_centers_with_query(
        self,
        mock_creds_manager_class,
        mock_ctk_modules,
        mock_credentials_manager
    ):
        """Test that centers are filtered based on query."""
        mock_creds_manager_class.return_value = mock_credentials_manager
        filtered_centers = [mock_credentials_manager.get_all_centers.return_value[0]]
        mock_credentials_manager.search_centers.return_value = filtered_centers
        
        main_window = MainWindow()
        main_window.center_count_label = MagicMock()
        
        main_window._filter_centers("Institut")
        
        mock_credentials_manager.search_centers.assert_called_once_with("Institut")
    
    @patch('wifi_connector.gui.main_window.CredentialsManager')
    def test_filter_centers_with_empty_query_shows_all(
        self,
        mock_creds_manager_class,
        mock_ctk_modules,
        mock_credentials_manager
    ):
        """Test that empty query shows all centers."""
        mock_creds_manager_class.return_value = mock_credentials_manager
        
        main_window = MainWindow()
        main_window.center_count_label = MagicMock()
        
        main_window._filter_centers("")
        
        # Should not call search_centers for empty query
        assert main_window.all_centers == mock_credentials_manager.get_all_centers.return_value
    
    @patch('wifi_connector.gui.main_window.CredentialsManager')
    def test_filter_centers_updates_count_label(
        self,
        mock_creds_manager_class,
        mock_ctk_modules,
        mock_credentials_manager
    ):
        """Test that count label is updated after filtering."""
        mock_creds_manager_class.return_value = mock_credentials_manager
        filtered_centers = [mock_credentials_manager.get_all_centers.return_value[0]]
        mock_credentials_manager.search_centers.return_value = filtered_centers
        
        main_window = MainWindow()
        main_window.center_count_label = MagicMock()
        
        main_window._filter_centers("Institut")
        
        main_window.center_count_label.configure.assert_called()
    
    @patch('wifi_connector.gui.main_window.CredentialsManager')
    def test_filter_centers_shows_no_results_message(
        self,
        mock_creds_manager_class,
        mock_ctk_modules,
        mock_credentials_manager
    ):
        """Test that 'No results found' is shown when filter returns empty."""
        mock_creds_manager_class.return_value = mock_credentials_manager
        mock_credentials_manager.search_centers.return_value = []
        
        main_window = MainWindow()
        main_window.center_count_label = MagicMock()
        
        main_window._filter_centers("NonExistent")
        
        main_window.center_count_label.configure.assert_called_with(
            text="No s'han trobat resultats",
            text_color="#e74c3c"
        )


class TestCenterSelection:
    """Tests for center selection functionality."""
    
    @patch('wifi_connector.gui.main_window.CredentialsManager')
    def test_on_center_selected_sets_selected_center(
        self,
        mock_creds_manager_class,
        mock_ctk_modules,
        mock_credentials_manager
    ):
        """Test that selected center is set when center is selected."""
        mock_creds_manager_class.return_value = mock_credentials_manager
        
        main_window = MainWindow()
        main_window.connect_button = MagicMock()
        # Clear center_buttons to avoid isinstance issue
        main_window.center_buttons = []
        
        center = mock_credentials_manager.get_all_centers.return_value[0]
        main_window._on_center_selected(center)
        
        assert main_window.selected_center == center
    
    @patch('wifi_connector.gui.main_window.CredentialsManager')
    def test_on_center_selected_updates_status(
        self,
        mock_creds_manager_class,
        mock_ctk_modules,
        mock_credentials_manager
    ):
        """Test that status is updated when center is selected."""
        mock_creds_manager_class.return_value = mock_credentials_manager
        
        main_window = MainWindow()
        main_window.status_label = MagicMock()
        main_window.center_buttons = []
        
        center = mock_credentials_manager.get_all_centers.return_value[0]
        main_window._on_center_selected(center)
        
        main_window.status_label.configure.assert_called()


class TestConnectionActions:
    """Tests for connection button actions."""
    
    @patch('wifi_connector.gui.main_window.CredentialsManager')
    def test_on_connect_profile_clicked_without_selection_shows_error(
        self,
        mock_creds_manager_class,
        mock_ctk_modules,
        mock_credentials_manager
    ):
        """Test that error is shown when Connect is clicked without selection."""
        mock_creds_manager_class.return_value = mock_credentials_manager
        
        main_window = MainWindow()
        main_window.status_label = MagicMock()
        main_window.selected_center = None
        
        main_window._on_connect_profile_clicked()
        
        main_window.status_label.configure.assert_called()
    
    @patch('wifi_connector.gui.main_window.CredentialsManager')
    def test_on_connect_profile_clicked_disables_button_during_connection(
        self,
        mock_creds_manager_class,
        mock_ctk_modules,
        mock_credentials_manager
    ):
        """Test that Connect button is disabled during connection."""
        mock_creds_manager_class.return_value = mock_credentials_manager
        
        main_window = MainWindow()
        main_window.connect_profile_button = MagicMock()
        main_window.selected_center = mock_credentials_manager.get_all_centers.return_value[0]
        
        main_window._on_connect_profile_clicked()
        
        main_window.connect_profile_button.configure.assert_called_with(
            state="disabled",
            text="Connectant..."
        )
    
    @patch('wifi_connector.gui.main_window.NetworkManager')
    @patch('wifi_connector.gui.main_window.CredentialsManager')
    def test_on_disconnect_clicked_calls_disconnect(
        self,
        mock_creds_manager_class,
        mock_network_manager_class,
        mock_ctk_modules,
        mock_credentials_manager
    ):
        """Test that disconnect is called when Disconnect button is clicked."""
        mock_creds_manager_class.return_value = mock_credentials_manager
        mock_network_manager = MagicMock()
        mock_network_manager.disconnect.return_value = True
        mock_network_manager_class.return_value = mock_network_manager
        
        main_window = MainWindow()
        main_window.status_label = MagicMock()
        
        main_window._on_disconnect_clicked()
        
        mock_network_manager.disconnect.assert_called_once()
    
    @patch('wifi_connector.gui.main_window.CredentialsManager')
    def test_on_disconnect_clicked_during_connection_shows_error(
        self,
        mock_creds_manager_class,
        mock_ctk_modules,
        mock_credentials_manager
    ):
        """Test that error is shown when disconnecting during connection."""
        mock_creds_manager_class.return_value = mock_credentials_manager
        
        main_window = MainWindow()
        main_window.status_label = MagicMock()
        main_window.is_connecting = True
        
        main_window._on_disconnect_clicked()
        
        main_window.status_label.configure.assert_called()


class TestWindowClose:
    """Tests for window close handling."""
    
    @patch('wifi_connector.gui.main_window.CredentialsManager')
    def test_on_window_close_destroys_window(
        self,
        mock_creds_manager_class,
        mock_ctk_modules
    ):
        """Test that window is destroyed on close."""
        mock_creds_manager = MagicMock()
        mock_creds_manager.load_credentials.return_value = True
        mock_creds_manager.get_all_centers.return_value = []
        mock_creds_manager_class.return_value = mock_creds_manager
        
        main_window = MainWindow()
        main_window._on_window_close()
        
        mock_ctk_modules['window'].destroy.assert_called_once()
    
    @patch('wifi_connector.gui.main_window.CredentialsManager')
    def test_on_window_close_during_connection_shows_message(
        self,
        mock_creds_manager_class,
        mock_ctk_modules
    ):
        """Test that message is shown when closing during connection."""
        mock_creds_manager = MagicMock()
        mock_creds_manager.load_credentials.return_value = True
        mock_creds_manager.get_all_centers.return_value = []
        mock_creds_manager_class.return_value = mock_creds_manager
        
        main_window = MainWindow()
        main_window.status_label = MagicMock()
        main_window.is_connecting = True
        
        main_window._on_window_close()
        
        main_window.status_label.configure.assert_called()


class TestDarkThemeIntegration:
    """Tests para verificar que la GUI usa tema oscuro correctamente."""
    
    @patch('wifi_connector.utils.theme.ctk')
    @patch('wifi_connector.utils.theme.Logger')
    def test_dark_theme_applied_before_gui_creation(self, mock_logger, mock_theme_ctk):
        """Verifica que el tema oscuro se puede configurar antes de crear la GUI."""
        from wifi_connector.utils.theme import setup_dark_theme
        
        # Configurar tema
        setup_dark_theme()
        
        # Verificar que API fue llamada
        mock_theme_ctk.set_appearance_mode.assert_called_once_with("dark")
        mock_theme_ctk.set_default_color_theme.assert_called_once_with("blue")
        
        # Verificar logging
        from wifi_connector.utils import translations as t
        mock_logger.info.assert_called_once_with(t.THEME_LOG_CONFIGURED)
    
    @patch('wifi_connector.gui.main_window.CredentialsManager')
    def test_gui_components_use_customtkinter_widgets(
        self,
        mock_creds_manager_class,
        mock_ctk_modules
    ):
        """Verifica que los componentes GUI usan widgets customTkinter."""
        mock_creds_manager = MagicMock()
        mock_creds_manager.load_credentials.return_value = True
        mock_creds_manager.get_all_centers.return_value = []
        mock_creds_manager_class.return_value = mock_creds_manager
        
        main_window = MainWindow()
        
        # Verificar que se usan widgets customTkinter (CTk*)
        # Los mocks demuestran que MainWindow usa CTkFrame, CTkButton, etc.
        assert mock_ctk_modules['frame'].called
        assert mock_ctk_modules['button'].called
        assert mock_ctk_modules['label'].called

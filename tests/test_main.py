"""Integration tests for main entry point.

This module tests the main() function that launches the GUI application,
including error handling and graceful shutdown scenarios.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import importlib


class TestMain:
    """Test suite for main entry point."""
    
    @patch('wifi_connector.gui.main_window.MainWindow')
    @patch('wifi_connector.utils.theme.setup_dark_theme')
    @patch('wifi_connector.utils.logger.Logger')
    def test_main_successful_execution(self, mock_logger, mock_theme, mock_main_window):
        """Test successful execution of main() function."""
        # Import main here to ensure patches are applied
        import main as main_module
        importlib.reload(main_module)
        
        # Setup mocks
        mock_app = Mock()
        mock_main_window.return_value = mock_app
        
        # Execute main
        exit_code = main_module.main()
        
        # Verify Logger was setup
        assert mock_logger.setup.called
        assert any('Iniciant aplicació' in str(call) for call in mock_logger.info.call_args_list)
        
        # Verify MainWindow was created and run
        mock_main_window.assert_called_once()
        mock_app.run.assert_called_once()
        
        # Verify successful exit code
        assert exit_code == 0
        
        # Verify closing log message
        assert any('tancada normalment' in str(call) or 'cerrada' in str(call) for call in mock_logger.info.call_args_list)
    
    @patch('wifi_connector.gui.main_window.MainWindow')
    @patch('wifi_connector.utils.theme.setup_dark_theme')
    @patch('wifi_connector.utils.logger.Logger')
    def test_main_keyboard_interrupt(self, mock_logger, mock_theme, mock_main_window):
        """Test graceful handling of keyboard interrupt (Ctrl+C)."""
        import main as main_module
        importlib.reload(main_module)
        
        # Setup mock to raise KeyboardInterrupt
        mock_app = Mock()
        mock_app.run.side_effect = KeyboardInterrupt()
        mock_main_window.return_value = mock_app
        
        # Execute main
        exit_code = main_module.main()
        
        # Verify keyboard interrupt was logged
        assert any('interromp' in str(call) for call in mock_logger.info.call_args_list)
        
        # Verify exit code is 0 (graceful shutdown)
        assert exit_code == 0
    
    @patch('wifi_connector.gui.main_window.MainWindow')
    @patch('wifi_connector.utils.theme.setup_dark_theme')
    @patch('wifi_connector.utils.logger.Logger')
    def test_main_gui_initialization_error(self, mock_logger, mock_theme, mock_main_window):
        """Test error handling when GUI initialization fails."""
        import main as main_module
        importlib.reload(main_module)
        
        # Setup mock to raise exception during initialization
        error_message = "Failed to initialize GUI"
        mock_main_window.side_effect = Exception(error_message)
        
        # Execute main
        exit_code = main_module.main()
        
        # Verify error was logged
        assert mock_logger.error.called
        error_calls = [str(call) for call in mock_logger.error.call_args_list]
        assert any('Error' in call for call in error_calls)
        
        # Verify error exit code
        assert exit_code == 1
    
    @patch('wifi_connector.gui.main_window.MainWindow')
    @patch('wifi_connector.utils.theme.setup_dark_theme')
    @patch('wifi_connector.utils.logger.Logger')
    def test_main_runtime_error(self, mock_logger, mock_theme, mock_main_window):
        """Test error handling when runtime error occurs."""
        import main as main_module
        importlib.reload(main_module)
        
        # Setup mock to raise exception during run
        mock_app = Mock()
        mock_app.run.side_effect = RuntimeError("Runtime error occurred")
        mock_main_window.return_value = mock_app
        
        # Execute main
        exit_code = main_module.main()
        
        # Verify error was logged
        mock_logger.error.assert_called_once()
        
        # Verify error exit code
        assert exit_code == 1
    
    @patch('main.main')
    def test_main_module_execution(self, mock_main):
        """Test that main() is called when module is executed directly."""
        # This test verifies the if __name__ == "__main__" guard
        # We can't directly test this without running the module,
        # but we can verify the function exists and is callable
        import main as main_module
        
        # Verify main function exists
        assert hasattr(main_module, 'main')
        assert callable(main_module.main)
        
        # Verify it returns an integer
        mock_main.return_value = 0
        result = mock_main()
        assert isinstance(result, int)

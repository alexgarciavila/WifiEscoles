"""Unit tests for Logger class."""

import logging
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, call
from wifi_connector.utils.logger import Logger


class TestLoggerSetup:
    """Tests for Logger.setup() method."""
    
    def setup_method(self):
        """Reset logger state before each test."""
        Logger._logger = None
        Logger._is_setup = False
    
    def test_setup_creates_logger_with_default_level(self):
        """Test that setup() creates logger with INFO level by default."""
        Logger.setup()
        
        assert Logger._logger is not None
        assert Logger._logger.level == logging.INFO
        assert Logger._is_setup is True
    
    def test_setup_creates_logger_with_custom_level(self):
        """Test that setup() creates logger with specified level."""
        Logger.setup(level="DEBUG")
        
        assert Logger._logger.level == logging.DEBUG
    
    def test_setup_adds_console_handler(self):
        """Test that setup() adds console handler."""
        Logger.setup()
        
        handlers = Logger._logger.handlers
        assert len(handlers) >= 1
        assert any(isinstance(h, logging.StreamHandler) for h in handlers)
    
    def test_setup_adds_file_handler_when_log_file_specified(self, tmp_path):
        """Test that setup() adds file handler when log_file is provided."""
        log_file = tmp_path / "test.log"
        Logger.setup(log_file=str(log_file))
        
        handlers = Logger._logger.handlers
        file_handlers = [h for h in handlers if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) == 1
    
    def test_setup_configures_formatter_with_timestamps(self):
        """Test that setup() configures formatter with timestamp format."""
        Logger.setup()
        
        handler = Logger._logger.handlers[0]
        formatter = handler.formatter
        assert formatter is not None
        assert '%(asctime)s' in formatter._fmt
        assert '%(levelname)s' in formatter._fmt
        assert '%(message)s' in formatter._fmt
    
    def test_setup_only_runs_once(self):
        """Test that setup() only initializes once."""
        Logger.setup(level="DEBUG")
        first_logger = Logger._logger
        
        Logger.setup(level="ERROR")
        second_logger = Logger._logger
        
        assert first_logger is second_logger
        assert Logger._logger.level == logging.DEBUG
    
    def test_setup_clears_existing_handlers(self):
        """Test that setup() clears existing handlers to avoid duplicates."""
        Logger.setup()
        initial_handler_count = len(Logger._logger.handlers)
        
        # Reset and setup again
        Logger._is_setup = False
        Logger.setup()
        
        assert len(Logger._logger.handlers) == initial_handler_count


class TestLoggerInfo:
    """Tests for Logger.info() method."""
    
    def setup_method(self):
        """Reset logger state before each test."""
        Logger._logger = None
        Logger._is_setup = False
    
    def test_info_logs_message_at_info_level(self):
        """Test that info() logs message at INFO level."""
        Logger.setup()
        
        with patch.object(Logger._logger, 'info') as mock_info:
            Logger.info("Test info message")
            mock_info.assert_called_once_with("Test info message")
    
    def test_info_auto_setups_if_not_setup(self):
        """Test that info() automatically sets up logger if not setup."""
        assert Logger._is_setup is False
        
        Logger.info("Test message")
        
        assert Logger._is_setup is True
        assert Logger._logger is not None


class TestLoggerError:
    """Tests for Logger.error() method."""
    
    def setup_method(self):
        """Reset logger state before each test."""
        Logger._logger = None
        Logger._is_setup = False
    
    def test_error_logs_message_at_error_level(self):
        """Test that error() logs message at ERROR level."""
        Logger.setup()
        
        with patch.object(Logger._logger, 'error') as mock_error:
            Logger.error("Test error message")
            mock_error.assert_called_once_with("Test error message", exc_info=False)
    
    def test_error_includes_exception_info_when_requested(self):
        """Test that error() includes exception info when exc_info=True."""
        Logger.setup()
        
        with patch.object(Logger._logger, 'error') as mock_error:
            Logger.error("Test error with exception", exc_info=True)
            mock_error.assert_called_once_with("Test error with exception", exc_info=True)
    
    def test_error_auto_setups_if_not_setup(self):
        """Test that error() automatically sets up logger if not setup."""
        assert Logger._is_setup is False
        
        Logger.error("Test error")
        
        assert Logger._is_setup is True
        assert Logger._logger is not None


class TestLoggerDebug:
    """Tests for Logger.debug() method."""
    
    def setup_method(self):
        """Reset logger state before each test."""
        Logger._logger = None
        Logger._is_setup = False
    
    def test_debug_logs_message_at_debug_level(self):
        """Test that debug() logs message at DEBUG level."""
        Logger.setup()
        
        with patch.object(Logger._logger, 'debug') as mock_debug:
            Logger.debug("Test debug message")
            mock_debug.assert_called_once_with("Test debug message")
    
    def test_debug_auto_setups_if_not_setup(self):
        """Test that debug() automatically sets up logger if not setup."""
        assert Logger._is_setup is False
        
        Logger.debug("Test debug")
        
        assert Logger._is_setup is True
        assert Logger._logger is not None


class TestLoggerWarning:
    """Tests for Logger.warning() method."""
    
    def setup_method(self):
        """Reset logger state before each test."""
        Logger._logger = None
        Logger._is_setup = False
    
    def test_warning_logs_message_at_warning_level(self):
        """Test that warning() logs message at WARNING level."""
        Logger.setup()
        
        with patch.object(Logger._logger, 'warning') as mock_warning:
            Logger.warning("Test warning message")
            mock_warning.assert_called_once_with("Test warning message")
    
    def test_warning_auto_setups_if_not_setup(self):
        """Test that warning() automatically sets up logger if not setup."""
        assert Logger._is_setup is False
        
        Logger.warning("Test warning")
        
        assert Logger._is_setup is True
        assert Logger._logger is not None


class TestLoggerFormatting:
    """Tests for log message formatting."""
    
    def setup_method(self):
        """Reset logger state before each test."""
        Logger._logger = None
        Logger._is_setup = False
    
    def test_formatter_includes_timestamp(self):
        """Test that log formatter includes timestamp."""
        Logger.setup()
        
        handler = Logger._logger.handlers[0]
        formatter = handler.formatter
        
        assert formatter.datefmt == '%Y-%m-%d %H:%M:%S'
    
    def test_formatter_includes_logger_name(self):
        """Test that log formatter includes logger name."""
        Logger.setup()
        
        handler = Logger._logger.handlers[0]
        formatter = handler.formatter
        
        assert '%(name)s' in formatter._fmt
        assert Logger._logger.name == "wifi_connector"
    
    def test_formatter_includes_level_and_message(self):
        """Test that log formatter includes level and message."""
        Logger.setup()
        
        handler = Logger._logger.handlers[0]
        formatter = handler.formatter
        
        assert '%(levelname)s' in formatter._fmt
        assert '%(message)s' in formatter._fmt

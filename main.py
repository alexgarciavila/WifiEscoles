"""Main entry point for WiFi Connector GUI application.

This module provides the main entry point for launching the WiFi Connector
graphical user interface. It handles initialization, error handling, and
graceful shutdown of the application.
"""

import sys
import os

# Fix for PyInstaller --windowed mode: redirect stderr/stdout to avoid AttributeError
# When running as .exe without console, sys.stderr and sys.stdout are None
# This causes customtkinter to crash when trying to write warnings
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w')
if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w')

from wifi_connector.utils.logger import Logger
from wifi_connector.utils import translations as t


def main() -> int:
    """Main function to create and run the WiFi Connector GUI.
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        # Setup logging
        Logger.setup(level="INFO")
        Logger.info(t.APP_STARTING)
        
        # Configure dark theme BEFORE importing GUI modules (critical)
        from wifi_connector.utils.theme import setup_dark_theme
        try:
            setup_dark_theme()
        except Exception as e:
            Logger.critical(f"No se pudo configurar el tema oscuro: {e}")
            print("Error crítico: No se puede iniciar la aplicación sin tema oscuro.")
            print(f"Detalles: {e}")
            return 1
        
        # Import GUI after theme setup to ensure widgets use dark theme
        from wifi_connector.gui.main_window import MainWindow
        
        # Create and run the main window
        app = MainWindow()
        app.run()
        
        Logger.info(t.APP_CLOSED)
        return 0
        
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        Logger.info(t.APP_INTERRUPTED)
        print("\nAplicació interrompuda per l'usuari")
        return 0
        
    except Exception as e:
        # Handle any unexpected errors during GUI initialization
        Logger.error(t.APP_ERROR_START.format(error=e), exc_info=True)
        print(t.APP_ERROR_MESSAGE)
        print(t.APP_ERROR_DETAILS.format(error=e))
        print(f"\n{t.APP_ERROR_CHECK_LOGS}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

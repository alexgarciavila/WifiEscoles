"""Main entry point for WiFi Connector GUI application.

This module provides the main entry point for launching the WiFi Connector
graphical user interface. It handles initialization, error handling, and
graceful shutdown of the application.
"""

import sys
from wifi_connector.gui.main_window import MainWindow
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

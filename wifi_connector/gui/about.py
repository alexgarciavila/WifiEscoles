import customtkinter as ctk
import webbrowser
from typing import Optional

class AboutWindow(ctk.CTkToplevel):
    """Ventana para mostrar información de la aplicación y créditos."""

    def __init__(self, parent: Optional[ctk.CTk] = None):
        super().__init__(parent)

        self.title("Sobre WifiEscoles")
        self.geometry("400x420")
        self.resizable(False, False)
        
        self.transient(parent)
        self.grab_set()
        self.focus_set()

        self._setup_ui()

    def _setup_ui(self):
        """Inicializa los componentes de la interfaz."""
        
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title_label = ctk.CTkLabel(
            main_frame,
            text="WiFi de Centres Educatius",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(10, 5))

        version_label = ctk.CTkLabel(
            main_frame,
            text="Versió 1.0",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        version_label.pack(pady=(0, 20))

        description_text = (
            "Aquesta aplicació facilita la connexió a les xarxes WiFi\n"
            "dels centres educatius de la Generalitat de Catalunya.\n\n"
            "Desenvolupada amb carinyo pels meus tècnics i companys.\n\n"
            "Que la força us acompanyi."
        )
        description_label = ctk.CTkLabel(
            main_frame,
            text=description_text,
            font=ctk.CTkFont(size=13),
            justify="center"
        )
        description_label.pack(pady=(0, 30))

        dev_label = ctk.CTkLabel(
            main_frame,
            text="Desenvolupat per:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        dev_label.pack(pady=(0, 5))

        name_label = ctk.CTkLabel(
            main_frame,
            text="Àlex Garcia Vilà",
            font=ctk.CTkFont(size=14)
        )
        name_label.pack(pady=(0, 10))

        linkedin_btn = ctk.CTkButton(
            main_frame,
            text="Veure Perfil de LinkedIn",
            command=self._open_linkedin,
            width=200,
            height=35,
            fg_color="#0077b5",
            hover_color="#005582"
        )
        linkedin_btn.pack(pady=(0, 10))

        website_btn = ctk.CTkButton(
            main_frame,
            text="Visita el meu portafolis",
            command=self._open_portfolio,
            width=200,
            height=35,
            fg_color="#2e7d32",
            hover_color="#1b5e20"
        )
        website_btn.pack(pady=(0, 10))

    def _open_linkedin(self):
        """Abre el perfil de LinkedIn en el navegador por defecto."""
        webbrowser.open("https://www.linkedin.com/in/alexgarciavila/")

    def _open_portfolio(self):
        """Abre el sitio web personal en el navegador por defecto."""
        webbrowser.open("https://alexgarciavila.github.io/")

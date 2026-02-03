"""Diálogo modal para solicitar la contraseña del vault."""

from typing import Optional
import customtkinter as ctk

from wifi_connector.utils import translations as t


class VaultPasswordDialog(ctk.CTkToplevel):
    """Diálogo modal para introducir la contraseña del vault."""

    def __init__(self, parent: ctk.CTk, error_message: str = "") -> None:
        super().__init__(parent)

        self._password: Optional[str] = None

        self.title(t.VAULT_DIALOG_TITLE)
        # Aumentar altura para acomodar mensajes de error sin comprimir los botones
        self.geometry("420x250")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()
        self.focus_set()

        self._build_ui(error_message)

    def _build_ui(self, error_message: str) -> None:
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title_label = ctk.CTkLabel(
            main_frame,
            text=t.VAULT_PROMPT_TITLE,
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        title_label.pack(pady=(0, 10))

        prompt_label = ctk.CTkLabel(
            main_frame,
            text=t.VAULT_PROMPT_MESSAGE,
            font=ctk.CTkFont(size=12),
            justify="center",
        )
        prompt_label.pack(pady=(0, 10))

        self._entry = ctk.CTkEntry(
            main_frame,
            placeholder_text=t.VAULT_PASSWORD_PLACEHOLDER,
            show="•",
        )
        self._entry.pack(fill="x", padx=10)
        self._entry.focus_set()
        self._entry.bind("<Return>", lambda event: self._submit())

        if error_message:
            error_label = ctk.CTkLabel(
                main_frame,
                text=error_message,
                font=ctk.CTkFont(size=11),
                text_color="#e74c3c",
            )
            error_label.pack(pady=(10, 0))

        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=(15, 0))

        submit_btn = ctk.CTkButton(
            button_frame,
            text=t.VAULT_UNLOCK_BUTTON,
            command=self._submit,
            width=120,
        )
        submit_btn.pack(side="left", padx=5)

        cancel_btn = ctk.CTkButton(
            button_frame,
            text=t.VAULT_CANCEL_BUTTON,
            command=self._cancel,
            width=120,
            fg_color="#7f8c8d",
            hover_color="#707b7c",
        )
        cancel_btn.pack(side="left", padx=5)

        self.protocol("WM_DELETE_WINDOW", self._cancel)

    def _submit(self) -> None:
        value = self._entry.get().strip()
        if not value:
            return
        self._password = value
        self.destroy()

    def _cancel(self) -> None:
        self._password = None
        self.destroy()

    def get_password(self) -> Optional[str]:
        """Bloquea hasta cerrar el diálogo y devuelve la contraseña."""
        self.wait_window()
        return self._password

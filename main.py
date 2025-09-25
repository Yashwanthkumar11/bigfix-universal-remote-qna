from bigfix_universal_remote_qna.services.qna_remote_debugger import QnARemoteDebugger
import os, sys
import tkinter as tk

def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS  # PyInstaller sets this
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def main():
    """Main entry point for the application"""
    root = tk.Tk()
    try:
        icon_path = resource_path(os.path.join("assets", "bigfix_logo.ico"))
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
    except Exception:
        pass

    app = QnARemoteDebugger(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
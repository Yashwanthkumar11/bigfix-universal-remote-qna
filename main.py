from pyutils_lib.services.stat_timer import StatTimer         # type: ignore
from pyutils_lib.services.config_manager import ConfigManager # type: ignore
from bigfix_universal_remote_qna.services.qna_remote_debugger import QnARemoteDebugger
import os
import tkinter as tk


def main():
    """Main entry point for the application"""
    root = tk.Tk()
    try:
        icon_path =  os.path.join(os.path.dirname(__file__), "assets", "bigfix_logo.ico")
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)

    except Exception:
        pass
    app = QnARemoteDebugger(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()





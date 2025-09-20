from pyutils_lib.services.stat_timer import StatTimer         # type: ignore
from pyutils_lib.services.config_manager import ConfigManager # type: ignore
from bigfix_universal_remote_qna.services.qna_remote_debugger import QnARemoteDebugger
import tkinter as tk


# ConfigManager().define_setting("test",False,3,'str','A test setting')
# ConfigManager().define_setting("secret_1",True,None,'str','A secret test setting')


def main():
    """Main entry point for the application"""
    root = tk.Tk()
    app = QnARemoteDebugger(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()





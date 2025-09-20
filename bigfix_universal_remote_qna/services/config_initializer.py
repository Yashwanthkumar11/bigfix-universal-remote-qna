from pyutils_lib.services.config_manager import ConfigManager   # pyright: ignore[reportMissingImports]

class ConfigInitializer:
    """Initialize all configuration settings using your ConfigManager"""
    
    @staticmethod
    def initialize_config():
        """Define all configuration settings"""
        config_manager = ConfigManager()
        
        # Connection settings
        config_manager.define_setting(
            "last_used_connection_index", False, 0, int, 
            "Index of the last used connection profile"
        )
        
        # UI Settings
        config_manager.define_setting(
            "window_geometry", False, "1000x700", str, 
            "Main window geometry (widthxheight)"
        )
        config_manager.define_setting(
            "save_passwords", False, True, bool, 
            "Whether to save passwords in encrypted form"
        )
        
        # QnA Paths for different OS
        config_manager.define_setting(
            "qna_path_windows", False, 
            r'C:\Program Files (x86)\BigFix Enterprise\BES Client\QnA.exe', str,
            "QnA executable path for Windows systems"
        )
        config_manager.define_setting(
            "qna_path_linux", False, "/opt/BESClient/bin/QnA", str,
            "QnA executable path for Linux systems"
        )
        config_manager.define_setting(
            "qna_path_mac", False, 
            "/Library/Application Support/BigFix/BES Agent/bin/QnA", str,
            "QnA executable path for macOS systems"
        )
        
        # Recent queries (stored as JSON string)
        config_manager.define_setting(
            "recent_queries", False, "[]", str,
            "JSON array of recent queries (max 10)"
        )
        
        
        # Load the configuration after defining all settings
        config_manager.load_configuration()
        
        return config_manager
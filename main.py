from pyutils_lib.services.stat_timer import StatTimer         # type: ignore
from pyutils_lib.services.config_manager import ConfigManager # type: ignore


ConfigManager().define_setting("test",False,3,'str','A test setting')
ConfigManager().define_setting("secret_1",True,None,'str','A secret test setting')

this_timer = StatTimer()

ConfigManager().load_configuration()

print("Hello World")

print(f"Total Time: {this_timer.Duration()}")
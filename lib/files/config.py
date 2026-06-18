import ujson
import os

class ConfigManager:
    def __init__(self, path="/config.json"):
        self.path = path
        self._create()
        
    def _create(self):
        try:
            os.stat(self.path)
        except:
            with open(self.path, "w") as f:
                config = ujson.dump({}, f)
        
    def set(self, key, value=None):
        # Read config file
        with open(self.path, "r") as f:
            config = ujson.load(f)
        # Change wifi config
        config[key] = value
        # Rewrite new wifi config
        with open(self.path, "w") as f:
            ujson.dump(config, f)
    
    def delete(self, key):
        # Read config file
        with open(self.path, "r") as f:
            config = ujson.load(f)
        # Change wifi config
        try:
            del config[key]
        except:
            pass
        # Rewrite new wifi config
        with open(self.path, "w") as f:
            ujson.dump(config, f)
            
    def get(self, key):
        # Read config file
        with open(self.path, "r") as f:
            config = ujson.load(f)
        # Change wifi config
        return config.get(key)
    
    def read(self):
        # Read config file
        with open(self.path, "r") as f:
            config = ujson.load(f)
        # Change wifi config
        return config
    
    def defaults(self, values):
        """
        values = {
            "wifi_ssid": None,
            "wifi_password": None,
            "mk": 1
        }
        """
        config = self.read()
        for key in values:
            if key not in config:
                self.set(key, values[key])

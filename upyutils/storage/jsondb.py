import ujson
import os

class JsonDB:
    """
    Administrador de archivos de JSON.

    Permite crear, leer, modificar y eliminar valores dentro de
    un archivo JSON almacenado en el sistema de archivos del
    dispositivo.

    Attributes:
        path (str): Ruta del archivo JSON.
    """
    def __init__(
        self, 
        path: str = "/data.json"
    ) -> None:
        """
        Inicializa el administrador de configuración.

        Si el archivo no existe, se crea automáticamente.

        Args:
            path (str, optional): Ruta del archivo JSON.
                Por defecto es "/data.json".

        Returns:
            None
        """
        self.path = path
        self._create()
        
    def _create(self):
        try:
            os.stat(self.path)
        except:
            with open(self.path, "w") as f:
                config = ujson.dump({}, f)
        
    def set(
        self, 
        key: str, 
        value=None
    ) -> None:
        """
        Crea o actualiza una clave dentro del archivo.

        Args:
            key (str): Nombre de la clave.
            value (Any, optional): Valor a almacenar.

        Returns:
            None
        """
        # Read config file
        with open(self.path, "r") as f:
            config = ujson.load(f)
        # Change wifi config
        config[key] = value
        # Rewrite new wifi config
        with open(self.path, "w") as f:
            ujson.dump(config, f)
    
    def delete(
        self, 
        key: str
    ) -> None:
        """
        Elimina una clave del archivo.

        Si la clave no existe, la operación es ignorada.

        Args:
            key (str): Nombre de la clave a eliminar.

        Returns:
            None
        """
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
            
    def get(
        self, 
        key: str
    ):
        """
        Obtiene el valor asociado a una clave.

        Args:
            key (str): Nombre de la clave.

        Returns:
            Any: Valor almacenado para la clave o None si no existe.
        """
        # Read config file
        with open(self.path, "r") as f:
            config = ujson.load(f)
        # Change wifi config
        return config.get(key)
    
    def read(self) -> dict:
        """
        Lee el contenido completo del archivo.

        Returns:
            dict: Diccionario con todos los valores almacenados.
        """
        # Read config file
        with open(self.path, "r") as f:
            config = ujson.load(f)
        # Change wifi config
        return config
    
    def defaults(self, values: dict) -> None:
        """
        Establece valores predeterminados para claves inexistentes.

        Solo se agregan las claves que aún no existen en el
        archivo actual.

        Args:
            values (dict): Diccionario con claves y valores
                predeterminados.
                
        Returns:
            None
        """
        config = self.read()
        for key in values:
            if key not in config:
                self.set(key, values[key])

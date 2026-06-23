import network
import time

""" DHCP IP
wifi = Wifi()

wifi.connect("MiWifi", "12345678")

"""

""" STATIC IP
wifi = Wifi()

wifi.connect(
    ssid="MiWifi",
    password="12345678",
    static_ip=(
        "192.168.1.50",
        "255.255.255.0",
        "192.168.1.1",
        "8.8.8.8"
    )
)
"""

class Wifi:
    """
    Administrador de conexiones WiFi para ESP32.

    Permite conectarse a redes WiFi mediante DHCP o IP estática,
    consultar información de red y controlar la interfaz STA
    (Station Mode).

    Attributes:
        log (bool): Habilita o deshabilita mensajes de consola.
        __sta_if (network.WLAN): Interfaz WiFi en modo estación.
    """
    def __init__(self, log: bool = True) -> None:
        """
        Inicializa la interfaz WiFi en modo estación.

        Args:
            log (bool, optional): Habilita mensajes de depuración.
                Por defecto es True.

        Returns:
            None
        """
        self.log = log
        self.__sta_if = network.WLAN(network.STA_IF)
        self.__sta_if.active(False)

    def connect(
        self,
        ssid: str,
        password: str = "",
        timeout: int | float = 10,
        hostname: str = "ESP32",
        static_ip: tuple | None = None,
        triying_connect_callback=None
    ) -> bool:
        """
        Conecta el dispositivo a una red WiFi.

        Puede utilizar DHCP o una configuración IP estática.

        Args:
            ssid (str): Nombre de la red WiFi.
            password (str, optional): Contraseña de la red.
            timeout (int | float, optional): Tiempo máximo de
                espera para la conexión en segundos.
            hostname (str, optional): Nombre del dispositivo
                en la red.
            static_ip (tuple | None, optional): Configuración
                IP estática en formato:

                    (
                        "192.168.1.50",
                        "255.255.255.0",
                        "192.168.1.1",
                        "8.8.8.8"
                    )

            triying_connect_callback (callable | None, optional):
                Función ejecutada periódicamente mientras se
                intenta establecer la conexión.

        Returns:
            bool: True si la conexión fue exitosa,
            False si ocurrió un timeout.
        """
        if self.isconnected():
            self._console("Already connected:", self.get_ip())
            return True

        self._console(f"Connecting to WiFi: {ssid}")
        self.__sta_if.active(True)
        self.__sta_if.config(hostname=hostname)


        # Asignar IP estática si se pasa
        if static_ip:
            self._console("Using static IP:", static_ip[0])
            self.__sta_if.ifconfig(static_ip)

        self.__sta_if.connect(ssid, password)

        start = time.time()
        while not self.isconnected():
            if time.time() - start > timeout:
                if self.log:
                    print()
                self._console("Connection timeout")
                return False

            if self.log:
                if triying_connect_callback:
                    triying_connect_callback()
                print(".", end="")
            time.sleep(0.5)

        if self.log:
            print()
        self._console("Connected! IP:", self.get_ip())
        return True

    def isconnected(self) -> bool:
        """
        Indica si existe una conexión WiFi activa.

        Returns:
            bool: True si el dispositivo está conectado,
            False en caso contrario.
        """
        return self.__sta_if.isconnected()

    def get_ip(self) -> str | None:
        """
        Obtiene la dirección IP asignada.

        Returns:
            str | None: Dirección IP actual o None si no existe
            una conexión activa.
        """
        if self.isconnected():
            return self.__sta_if.ifconfig()[0]
        return None

    def get_mac(self) -> str:
        """
        Obtiene la dirección MAC de la interfaz WiFi.

        Returns:
            str: Dirección MAC en formato hexadecimal.
        """
        mac = self.__sta_if.config('mac')
        return ':'.join('{:02X}'.format(b) for b in mac)

    def off(self, delay: int | float = 0) -> None:
        """
        Desactiva la interfaz WiFi.

        Args:
            delay (int | float, optional): Tiempo de espera
                después de apagar la interfaz, en segundos.

        Returns:
            None
        """
        self.__sta_if.active(False)
        try:
            if self.__sta_if.active():
                self.__sta_if.disconnect()
        except OSError:
            pass
        time.sleep(delay)

    def _console(self, *args):
        if self.log:
            print("[ WIFI ]", *args)

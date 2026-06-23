import network
import time

"""
ap = uAccessPoint(
    essid="ESP32_AP",
    password="12345678",
    
    # Optional
    ip_config=(
        "192.168.10.1",
        "255.255.255.0",
        "192.168.10.1",
        "8.8.8.8"
    )
)

ap.active()
"""
class uAccessPoint:
    """
    Administrador de puntos de acceso WiFi para ESP32.

    Permite crear, configurar y controlar un punto de acceso
    (Access Point) utilizando la interfaz AP de MicroPython.

    Attributes:
        essid (str): Nombre de la red WiFi.
        password (str | None): Contraseña de la red WiFi.
        ip_config (tuple | None): Configuración IP estática
            en formato (ip, mask, gateway, dns).
        log (bool): Habilita o deshabilita mensajes de consola.
        ap (network.WLAN): Interfaz Access Point.
    """    
    def __init__(
        self,
        essid: str = "ESP32",
        password: str | None = None,
        ip_config: tuple | None = None,
        log: bool = True
    ) -> None:
        """
        Inicializa el punto de acceso.

        Args:
            essid (str, optional): Nombre de la red WiFi.
                Por defecto es "ESP32".
            password (str | None, optional): Contraseña WPA/WPA2.
                Debe contener al menos 8 caracteres.
                Si es None, la red será abierta.
            ip_config (tuple | None, optional): Configuración IP
                estática en formato:
                (ip, mascara, gateway, dns).
            log (bool, optional): Habilita mensajes de depuración.
                Por defecto es True.

        Raises:
            ValueError: Si la contraseña contiene menos de
                8 caracteres.

        Returns:
            None
        """
        if password is not None and len(password) < 8:
            raise ValueError("Password must have at least 8 characters")

        self.log = log
        self.essid = essid
        self.password = password
        self.ip_config = ip_config
        self.ap = network.WLAN(network.AP_IF)

        self.configure()

    # =========================
    # Configure AP
    # =========================
    def configure(self) -> None:
        """
        Configura y reinicia el punto de acceso.

        Aplica la configuración IP y los parámetros de
        seguridad especificados durante la inicialización.

        Returns:
            None
        """
        # Reiniciar AP
        self.ap.active(False)

        time.sleep(1)

        # ACTIVAR PRIMERO
        self.ap.active(True)

        time.sleep(1)

        # Configurar IP DESPUÉS
        if self.ip_config:
            self.ap.ifconfig(self.ip_config)
            self._console("Static IP:", self.ip_config[0])

        # Configurar seguridad
        if self.password:
            self.ap.config(
                essid=self.essid,
                password=self.password,
                authmode=network.AUTH_WPA_WPA2_PSK
            )
        else:
            self.ap.config(
                essid=self.essid,
                authmode=network.AUTH_OPEN
            )
            
    # =========================
    # Stations
    # =========================
    def stations(self) -> list:
        """
        Obtiene la lista de dispositivos conectados.

        Returns:
            list: Lista de estaciones conectadas.
        """
        return self.ap.status('stations') or []

    def is_station_connected(self, mac: bytes) -> bool:
        """
        Verifica si una dirección MAC está conectada.

        Args:
            mac (bytes): Dirección MAC del dispositivo.

        Returns:
            bool: True si el dispositivo está conectado,
            False en caso contrario.
        """
        return any(sta[0] == mac for sta in self.stations())

    # =========================
    # Control
    # =========================
    def active(self) -> None:
        """
        Activa el punto de acceso.

        Returns:
            None
        """
        self.ap.active(True)
        self._console(f"Active as '{self.essid}'")
        self._console("IP:", self.ap.ifconfig()[0])

    def deactive(self) -> None:
        """
        Desactiva el punto de acceso.

        Returns:
            None
        """
        self.ap.active(False)
        self._console("Deactivated")

    # =========================
    # Network info
    # =========================
    def ifconfig(self) -> tuple:
        """
        Obtiene la configuración de red actual.

        Returns:
            tuple: Configuración en formato
            (ip, mascara, gateway, dns).
        """
        return self.ap.ifconfig()

    def is_active(self) -> bool:
        """
        Indica si el punto de acceso está activo.

        Returns:
            bool: Estado actual del Access Point.
        """
        return self.ap.active()

    # =========================
    # Log
    # =========================
    def _console(self, *args) -> None:
        """
        Imprime mensajes de depuración.

        Los mensajes solo se muestran si el atributo
        'log' está habilitado.

        Args:
            *args: Valores a imprimir.

        Returns:
            None
        """
        if self.log:
            print("[ uAP ]", *args)

"""
def device_connected(sta):
    mac = ':'.join('{:02X}'.format(b) for b in sta[0])
    print("Conectado:", mac)

def device_disconnected(sta):
    mac = ':'.join('{:02X}'.format(b) for b in sta[0])
    print("Desconectado:", mac)

ap = uAccessPoint()
ap.active()

watcher = APWatcher(
    ap,
    on_connect=device_connected,
    on_disconnect=device_disconnected,
    interval=1
)

watcher.start()
"""
import time

class APWatcher:
    """
    Monitor de dispositivos conectados a un punto de acceso.

    Detecta conexiones y desconexiones de estaciones
    mediante sondeo periódico y ejecuta callbacks
    personalizados.

    Attributes:
        uap (uAccessPoint): Punto de acceso monitoreado.
        on_connect (callable | None): Función ejecutada
            cuando un dispositivo se conecta.
        on_disconnect (callable | None): Función ejecutada
            cuando un dispositivo se desconecta.
        interval (int | float): Intervalo de sondeo
            en segundos.
        last (list): Última lista conocida de estaciones.
    """    
    def __init__(
        self,
        uap,
        on_connect=None,
        on_disconnect=None,
        interval: int | float = 1
    ) -> None:
        """
        Inicializa el monitor de conexiones.

        Args:
            uap (uAccessPoint): Punto de acceso a monitorear.
            on_connect (callable | None, optional): Callback
                ejecutado al detectar una nueva conexión.
            on_disconnect (callable | None, optional): Callback
                ejecutado al detectar una desconexión.
            interval (int | float, optional): Tiempo entre
                verificaciones en segundos.

        Returns:
            None
        """
        self.uap = uap                
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect
        self.interval = interval
        self.last = []

    def start(self) -> None:
        """
        Inicia el monitoreo continuo de estaciones.

        Este método ejecuta un bucle infinito que detecta
        dispositivos conectados y desconectados, invocando
        los callbacks correspondientes cuando se producen
        cambios.

        Returns:
            None
        """
        while True:
            current = self.uap.stations()

            # Nuevos dispositivos
            for sta in current:
                if sta not in self.last:
                    if self.on_connect:
                        self.on_connect(sta)

            # Dispositivos desconectados
            for sta in self.last:
                if sta not in current:
                    if self.on_disconnect:
                        self.on_disconnect(sta)

            self.last = current
            time.sleep(self.interval)

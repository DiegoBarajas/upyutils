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
    def __init__(
        self,
        essid="ESP32",
        password=None,
        ip_config=None,
        log=True
    ):
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
    def configure(self):
        # Reiniciar AP
        self.ap.active(False)

        time.sleep(1)

        # ACTIVAR PRIMERO
        self.ap.active(True)

        time.sleep(1)

        # Configurar IP DESPUÉS
        if self.ip_config:
            self.ap.ifconfig(self.ip_config)
            self.console("Static IP:", self.ip_config[0])

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
    def stations(self):
        return self.ap.status('stations') or []

    def is_station_connected(self, mac):
        return any(sta[0] == mac for sta in self.stations())

    # =========================
    # Control
    # =========================
    def active(self):
        self.ap.active(True)
        self.console(f"Active as '{self.essid}'")
        self.console("IP:", self.ap.ifconfig()[0])

    def deactive(self):
        self.ap.active(False)
        self.console("Deactivated")

    # =========================
    # Network info
    # =========================
    def ifconfig(self):
        return self.ap.ifconfig()

    def is_active(self):
        return self.ap.active()

    # =========================
    # Log
    # =========================
    def console(self, *args):
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
    def __init__(self, uap, on_connect=None, on_disconnect=None, interval=1):
        self.uap = uap                
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect
        self.interval = interval
        self.last = []

    def start(self):
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

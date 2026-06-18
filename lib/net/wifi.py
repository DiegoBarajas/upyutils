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
    def __init__(self, log=True):
        self.log = log
        self.__sta_if = network.WLAN(network.STA_IF)
        self.__sta_if.active(False)

    def connect(
        self,
        ssid,
        password="",
        timeout=10,
        hostname="ESP32",
        static_ip=None,
        triying_connect_callback=None
    ):
        """
        static_ip = (
            "192.168.1.50",
            "255.255.255.0",
            "192.168.1.1",
            "8.8.8.8"
        )
        """

        if self.isconnected():
            self.console("Already connected:", self.get_ip())
            return True

        self.console(f"Connecting to WiFi: {ssid}")
        self.__sta_if.active(True)
        self.__sta_if.config(hostname=hostname)


        # Asignar IP estática si se pasa
        if static_ip:
            self.console("Using static IP:", static_ip[0])
            self.__sta_if.ifconfig(static_ip)

        self.__sta_if.connect(ssid, password)

        start = time.time()
        while not self.isconnected():
            if time.time() - start > timeout:
                if self.log:
                    print()
                self.console("Connection timeout")
                return False

            if self.log:
                if triying_connect_callback:
                    triying_connect_callback()
                print(".", end="")
            time.sleep(0.5)

        if self.log:
            print()
        self.console("Connected! IP:", self.get_ip())
        return True

    def isconnected(self):
        return self.__sta_if.isconnected()

    def get_ip(self):
        if self.isconnected():
            return self.__sta_if.ifconfig()[0]
        return None

    def get_mac(self):
        mac = self.__sta_if.config('mac')
        return ':'.join('{:02X}'.format(b) for b in mac)

    def off(self, delay=0):
        self.__sta_if.active(False)
        try:
            if self.__sta_if.active():
                self.__sta_if.disconnect()
        except OSError:
            pass
        time.sleep(delay)

    def console(self, *args):
        if self.log:
            print("[ WIFI ]", *args)

import network
import espnow

class ESPNowReceiver:
    def __init__(self):
        sta = network.WLAN(network.STA_IF)
        sta.active(True)

        self.esp = espnow.ESPNow()
        self.esp.active(True)

    def receive(self):
        return self.esp.recv(0)
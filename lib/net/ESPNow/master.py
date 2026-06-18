import network
import espnow

class ESPNowMaster:
    def __init__(self):
        self.sta = network.WLAN(network.STA_IF)
        self.e = espnow.ESPNow()
        self.peers = {}

        self.activate()

    def activate(self):
        self.sta.active(True)
        self.e.active(True)

    def deactivate(self):
        self.e.active(False)
        self.sta.active(False)

    def get_mac(self):
        return self.sta.config("mac")

    def add_peer(self, peer_mac, alias=None):
        try:
            self.e.add_peer(peer_mac)
        except OSError:
            pass

        if alias:
            self.peers[alias] = peer_mac

    def remove_peer(self, peer):
        peer_mac = self._resolve_peer(peer)

        try:
            self.e.del_peer(peer_mac)
        except OSError:
            pass

    def send(self, peer, message):
        peer_mac = self._resolve_peer(peer)

        if isinstance(message, str):
            message = message.encode()

        self.e.send(peer_mac, message)

    def receive(self, timeout=0):
        return self.e.recv(timeout)

    def receive_text(self, timeout=0):
        mac, msg = self.receive(timeout)

        if msg is None:
            return None, None

        try:
            msg = msg.decode()
        except:
            pass

        return mac, msg

    def _resolve_peer(self, peer):
        if isinstance(peer, bytes):
            return peer

        if peer in self.peers:
            return self.peers[peer]

        raise ValueError(
            "Peer '{}' no registrado".format(peer)
        )
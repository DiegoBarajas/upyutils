from dfplayer import DFPlayer
from time import sleep_ms

tracks = {
    "on": {
        "id": 1,
        "duration_ms": 1.504 * 1000
    },
    "off": {
        "id": 2,
        "duration_ms": 1 * 1000
    }
}

class TrackManager:
    def __init__(self, uart_id=2, tx=17, rx=16):
        self.player = DFPlayer(uart_id=uart_id, tx=tx, rx=rx)
        
    def play(self, name):
        if name not in tracks:
            return
        track = tracks[name.lower()]
        self.player.play(track["id"])
        sleep_ms(int( track["duration_ms"] ))
    
    def volume(self, vol):
        vol = max(0, min(100, vol))
        volume = vol * 30 / 100
        self.player.volume(int(volume))
    


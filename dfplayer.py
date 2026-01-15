from machine import UART, Pin
import time

class DFPlayer:
    def __init__(self, uart_id=2, tx=17, rx=16):
        self.uart = UART(
            uart_id,
            baudrate=9600,
            bits=8,
            parity=None,
            stop=1,
            tx=Pin(tx),
            rx=Pin(rx),
            timeout=100
        )
        time.sleep(1)

    def _checksum(self, cmd, param):
        total = 0xFF + 0x06 + cmd + 0x00 + (param >> 8) + (param & 0xFF)
        return (-total) & 0xFFFF

    def _send(self, cmd, param=0):
        cs = self._checksum(cmd, param)
        packet = bytes([
            0x7E, 0xFF, 0x06, cmd, 0x00,
            (param >> 8) & 0xFF,
            param & 0xFF,
            (cs >> 8) & 0xFF,
            cs & 0xFF,
            0xEF
        ])
        self.uart.write(packet)

    def play(self, track):
        self._send(0x03, track)

    def volume(self, level):
        self._send(0x06, max(0, min(30, level)))

    def stop(self):
        self._send(0x16)

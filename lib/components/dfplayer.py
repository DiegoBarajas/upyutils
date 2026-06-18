from machine import UART, Pin
import time

class DFPlayer:
    """
    Controlador para módulos DFPlayer Mini mediante UART.

    Esta clase proporciona una interfaz sencilla para reproducir
    archivos de audio almacenados en una tarjeta microSD usando
    un módulo DFPlayer Mini conectado a un microcontrolador ESP32.

    Attributes:
        uart (UART): Instancia de comunicación serial utilizada
            para enviar comandos al DFPlayer.

    Example:
        >>> player = DFPlayer(tx=17, rx=16)
        >>> player.volume(20)
        >>> player.play(1)
    """
    def __init__(
        self, 
        uart_id:int = 2, 
        tx:int = 17, 
        rx:int = 16
    ) -> None:
        """
        Inicializa la comunicación UART con el módulo DFPlayer.

        Args:
            uart_id (int, optional): Identificador del puerto UART.
                Por defecto es 2.
            tx (int, optional): Pin TX del ESP32 conectado al RX
                del DFPlayer. Por defecto es 17.
            rx (int, optional): Pin RX del ESP32 conectado al TX
                del DFPlayer. Por defecto es 16.
        """
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

    def play(
        self, 
        track:int
    ) -> None:
        """
        Reproduce una pista específica.

        Args:
            track (int): Número de archivo a reproducir.
                Debe existir en la tarjeta microSD.
        """
        self._send(0x03, track)

    def volume(
        self, 
        level:int
    ) -> None:
        """
        Establece el volumen de reproducción.

        Args:
            level (int): Nivel de volumen entre 0 y 30.
                Los valores fuera del rango serán ajustados
                automáticamente al límite más cercano.
        """
        self._send(0x06, max(0, min(30, level)))

    def stop(self) -> None:
        """
        Detiene la reproducción actual.
        """
        self._send(0x16)

from machine import Pin
import neopixel
from time import sleep


class WS2812B:
    """
    Controlador para tiras LED WS2812B (NeoPixel).

    Permite controlar el color, brillo y efectos básicos de una
    tira LED WS2812B conectada a un microcontrolador compatible
    con MicroPython.

    Attributes:
        din (Pin): Pin de datos de la tira LED.
        num_leds (int): Número total de LEDs.
        brillo (float): Factor de brillo en el rango [0.0, 1.0].
        np (neopixel.NeoPixel): Instancia de control NeoPixel.
    """

    def __init__(
        self,
        din_pin: int,
        num_leds: int,
        brillo: float = 1.0
    ) -> None:
        """
        Inicializa la tira LED.

        Args:
            din_pin (int): Pin GPIO conectado a la entrada DIN
                de la tira LED.
            num_leds (int): Cantidad de LEDs en la tira.
            brillo (float, optional): Nivel de brillo en el
                rango [0.0, 1.0]. Por defecto es 1.0.

        Returns:
            None
        """
        self.din = Pin(din_pin)
        self.num_leds = num_leds
        self.brillo = brillo
        self.np = neopixel.NeoPixel(self.din, self.num_leds)
        self.off_all()

    def _apply_brillo(
        self,
        colors: tuple[int, int, int]
    ) -> tuple[int, int, int]:
        """
        Aplica el factor de brillo a un color RGB.

        Args:
            colors (tuple[int, int, int]): Color RGB donde cada
                componente está en el rango [0, 255].

        Returns:
            tuple[int, int, int]: Color RGB ajustado al brillo
            configurado.
        """
        r, g, b = colors
        return (
            int(r * self.brillo),
            int(g * self.brillo),
            int(b * self.brillo)
        )

    def set_brillo(
        self,
        brillo: float
    ) -> None:
        """
        Establece el brillo global de la tira LED.

        Args:
            brillo (float): Nivel de brillo en el rango
                [0.0, 1.0].

        Returns:
            None
        """
        if 0 <= brillo <= 1:
            self.brillo = brillo

    def set_color(
        self,
        num: int,
        colors: tuple[int, int, int]
    ) -> None:
        """
        Establece el color de un LED específico.

        Args:
            num (int): Índice del LED.
            colors (tuple[int, int, int]): Color RGB donde cada
                componente está en el rango [0, 255].

        Returns:
            None
        """
        self.np[num] = self._apply_brillo(colors)
        self.np.write()

    def set_all(
        self,
        colors: tuple[int, int, int]
    ) -> None:
        """
        Establece el mismo color para todos los LEDs.

        Args:
            colors (tuple[int, int, int]): Color RGB donde cada
                componente está en el rango [0, 255].

        Returns:
            None
        """
        color = self._apply_brillo(colors)
        for i in range(self.num_leds):
            self.np[i] = color
        self.np.write()

    def off_all(self) -> None:
        """
        Apaga todos los LEDs de la tira.

        Returns:
            None
        """
        for i in range(self.num_leds):
            self.np[i] = (0, 0, 0)
        self.np.write()

    def on_sequencial(
        self,
        colors: tuple[int, int, int],
        time: float = 1.0
    ) -> None:
        """
        Enciende los LEDs secuencialmente.

        Los LEDs se encienden uno a uno hasta completar
        la tira.

        Args:
            colors (tuple[int, int, int]): Color RGB donde cada
                componente está en el rango [0, 255].
            time (float, optional): Tiempo total de la animación
                en segundos. Por defecto es 1.0.

        Returns:
            None
        """
        color = self._apply_brillo(colors)
        self.off_all()

        delay = time / self.num_leds
        for i in range(self.num_leds):
            self.np[i] = color
            self.np.write()
            sleep(delay)

    def off_sequencial(
        self,
        time: float = 1.0
    ) -> None:
        """
        Apaga los LEDs secuencialmente.

        Los LEDs se apagan uno a uno comenzando desde
        el último LED de la tira.

        Args:
            time (float, optional): Tiempo total de la animación
                en segundos. Por defecto es 1.0.

        Returns:
            None
        """
        delay = time / self.num_leds

        for i in range(self.num_leds - 1, -1, -1):
            self.np[i] = (0, 0, 0)
            self.np.write()
            sleep(delay)

from machine import Pin
import neopixel
from time import sleep

class WS2812B:
    def __init__(self, din_pin, num_leds, brillo=1.0):
        self.din = Pin(din_pin)
        self.num_leds = num_leds
        self.brillo = brillo  # 0.0 a 1.0
        self.np = neopixel.NeoPixel(self.din, self.num_leds)
        self.off_all()

    def _apply_brillo(self, colors):
        r, g, b = colors
        return (
            int(r * self.brillo),
            int(g * self.brillo),
            int(b * self.brillo)
        )

    def set_brillo(self, brillo):
        if 0 <= brillo <= 1:
            self.brillo = brillo

    def set_color(self, num, colors):
        self.np[num] = self._apply_brillo(colors)
        self.np.write()

    def set_all(self, colors):
        color = self._apply_brillo(colors)
        for i in range(self.num_leds):
            self.np[i] = color
        self.np.write()

    def off_all(self):
        for i in range(self.num_leds):
            self.np[i] = (0, 0, 0)
        self.np.write()
        
    def on_sequencial(self, colors, time=1.0):
        color = self._apply_brillo(colors)
        self.off_all()
        
        delay = time / self.num_leds
        for i in range(self.num_leds):
            self.np[i] = (color)
            self.np.write()
            sleep(delay)
            
    def off_sequencial(self, time=1.0):
        color = (0,0,0)
        
        delay = time / self.num_leds
        for i in range(self.num_leds-1, -1, -1):
            self.np[i] = (color)
            self.np.write()
            sleep(delay)





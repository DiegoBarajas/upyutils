import bluetooth
from ._ble_ import BLEUART

class BLE:
    """
    Controlador BLE UART para MicroPython.

    Permite enviar y recibir mensajes mediante Bluetooth Low Energy
    utilizando una interfaz basada en eventos.

    Example:
        >>> ble = BLEController("Kyber")

        >>> ble.add_event("ON", turn_on)
        >>> ble.add_event("OFF", turn_off)

        >>> ble.add_event("*", lambda msg: print(msg))
    """

    def __init__(self, name="ESP-32", log=True):
        """
        Inicializa el controlador BLE.

        Args:
            name (str, optional):
                Nombre que será visible al anunciar el dispositivo BLE.
                Defaults to "ESP-32".

            log (bool, optional):
                Habilita los mensajes de consola.
                Defaults to True.
        """
        self.name = name
        self.log = log

        self._ble = bluetooth.BLE()
        self._uart = BLEUART(self._ble, self.name)

        self._events = {}

        self._uart.irq(handler=self._irq_handler)

        self.console(f'Initialized as "{self.name}"')

    def send(self, message):
        """
        Envía un mensaje mediante BLE.

        Args:
            message (str | bytes):
                Mensaje a enviar.

        Raises:
            ValueError:
                Si el mensaje está vacío.
        """
        if not message:
            raise ValueError("[BLE] Message can't be empty")

        self._uart.write(message)

    def add_event(self, command, function):
        """
        Registra un callback para un comando.

        También puede utilizarse el comando '*'
        para recibir todos los mensajes.

        Args:
            command (str):
                Comando a escuchar.

            function (callable):
                Función que será ejecutada cuando se reciba el comando.

        Raises:
            TypeError:
                Si command no es una cadena o function no es callable.

        Example:
            >>> ble.add_event("ON", turn_on)
            >>> ble.add_event("*", logger)
        """
        if not isinstance(command, str):
            raise TypeError('[BLE] "command" must be a str')

        if not callable(function):
            raise TypeError('[BLE] "function" must be callable')

        self._events[command] = function

    def remove_event(self, command):
        """
        Elimina un evento registrado.

        Args:
            command (str):
                Comando a eliminar.
        """
        self._events.pop(command, None)

    def _irq_handler(self):
        """
        Manejador interno de recepción BLE.

        Formato soportado:

            COMMAND
            COMMAND arg1 arg2 arg3

        Examples:
            ON
            OFF
            COLOR 255 0 0
        """
        try:
            raw = self._uart.read()

            if not raw:
                return

            message = raw.decode().strip()

            if not message:
                return

            parts = message.split()

            command = parts[0]
            args = parts[1:]

            # Evento global
            if "*" in self._events:
                self._events["*"](message)

            # Evento específico
            if command in self._events:
                self._events[command](*args)

        except Exception as e:
            self.console("IRQ Error:", e)

    def console(self, *args):
        """
        Imprime mensajes de depuración.

        Args:
            *args:
                Argumentos a imprimir.
        """
        if self.log:
            print("[ BLE ]", *args)
import bluetooth
from __BLE__ import BLEUART

class BLEController:
    def __init__(self, name="ESP-32", log=True):
        self.name = name
        self.log = log
        
        self.__ble = bluetooth.BLE()
        self.__uart = BLEUART(self.__ble, self.name)
        
        self.__uart.irq(handler=self.__irq_handler)
        self.__events = { }
        
        self.console(f'Initialized as "{self.name}"')
    
    def send(self, message=None):
        if not message:
            raise Exception("[BLE] Message can't be empty")
        
        self.__uart.write(message)
        
    def add_event(self, command, function):
        if not isinstance(command, str):
            raise Exception('[BLE] "command" must be a str')
        
        self.__events[command] = function
        
    def __irq_handler(self):
        message = self.__uart.read().decode().strip()
        
        if "*" in self.__events:
            self.__events["*"](message)
            if message == "*": return
        if message in self.__events:
            self.__events[message]()
    
        
    def console(self, *args):
        if self.log:
            print("[ BLE ]", *args)

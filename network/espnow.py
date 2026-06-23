import network
import network.espnow as espnow

class ESPNow:
    """
    Administrador de comunicaciones ESP-NOW.

    Permite registrar dispositivos remotos (peers), enviar y
    recibir mensajes, así como gestionar alias para facilitar
    la identificación de cada dispositivo.

    Attributes:
        sta (network.WLAN): Interfaz WiFi en modo estación.
        e (espnow.ESPNow): Instancia principal de ESP-NOW.
        peers (dict[str, bytes]): Diccionario de alias y
            direcciones MAC asociadas.
    """
    def __init__(self) -> None:
        """
        Inicializa el controlador ESP-NOW.

        Activa automáticamente la interfaz WiFi y el protocolo
        ESP-NOW.

        Returns:
            None
        """
        self.sta = network.WLAN(network.STA_IF)
        self.e = espnow.ESPNow()
        self.peers = {}

        self.activate()

    def activate(self) -> None:
        """
        Activa la interfaz WiFi y ESP-NOW.

        Returns:
            None
        """
        self.sta.active(True)
        self.e.active(True)

    def deactivate(self) -> None:
        """
        Desactiva la interfaz WiFi y ESP-NOW.

        Returns:
            None
        """
        self.e.active(False)
        self.sta.active(False)

    def get_mac(self) -> bytes:
        """
        Obtiene la dirección MAC del dispositivo.

        Returns:
            bytes: Dirección MAC de la interfaz WiFi.
        """
        return self.sta.config("mac")

    def add_peer(
        self,
        peer_mac: bytes,
        alias: str | None = None
    ) -> None:
        """
        Registra un dispositivo remoto.

        Args:
            peer_mac (bytes): Dirección MAC del dispositivo.
            alias (str | None, optional): Nombre utilizado para
                identificar el dispositivo.

        Returns:
            None
        """
        try:
            self.e.add_peer(peer_mac)
        except OSError:
            pass

        if alias:
            self.peers[alias] = peer_mac

    def remove_peer(
        self,
        peer: str | bytes
    ) -> None:
        """
        Elimina un dispositivo registrado.

        Args:
            peer (str | bytes): Alias o dirección MAC del
                dispositivo.

        Returns:
            None
        """
        peer_mac = self._resolve_peer(peer)

        try:
            self.e.del_peer(peer_mac)
        except OSError:
            pass

    def send(
        self,
        peer: str | bytes,
        message: str | bytes
    ) -> None:
        """
        Envía un mensaje a un dispositivo remoto.

        Args:
            peer (str | bytes): Alias o dirección MAC del
                destinatario.
            message (str | bytes): Mensaje a enviar.

        Returns:
            None

        Raises:
            ValueError: Si el dispositivo no está registrado.
        """
        peer_mac = self._resolve_peer(peer)

        if isinstance(message, str):
            message = message.encode()

        self.e.send(peer_mac, message)

    def receive(
        self,
        timeout: int = 0
    ) -> tuple:
        """
        Recibe un mensaje ESP-NOW.

        Args:
            timeout (int, optional): Tiempo máximo de espera en
                milisegundos. Por defecto es 0.

        Returns:
            tuple: Tupla en formato (mac, mensaje).
        """
        return self.e.recv(timeout)

    def receive_text(
        self,
        timeout: int = 0
    ) -> tuple[bytes | None, str | bytes | None]:
        """
        Recibe un mensaje e intenta decodificarlo como texto.

        Args:
            timeout (int, optional): Tiempo máximo de espera en
                milisegundos. Por defecto es 0.

        Returns:
            tuple: Tupla en formato (mac, mensaje).

            - mac (bytes): Dirección MAC del remitente.
            - mensaje (str): Mensaje decodificado.
            - (None, None): Si no se recibió ningún mensaje.
        """
        mac, msg = self.receive(timeout)

        if msg is None:
            return None, None

        try:
            msg = msg.decode()
        except:
            pass

        return mac, msg
    
    
    def on_receive(
        self, 
        callback : function
    ) -> None:
        """
        Agrega una irq al recibir mensaje
        
        Args:
            callback (function): Funcion a ejecutar al caer la irq
            
        Returns:
            None
        """
        
        self._callback = callback
        self.e.irq(self._irq_handler)

    def _resolve_peer(
        self,
        peer: str | bytes
    ) -> bytes:
        """
        Resuelve un alias a su dirección MAC correspondiente.

        Args:
            peer (str | bytes): Alias o dirección MAC.

        Returns:
            bytes: Dirección MAC del dispositivo.

        Raises:
            ValueError: Si el alias no está registrado.
        """
        if isinstance(peer, bytes):
            return peer

        if peer in self.peers:
            return self.peers[peer]

        raise ValueError(
            "Peer '{}' no registrado".format(peer)
        )


    def _irq_handler(self, e):
        while True:
            mac, msg = e.recv(0)

            if mac is None:
                break

            if self._callback:
                self._callback(mac, msg)
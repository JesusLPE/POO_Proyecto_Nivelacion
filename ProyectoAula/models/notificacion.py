from datetime import datetime

class Notificacion:
    def __init__(self, mensaje: str, destinatario):
        self._mensaje = mensaje
        self._destinatario = destinatario
        self._fecha = datetime.now()
        self._leida = False

    def enviar(self):
        print(f"Enviando a {self._destinatario.email}: {self._mensaje}")

    def marcar_leida(self):
        self._leida = True

    @property
    def estado(self):
        return "leída" if self._leida else "no leída"
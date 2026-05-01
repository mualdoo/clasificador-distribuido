from backend.network.broadcast import enviar_broadcast

class BroadcastClient:
    def __init__(self, puerto_udp_red: int = 5556):
        """
        puerto_udp_red: Es el puerto en el que TODOS los nodos de la red local
        acordaron escuchar los mensajes de descubrimiento.
        """
        self.puerto_udp_red = puerto_udp_red

    def enviar_saludo(self, nodo_id: str, puerto_tcp_local: int, espacio_maximo: int, espacio_usado: int) -> bool:
        """
        Anuncia la presencia de este nodo a toda la red local.
        """
        payload = {
            "id": nodo_id,
            "puerto_tcp": puerto_tcp_local,
            "espacio_maximo": espacio_maximo,
            "espacio_usado": espacio_usado
        }
        return enviar_broadcast(self.puerto_udp_red, "saludo", payload)

    def enviar_despedida(self, nodo_id: str) -> bool:
        """
        Avisa a la red local que este nodo se va a desconectar.
        """
        payload = {
            "id": nodo_id
        }
        return enviar_broadcast(self.puerto_udp_red, "despedida", payload)
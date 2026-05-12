from backend.network.broadcast import enviar_broadcast
from backend.config import NODE_IP

class BroadcastClient:
    def __init__(self, puerto_udp_red: int = 5556):
        self.puerto_udp_red = puerto_udp_red

    def enviar_saludo(self, nodo_id: str, puerto_tcp_local: int, espacio_maximo: int, espacio_usado: int) -> bool:
        """
        Anuncia la presencia de este nodo a toda la red local.
        """
        payload = {
            "id": nodo_id,
            "puerto_tcp": puerto_tcp_local,
            "espacio_maximo": espacio_maximo,
            "espacio_usado": espacio_usado,
            "ip_nodo": NODE_IP,  # <--- Tu idea: inyectamos nuestra IP real explícitamente
        }
        return enviar_broadcast(self.puerto_udp_red, "saludo", payload)
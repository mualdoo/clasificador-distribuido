import socket
import threading
import json
import time
from src.config import UDP_PORT, NODE_IP, NODE_ID
from src.database.models import Nodo, db
from datetime import datetime

class DiscoveryService:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Permite que varios procesos en la misma PC usen el mismo puerto (útil para pruebas)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.running = True

    def start_listener(self):
        """Hilo que escucha anuncios UDP de otros nodos."""
        self.socket.bind(('', UDP_PORT))
        print(f"Escuchando anuncios en el puerto {UDP_PORT}...")
        
        while self.running:
            try:
                data, addr = self.socket.recvfrom(1024)
                message = json.loads(data.decode('utf-8'))
                
                # Ignorar mis propios mensajes
                if message.get('node_id') == NODE_ID:
                    continue
                
                if message.get('type') == 'HELLO':
                    self._register_node(message, addr[0])
                elif message.get('type') == 'BYE':
                    self._unregister_node(message)
                    
            except Exception as e:
                if self.running:
                    print(f"Error en listener UDP: {e}")

    def _register_node(self, data, ip):
        """Guarda o actualiza un nodo en la base de datos local."""
        try:
            with db.atomic():
                nodo, created = Nodo.get_or_create(
                    id=data['node_id'],
                    defaults={'direccion_ip': ip, 'ultima_conexion': datetime.now()}
                )
                if not created:
                    nodo.direccion_ip = ip
                    nodo.ultima_conexion = datetime.now()
                    nodo.save()
            
            action = "Nuevo nodo descubierto" if created else "Nodo actualizado"
            print(f"{action}: {data['node_id']} en {ip}")
        except Exception as e:
            print(f"Error al registrar nodo: {e}")

    def _unregister_node(self, data):
        """Elimina un nodo que avisó su desconexión."""
        try:
            query = Nodo.delete().where(Nodo.id == data['node_id'])
            query.execute()
            print(f"Nodo desconectado: {data['node_id']}")
        except Exception as e:
            print(f"Error al eliminar nodo: {e}")

    def announce_presence(self):
        """Envía un broadcast avisando que entramos a la red."""
        message = {
            "type": "HELLO",
            "node_id": NODE_ID,
            "ip": NODE_IP
        }
        self.socket.sendto(json.dumps(message).encode('utf-8'), ('255.255.255.255', UDP_PORT))

    def send_goodbye(self):
        """Avisa a la red antes de apagar el programa."""
        message = {
            "type": "BYE",
            "node_id": NODE_ID
        }
        self.socket.sendto(json.dumps(message).encode('utf-8'), ('255.255.255.255', UDP_PORT))
        self.running = False
        self.socket.close()

# Instancia global para ser usada en main.py
discovery = DiscoveryService()
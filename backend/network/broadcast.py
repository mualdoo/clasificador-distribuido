import socket
import json
import logging
from typing import Dict, Any

from backend.network.p2p import serializador_personalizado
from backend.config import NODE_IP

def iniciar_listener_broadcast(puerto: int, handler):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", puerto))
    
    logging.info(f"Escuchando descubrimientos (Broadcast UDP) en el puerto {puerto}...")

    while True:
        try:
            data, addr = sock.recvfrom(4096)
            mensaje_crudo = data.decode('utf-8')
            mensaje = json.loads(mensaje_crudo)
            
            if isinstance(mensaje, dict):
                if "payload" not in mensaje:
                    mensaje["payload"] = {}
                # Seguimos inyectando esto solo como "Plan B" por si acaso
                mensaje["payload"]["ip_origen_udp"] = addr[0]
            
            handler.procesar(mensaje)
            
        except json.JSONDecodeError:
            logging.warning(f"JSON inválido recibido por broadcast desde {addr[0]}")
        except Exception as e:
            logging.error(f"Error en listener de broadcast: {str(e)}")


def enviar_broadcast(puerto: int, tipo: str, payload: dict) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    # FORZAR SALIDA: Obligamos al SO a enviar el grito por nuestra interfaz real, no por VMware
    try:
        sock.bind((NODE_IP, 0))
    except Exception as e:
        logging.warning(f"No se pudo forzar el bind a {NODE_IP}. Usando interfaz por defecto: {e}")

    mensaje = {
        "tipo": tipo,
        "payload": payload
    }
    
    try:
        mensaje_str = json.dumps(mensaje, default=serializador_personalizado)
        sock.sendto(mensaje_str.encode('utf-8'), ('255.255.255.255', puerto))
        return True
    except Exception as e:
        logging.error(f"Error enviando paquete de broadcast: {str(e)}")
        return False
    finally:
        sock.close()
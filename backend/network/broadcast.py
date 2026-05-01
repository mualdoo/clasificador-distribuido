import socket
import json
import logging
from typing import Dict, Any

# Reutilizamos el serializador que configuraste antes para manejar UUIDs y Fechas
from backend.network.p2p import serializador_personalizado

def iniciar_listener_broadcast(puerto: int, handler):
    """
    Inicia un hilo/bucle infinito que escucha mensajes de broadcast UDP entrantes.
    """
    # Creamos el socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # SO_REUSEADDR permite que varios procesos locales escuchen en el mismo puerto 
    # (muy útil si haces pruebas con múltiples nodos en la misma computadora)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Escuchamos en todas las interfaces en el puerto especificado
    sock.bind(("", puerto))
    
    logging.info(f"Escuchando descubrimientos (Broadcast UDP) en el puerto {puerto}...")

    while True:
        try:
            # Esperamos un paquete (tamaño máximo de buffer 4096 bytes)
            data, addr = sock.recvfrom(4096)
            mensaje_crudo = data.decode('utf-8')
            mensaje = json.loads(mensaje_crudo)
            
            # TRUCO IMPORTANTE: En el descubrimiento P2P, el que recibe el mensaje 
            # necesita saber la IP del que lo envió para poder contactarlo por TCP después.
            # Inyectamos la IP de origen en el payload automáticamente.
            if isinstance(mensaje, dict):
                if "payload" not in mensaje:
                    mensaje["payload"] = {}
                mensaje["payload"]["ip_origen"] = addr[0]
            
            # Pasamos el mensaje al handler genérico.
            # Nota: No enviamos respuesta de vuelta. En UDP Broadcast, el handler 
            # se encargará de procesar la información de forma pasiva.
            handler.procesar(mensaje)
            
        except json.JSONDecodeError:
            logging.warning(f"JSON inválido recibido por broadcast desde {addr[0]}")
        except Exception as e:
            logging.error(f"Error en listener de broadcast: {str(e)}")


def enviar_broadcast(puerto: int, tipo: str, payload: dict) -> bool:
    """
    Envía un paquete UDP a toda la red local.
    Retorna True si se envió correctamente, False si hubo un error local.
    """
    # Creamos el socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Habilitamos explícitamente el permiso del SO para enviar mensajes de broadcast
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    mensaje = {
        "tipo": tipo,
        "payload": payload
    }
    
    try:
        # Serializamos usando la misma función que arregló tu problema de UUIDs
        mensaje_str = json.dumps(mensaje, default=serializador_personalizado)
        
        # 255.255.255.255 es la dirección IP universal para broadcast en tu subred actual
        sock.sendto(mensaje_str.encode('utf-8'), ('255.255.255.255', puerto))
        return True
    except Exception as e:
        logging.error(f"Error enviando paquete de broadcast: {str(e)}")
        return False
    finally:
        sock.close()
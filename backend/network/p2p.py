import zmq
import json
import logging
import uuid
import datetime
from typing import Tuple, Dict, Any
from backend.network.handler import MessageHandler
from backend.config import REQUEST_TIMEOUT, REQUEST_RETRIES

def serializador_personalizado(obj):
    """Le enseña a json.dumps cómo procesar UUIDs y Fechas."""
    if isinstance(obj, uuid.UUID):
        return str(obj)
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError(f"El tipo {type(obj)} no es serializable")
# ---------------------

def iniciar_listener(puerto: int, handler: MessageHandler):
    """
    Inicia un hilo/bucle infinito que escucha mensajes entrantes usando un socket REP (Reply).
    """
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://*:{puerto}")
    
    logging.info(f"Nodo escuchando en el puerto {puerto}...")

    while True:
        try:
            # Esperamos un mensaje
            mensaje_crudo = socket.recv_string()
            mensaje = json.loads(mensaje_crudo)
            
            # Pasamos el mensaje al handler genérico
            respuesta = handler.procesar(mensaje)
            
            # Devolvemos la respuesta (ACK) al nodo que nos envió el mensaje
            socket.send_string(json.dumps(respuesta, default=serializador_personalizado))
            
        except json.JSONDecodeError:
            socket.send_string(json.dumps({"status": "error", "error": "JSON inválido"}))
        except Exception as e:
            logging.error(f"Error en listener: {str(e)}")
            # En ZMQ REP/REQ, SIEMPRE debemos enviar una respuesta para no romper el ciclo
            socket.send_string(json.dumps({"status": "error", "error": "Error interno del nodo"}))


def enviar_mensaje(ip: str, puerto: int, tipo: str, payload: dict) -> Tuple[bool, Dict[str, Any]]:
    """
    Envía un mensaje usando un socket REQ (Request) con el patrón "Lazy Pirate" para reintentos.
    Retorna una tupla: (Exito: bool, Respuesta: dict)
    Si Exito es False, debes marcar el nodo como inactivo en tu base de datos.
    """
    context = zmq.Context()
    
    mensaje = {
        "tipo": tipo,
        "payload": payload
    }
    mensaje_str = json.dumps(mensaje, default=serializador_personalizado)
    endpoint = f"tcp://{ip}:{puerto}"

    socket = context.socket(zmq.REQ)
    socket.connect(endpoint)

    poll = zmq.Poller()
    poll.register(socket, zmq.POLLIN)

    intentos_restantes = REQUEST_RETRIES

    while intentos_restantes > 0:
        socket.send_string(mensaje_str)
        
        # Esperamos respuesta con timeout
        eventos = dict(poll.poll(REQUEST_TIMEOUT))
        
        if socket in eventos:
            # ¡El mensaje llegó y tenemos respuesta!
            respuesta_str = socket.recv_string()
            try:
                respuesta = json.loads(respuesta_str)
                socket.close()
                context.term()
                return True, respuesta
            except json.JSONDecodeError:
                socket.close()
                context.term()
                return False, {"error": "Respuesta inválida del nodo"}

        # Si llegamos aquí, hubo un timeout (el nodo no respondió)
        intentos_restantes -= 1
        logging.warning(f"Timeout al conectar con {endpoint}. Intentos restantes: {intentos_restantes}")

        # La regla de oro en ZMQ REQ/REP ante un error: cerrar el socket y recrearlo
        socket.setsockopt(zmq.LINGER, 0)
        socket.close()
        poll.unregister(socket)

        if intentos_restantes > 0:
            # Recreamos el socket para el siguiente intento
            socket = context.socket(zmq.REQ)
            socket.connect(endpoint)
            poll.register(socket, zmq.POLLIN)

    # Si se agotan los intentos
    context.term()
    return False, {"error": "El nodo está inactivo o inalcanzable"}
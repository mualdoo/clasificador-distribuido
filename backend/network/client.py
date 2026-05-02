import base64
from datetime import datetime
from typing import Tuple, Dict, Any
import logging

from backend.network.p2p import enviar_mensaje
from backend.services.io_service import IOService
from backend.services.services import NodoService

class P2PClient:
    def __init__(self):
        self.io_service = IOService()
        self.nodo_service = NodoService()

    def reportar_falla_nodo(self, ip_fallida: str, puerto: int):
        """Busca qué nodo tiene la IP que falló, lo desactiva y avisa a la red."""
        nodos_db = self.nodo_service.model.select().where(self.nodo_service.model.ip == ip_fallida)
        if not nodos_db.exists():
            return 
            
        nodo_caido = nodos_db.get()
        if not nodo_caido.activo:
            return

        logging.warning(f"Detectada caída del nodo {nodo_caido.id} ({ip_fallida}). Notificando a la red...")
        self.nodo_service.update(nodo_caido.id, activo=False)
        
        payload = {"nodo_id": str(nodo_caido.id)}
        nodos_amigos = self.nodo_service.model.select().where(
            (self.nodo_service.model.activo == True) & 
            (self.nodo_service.model.id != nodo_caido.id)
        )
        for nodo_amigo in nodos_amigos:
            enviar_mensaje(nodo_amigo.ip, puerto, "nodo_inactivo", payload)

    def _enviar_seguro(self, ip: str, puerto: int, tipo: str, payload: dict) -> Tuple[bool, Dict[str, Any]]:
        """
        Punto centralizado para enviar mensajes. 
        Maneja automáticamente el reporte de fallas si el nodo no responde.
        """
        exito, respuesta = enviar_mensaje(ip, puerto, tipo, payload)
        
        if not exito:
            self.reportar_falla_nodo(ip, puerto)
            
        return exito, respuesta

    def enviar_ping(self, ip: str, puerto: int) -> Tuple[bool, Dict[str, Any]]:
        return self._enviar_seguro(ip, puerto, "ping", {})

    def solicitar_cambios(self, ip: str, puerto: int, since_timestamp: datetime) -> Tuple[bool, Dict[str, Any]]:
        payload = {"timestamp": since_timestamp.isoformat()}
        return self._enviar_seguro(ip, puerto, "obtener_cambios", payload)

    def enviar_cambios(self, ip: str, puerto: int, cambios_dict: dict) -> Tuple[bool, Dict[str, Any]]:
        payload = {"cambios": cambios_dict}
        return self._enviar_seguro(ip, puerto, "recibir_cambios", payload)

    def sincronizar_usuario(self, ip: str, puerto: int, usuario_dict: dict) -> Tuple[bool, Dict[str, Any]]:
        payload = {"usuario": usuario_dict}
        return self._enviar_seguro(ip, puerto, "guardar_usuario", payload)

    def eliminar_usuario_remoto(self, ip: str, puerto: int, usuario_id: str) -> Tuple[bool, Dict[str, Any]]:
        payload = {"usuario_id": str(usuario_id)}
        return self._enviar_seguro(ip, puerto, "eliminar_usuario", payload)

    def sincronizar_metadatos_archivo(self, ip: str, puerto: int, archivo_dict: dict, ubicaciones_list: list) -> Tuple[bool, Dict[str, Any]]:
        payload = {
            "archivo": archivo_dict,
            "ubicaciones": ubicaciones_list
        }
        return self._enviar_seguro(ip, puerto, "guardar_metadatos_archivo", payload)

    def enviar_archivo_desde_memoria(self, ip: str, puerto: int, archivo_dict: dict, ubicaciones_list: list, contenido_bytes: bytes) -> Tuple[bool, Dict[str, Any]]:
        try:
            contenido_b64 = base64.b64encode(contenido_bytes).decode('utf-8')
            payload = {
                "archivo": archivo_dict,
                "ubicaciones": ubicaciones_list,
                "contenido_b64": contenido_b64
            }
            return self._enviar_seguro(ip, puerto, "guardar_archivo", payload)
        except Exception as e:
            return False, {"error": f"Error local: {str(e)}"}

    def eliminar_archivo_remoto(self, ip: str, puerto: int, usuario_id: str, archivo_id: str) -> Tuple[bool, Dict[str, Any]]:
        payload = {
            "usuario_id": str(usuario_id),
            "archivo_id": str(archivo_id)
        }
        return self._enviar_seguro(ip, puerto, "eliminar_archivo", payload)

    def solicitar_descarga_archivo(self, ip: str, puerto: int, usuario_id: str, archivo_id: str) -> Tuple[bool, Dict[str, Any]]:
        payload = {
            "usuario_id": str(usuario_id),
            "archivo_id": str(archivo_id)
        }
        
        exito, respuesta = self._enviar_seguro(ip, puerto, "enviar_archivo", payload)
        
        if exito and respuesta.get("status") == "ok":
            try:
                contenido_b64 = respuesta.get("contenido_b64")
                if not contenido_b64:
                    return False, {"error": "El nodo no incluyó el contenido Base64"}
                
                contenido_bytes = base64.b64decode(contenido_b64)
                del respuesta["contenido_b64"]
                respuesta["contenido_bytes"] = contenido_bytes
                
                return True, respuesta
            except Exception as e:
                return False, {"error": f"Fallo al decodificar: {str(e)}"}
                
        return exito, respuesta
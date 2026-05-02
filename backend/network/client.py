import base64
from datetime import datetime
from typing import Tuple, Dict, Any

from backend.network.p2p import enviar_mensaje
from backend.services.io_service import IOService

class P2PClient:
    def __init__(self):
        # Instanciamos el servicio IO por si necesitamos leer/guardar archivos
        # al enviarlos o recibirlos
        self.io_service = IOService()

    def enviar_ping(self, ip: str, puerto: int) -> Tuple[bool, Dict[str, Any]]:
        """Verifica si un nodo remoto está activo."""
        return enviar_mensaje(ip, puerto, "ping", {})
    
    def enviar_cambios(self, ip: str, puerto: int, cambios_dict: dict) -> Tuple[bool, Dict[str, Any]]:
        """
        Envía proactivamente un diccionario consolidado de registros a otro nodo.
        Espera el mismo formato que retorna 'obtener_cambios' 
        (ej: {"usuarios": [...], "archivos": [...]}).
        """
        payload = {
            "cambios": cambios_dict
        }
        return enviar_mensaje(ip, puerto, "recibir_cambios", payload)

    def solicitar_cambios(self, ip: str, puerto: int, since_timestamp: datetime) -> Tuple[bool, Dict[str, Any]]:
        """
        Pide al nodo remoto todos los registros modificados desde una fecha.
        Convierte el objeto datetime de Python a string ISO 8601.
        """
        payload = {
            "timestamp": since_timestamp.isoformat()
        }
        return enviar_mensaje(ip, puerto, "obtener_cambios", payload)

    def sincronizar_usuario(self, ip: str, puerto: int, usuario_dict: dict) -> Tuple[bool, Dict[str, Any]]:
        """Envía los datos de un usuario para que se guarden o actualicen en el nodo remoto."""
        payload = {
            "usuario": usuario_dict
        }
        return enviar_mensaje(ip, puerto, "guardar_usuario", payload)

    def eliminar_usuario_remoto(self, ip: str, puerto: int, usuario_id: str) -> Tuple[bool, Dict[str, Any]]:
        """Ordena a un nodo remoto que aplique la eliminación (soft y hard) de un usuario."""
        payload = {
            "usuario_id": str(usuario_id)
        }
        return enviar_mensaje(ip, puerto, "eliminar_usuario", payload)

    def sincronizar_metadatos_archivo(self, ip: str, puerto: int, archivo_dict: dict, ubicaciones_list: list) -> Tuple[bool, Dict[str, Any]]:
        payload = {
            "archivo": archivo_dict,
            "ubicaciones": ubicaciones_list # Cambiado a lista
        }
        return enviar_mensaje(ip, puerto, "guardar_metadatos_archivo", payload)

    def enviar_archivo_desde_memoria(self, ip: str, puerto: int, archivo_dict: dict, ubicaciones_list: list, contenido_bytes: bytes) -> Tuple[bool, Dict[str, Any]]:
        try:
            contenido_b64 = base64.b64encode(contenido_bytes).decode('utf-8')
            payload = {
                "archivo": archivo_dict,
                "ubicaciones": ubicaciones_list, # Cambiado a lista
                "contenido_b64": contenido_b64
            }
            return enviar_mensaje(ip, puerto, "guardar_archivo", payload)
        except Exception as e:
            return False, {"error": f"Error local: {str(e)}"}

    def solicitar_descarga_archivo(self, ip: str, puerto: int, usuario_id: str, archivo_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Pide a un nodo remoto que le envíe un archivo. 
        Retorna el archivo decodificado en memoria (bytes) para que la capa superior 
        (ej. API o Frontend) decida cómo entregarlo al usuario final.
        """
        payload = {
            "usuario_id": str(usuario_id),
            "archivo_id": str(archivo_id)
        }
        
        exito, respuesta = enviar_mensaje(ip, puerto, "enviar_archivo", payload)
        
        # Si la comunicación fue exitosa y el receptor encontró el archivo
        if exito and respuesta.get("status") == "ok":
            try:
                contenido_b64 = respuesta.get("contenido_b64")
                if not contenido_b64:
                    return False, {"error": "El nodo respondió OK pero no incluyó el contenido Base64"}
                
                # Decodificamos a bytes para mantenerlo solo en memoria RAM
                contenido_bytes = base64.b64decode(contenido_b64)
                
                # Eliminamos el string Base64 pesado y lo reemplazamos por los bytes puros
                del respuesta["contenido_b64"]
                respuesta["contenido_bytes"] = contenido_bytes
                respuesta["mensaje"] = "Archivo recibido y decodificado en memoria con éxito."
                
                return True, respuesta
                
            except Exception as e:
                return False, {"error": f"Fallo al decodificar el archivo recibido: {str(e)}"}
                
        # Si falló la comunicación o el nodo devolvió un error
        return exito, respuesta

    def eliminar_archivo_remoto(self, ip: str, puerto: int, usuario_id: str, archivo_id: str) -> Tuple[bool, Dict[str, Any]]:
        """Ordena a un nodo remoto que elimine un archivo (DB y físico)."""
        payload = {
            "usuario_id": str(usuario_id),
            "archivo_id": str(archivo_id)
        }
        return enviar_mensaje(ip, puerto, "eliminar_archivo", payload)
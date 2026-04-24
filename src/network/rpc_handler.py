# Servidor JSON-RPC (Métodos remotos)import base64
import base64
import os
from jsonrpcserver import method, dispatch, Result, Success, Error
from src.database.models import Usuario, Archivo, Nodo, db
from src.config import STORAGE_PATH, NODE_ID

@method
def ping() -> Result:
    """Responde para confirmar que el nodo está en línea."""
    return Success("pong")

@method
def replicate_user(user_data) -> Result:
    """Guarda un usuario replicado desde otro nodo."""
    try:
        with db.atomic():
            Usuario.get_or_create(
                id=user_data['id'],
                defaults={
                    'username': user_data['username'],
                    'password': user_data['password'],
                    'intereses': user_data['intereses'],
                    'rol': user_data.get('rol', 'user')
                }
            )
        return Success(True)
    except Exception as e:
        return Error(1, f"Error al replicar usuario: {str(e)}")

@method
def replicate_file_metadata(file_data) -> Result:
    """Guarda los metadatos de un archivo subido en la red."""
    try:
        with db.atomic():
            # Primero aseguramos que el nodo dueño existe en nuestra DB
            nodo_dueno, _ = Nodo.get_or_create(id=file_data['nodo_id'], defaults={'direccion_ip': file_data['ip']})
            
            Archivo.get_or_create(
                id=file_data['id'],
                defaults={
                    'nombre': file_data['nombre'],
                    'clasificacion': file_data['clasificacion'],
                    'confianza': file_data['confianza'],
                    'ubicacion_nodo_id': nodo_dueno,
                    'ruta_relativa': file_data['ruta_relativa'],
                    'propietario': file_data['propietario_id']
                }
            )
        return Success(True)
    except Exception as e:
        return Error(2, f"Error al replicar metadatos: {str(e)}")

@method
def get_file_content(file_uuid) -> Result:
    """Lee un archivo local y lo envía en Base64."""
    try:
        archivo = Archivo.get_by_id(file_uuid)
        # Solo enviamos si el archivo está físicamente en ESTE nodo
        if str(archivo.ubicacion_nodo_id) != NODE_ID:
            return Error(3, "El archivo no se encuentra físicamente en este nodo.")

        file_path = os.path.join(STORAGE_PATH, archivo.ruta_relativa)
        with open(file_path, "rb") as f:
            encoded_content = base64.b64encode(f.read()).decode('utf-8')
        
        return Success(encoded_content)
    except Exception as e:
        return Error(4, f"Error al leer archivo: {str(e)}")

def handle_rpc_request(request_data):
    """Punto de entrada para procesar el JSON-RPC."""
    return dispatch(request_data)
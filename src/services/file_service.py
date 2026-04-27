import os
import base64
from src.config import STORAGE_PATH, NODE_ID
from src.database.models import Nodo, Archivo, db
from src.network.messenger import send_rpc

class FileService:
    @staticmethod
    def save_local_file(file_bytes, metadata):
        """Guarda el archivo físicamente en el disco de este nodo."""
        full_path = os.path.join(STORAGE_PATH, metadata['ruta_relativa'])
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, "wb") as f:
            f.write(file_bytes)
        return True

    @staticmethod
    def choose_nodes_for_storage(exclude_node_id=None):
        """
        Selecciona los mejores nodos para guardar el archivo y su réplica.
        Criterio: Nodos con más espacio disponible o selección aleatoria.
        """
        nodos = list(Nodo.select().where(Nodo.id != exclude_node_id))
        
        # Necesitamos al menos un nodo para el original y otro para la réplica
        if len(nodos) < 1:
            return [NODE_ID], [] # Todo local si no hay nadie más
        
        # En un sistema real, aquí ordenarías por 'espacio_disponible'
        # Por ahora, tomamos los primeros dos disponibles
        primary = nodos[0]
        replica = nodos[1] if len(nodos) > 1 else None
        
        return primary, replica

file_service = FileService()
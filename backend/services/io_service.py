import os
from backend.config import STORAGE_DIR

class IOService:
    
    def _get_user_dir(self, usuario_id: str) -> str:
        """
        Genera la ruta del usuario y crea la carpeta si no existe.
        Ejemplo: backend/storage/123e4567-e89b-12d3.../
        """
        # Aseguramos que usuario_id sea string por si llega como objeto UUID
        user_dir = os.path.join(STORAGE_DIR, str(usuario_id))
        
        # exist_ok=True evita que lance error si la carpeta ya estaba creada
        os.makedirs(user_dir, exist_ok=True)
        return user_dir

    def _get_file_path(self, usuario_id: str, archivo_id: str) -> str:
        """
        Construye la ruta absoluta segura hacia el archivo físico.
        """
        user_dir = self._get_user_dir(usuario_id)
        # Evitamos ataques de Path Traversal limpiando el nombre por si acaso
        safe_file_name = os.path.basename(str(archivo_id))
        return os.path.join(user_dir, safe_file_name)

    def guardar_archivo(self, usuario_id: str, archivo_id: str, contenido_bytes: bytes) -> int:
        """
        Guarda los bytes en el disco y retorna el tamaño guardado.
        Ideal para actualizar el campo 'tamano_bytes' y el espacio del nodo.
        """
        file_path = self._get_file_path(usuario_id, archivo_id)
        
        with open(file_path, 'wb') as f:
            f.write(contenido_bytes)
            
        # Retornamos el tamaño real que ocupó en disco
        return os.path.getsize(file_path)

    def leer_archivo(self, usuario_id: str, archivo_id: str) -> bytes:
        """
        Lee el archivo físico del disco y lo retorna en bytes.
        """
        file_path = self._get_file_path(usuario_id, archivo_id)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"El archivo {archivo_id} no existe en el almacenamiento del usuario.")
            
        with open(file_path, 'rb') as f:
            return f.read()

    def eliminar_archivo(self, usuario_id: str, archivo_id: str) -> bool:
        """
        Elimina el archivo físico del disco.
        Retorna True si se eliminó, False si no existía.
        """
        file_path = self._get_file_path(usuario_id, archivo_id)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            # Opcional: Si quieres limpiar la carpeta del usuario cuando quede vacía
            # self._limpiar_carpeta_si_vacia(self._get_user_dir(usuario_id))
            return True
        return False

    def _limpiar_carpeta_si_vacia(self, user_dir: str):
        """
        Utilidad opcional: Borra la carpeta del usuario si ya no tiene archivos,
        para no dejar basura en el disco duro.
        """
        if os.path.exists(user_dir) and not os.listdir(user_dir):
            os.rmdir(user_dir)
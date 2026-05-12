import bcrypt
from backend.services.base import BaseService
from backend.db.models import Nodo, Usuario, Archivo, UbicacionArchivo

class NodoService(BaseService):
    def __init__(self):
        super().__init__(Nodo)

    def actualizar_espacio(self, nodo_id: str, tamano_bytes: int, sumar: bool = True):
        """Suma o resta espacio usado a un nodo y guarda el cambio."""
        nodo = self.model.get_or_none(self.model.id == nodo_id)
        if not nodo:
            return

        if sumar:
            nodo.espacio_usado += tamano_bytes
        else:
            # max(0, ...) evita que por algún bug de red el espacio sea negativo
            nodo.espacio_usado = max(0, nodo.espacio_usado - tamano_bytes)
            
        nodo.save()

class ArchivoService(BaseService):
    def __init__(self):
        super().__init__(Archivo)

class UbicacionArchivoService(BaseService):
    def __init__(self):
        super().__init__(UbicacionArchivo)

class UsuarioService(BaseService):
    def __init__(self):
        super().__init__(Usuario)

    def _hash_password(self, password: str) -> str:
        """Genera un hash seguro usando bcrypt."""
        # bcrypt requiere bytes, así que codificamos el string
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        # Lo decodificamos a string para guardarlo en la BD
        return hashed.decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica si una contraseña en texto plano coincide con el hash."""
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )

    def _format_in(self, data):
        """Pre-procesa los datos antes de guardarlos (Array -> String)."""
        processed_data = data.copy()
        if 'intereses' in processed_data and isinstance(processed_data['intereses'], list):
            processed_data['intereses'] = ','.join(processed_data['intereses'])
        return processed_data

    def _to_dict(self, instance):
        """Post-procesa los datos al sacarlos de la BD (String -> Array)."""
        data = super()._to_dict(instance)
        if data and 'intereses' in data:
            if data['intereses']:
                data['intereses'] = data['intereses'].split(',')
            else:
                data['intereses'] = []
        return data

    def create(self, is_sync=False, **data):
        formatted_data = self._format_in(data)
        
        # Lógica para evitar el doble hash en la replicación
        if 'contrasena' in formatted_data:
            if not is_sync:
                # Es un registro local, necesitamos hashear
                formatted_data['contrasena'] = self._hash_password(formatted_data['contrasena'])
            # Si is_sync es True, confiamos en que ya viene hasheada del otro nodo y no hacemos nada
            
        return super().create(is_sync=is_sync, **formatted_data)

    def update(self, pk_id, is_sync=False, **data):
        formatted_data = self._format_in(data)
        
        # Aplicamos la misma regla si están actualizando la contraseña
        if 'contrasena' in formatted_data and not is_sync:
            formatted_data['contrasena'] = self._hash_password(formatted_data['contrasena'])
            
        return super().update(pk_id, is_sync=is_sync, **formatted_data)
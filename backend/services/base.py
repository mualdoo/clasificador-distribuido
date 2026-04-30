from playhouse.shortcuts import model_to_dict

class BaseService:
    def __init__(self, model):
        self.model = model

    def _to_dict(self, instance):
        """Convierte la instancia del modelo a un diccionario de Python."""
        if not instance:
            return None
        return model_to_dict(instance)

    def get_one(self, pk_id):
        try:
            instance = self.model.get_by_id(pk_id)
            # Evitar retornar elementos con soft-delete mediante get_one
            if instance.deleted_at:
                return None
            return self._to_dict(instance)
        except self.model.DoesNotExist:
            return None

    def get_all(self, since_timestamp=None):
        query = self.model.select()
        
        if since_timestamp:
            # Sincronización: Trae creados, editados o borrados (soft-delete) después del timestamp
            query = query.where(
                (self.model.created_at >= since_timestamp) |
                (self.model.edited_at >= since_timestamp) |
                (self.model.deleted_at >= since_timestamp)
            )
        else:
            # Consulta normal: Ocultar los elementos con soft-delete
            query = query.where(self.model.deleted_at.is_null())

        return [self._to_dict(item) for item in query]

    def create(self, **data):
        instance = self.model.create(**data)
        return self._to_dict(instance)

    def update(self, pk_id, **data):
        try:
            instance = self.model.get_by_id(pk_id)
            if instance.deleted_at:
                return None # Bloquear la edición de elementos "borrados"
            
            # Actualizar campos
            for key, value in data.items():
                setattr(instance, key, value)
            
            instance.save() # El save() del modelo ya actualiza edited_at
            return self._to_dict(instance)
        except self.model.DoesNotExist:
            return None

    def delete(self, pk_id):
        try:
            instance = self.model.get_by_id(pk_id)
            # Evitar aplicar delete sobre algo ya borrado
            if not instance.deleted_at:
                instance.delete_instance()
            return True
        except self.model.DoesNotExist:
            return False
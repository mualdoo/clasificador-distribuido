import datetime
from peewee import Model, DateTimeField, Proxy

# Proxy para la base de datos SQLite
db_proxy = Proxy()

class BaseModel(Model):
    created_at = DateTimeField(default=datetime.datetime.now)
    edited_at = DateTimeField(default=datetime.datetime.now)
    deleted_at = DateTimeField(null=True)

    class Meta:
        database = db_proxy

    def save(self, *args, **kwargs):
        # Actualización automática de la fecha de edición
        self.edited_at = datetime.datetime.now()
        return super(BaseModel, self).save(*args, **kwargs)

    def delete_instance(self, recursive=False, delete_nullable=False):
        # Implementación de soft-delete
        self.deleted_at = datetime.datetime.now()
        return self.save()
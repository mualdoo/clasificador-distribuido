import uuid
from peewee import (
    CharField, 
    BooleanField, 
    FloatField, 
    ForeignKeyField, 
    UUIDField, 
    DateTimeField, 
    BigIntegerField
)
from backend.db.base import BaseModel

class Nodo(BaseModel):
    # ID como dirección MAC (XX:XX:XX:XX:XX:XX)
    id = CharField(primary_key=True, max_length=17)
    ip = CharField()
    # Limite máximo, ej: 104857600 (100MB en bytes)
    espacio_maximo = BigIntegerField(default=104857600) 
    # Lo que llevamos ocupado. Espacio disponible = maximo - usado
    espacio_usado = BigIntegerField(default=0)
    activo = BooleanField(default=True)
    ultima_conexion = DateTimeField()

    @property
    def espacio_disponible(self):
        # Propiedad calculada al vuelo en Python, no en la BD
        return self.espacio_maximo - self.espacio_usado

class Usuario(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    nombre = CharField()
    contrasena = CharField()
    rol = CharField()  # 'usuario' o 'admin'
    # Almacena array como string (ej: "linux,p2p,python")
    intereses = CharField(null=True)

class Archivo(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    nombre = CharField()
    categoria = CharField()
    subcategoria = CharField()
    confianza = FloatField()
    # Nuevo campo: vital para saber cuánto transferir sin ir al disco
    tamano_bytes = BigIntegerField() 
    propietario = ForeignKeyField(Usuario, backref='archivos')

class UbicacionArchivo(BaseModel):
    nodo = ForeignKeyField(Nodo, backref='ubicaciones')
    archivo = ForeignKeyField(Archivo, backref='nodos')
    es_replica = BooleanField(default=False)

    class Meta:
        table_name = 'ubicacion_archivo'
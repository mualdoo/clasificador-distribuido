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
    # Espacio en bytes, usando BigInteger para prevenir desbordamientos futuros
    espacio_disponible = BigIntegerField()
    activo = BooleanField(default=True)
    ultima_conexion = DateTimeField()

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
    propietario = ForeignKeyField(Usuario, backref='archivos')

class UbicacionArchivo(BaseModel):
    nodo = ForeignKeyField(Nodo, backref='ubicaciones')
    archivo = ForeignKeyField(Archivo, backref='nodos')
    es_replica = BooleanField(default=False)

    class Meta:
        table_name = 'ubicacion_archivo'
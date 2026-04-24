from peewee import *
from src.config import DB_PATH
import uuid

# Definición de la base de datos SQLite
db = SqliteDatabase(DB_PATH)

class BaseModel(Model):
    class Meta:
        database = db

class Nodo(BaseModel):
    # Usamos la MAC o el UUID generado en config
    id = CharField(primary_key=True) 
    direccion_ip = CharField()
    espacio_total = FloatField(default=0.0)      # En MB
    espacio_disponible = FloatField(default=0.0) # En MB
    ultima_conexion = TimestampField()

class Usuario(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    username = CharField(unique=True)
    password = CharField() # Recuerden usar hashing (ej. bcrypt) en el futuro
    rol = CharField(default="user") # 'admin' o 'user'
    intereses = TextField() # Guardaremos las categorías como "IA, Redes, Programacion"

class Archivo(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    nombre = CharField()
    clasificacion = CharField()      # Categoría ganadora (ej. "IA")
    confianza = FloatField()         # El % que dio Ollama (ej. 0.85)
    
    # Ubicación física del archivo
    ubicacion_nodo_id = ForeignKeyField(Nodo, backref='archivos') 
    ruta_relativa = CharField()      # Ruta dentro de data/library/
    
    # Usuario que lo subió
    propietario = ForeignKeyField(Usuario, backref='mis_archivos')

def init_db():
    """Crea las tablas si no existen"""
    db.connect()
    db.create_tables([Nodo, Usuario, Archivo])
    db.close()

if __name__ == "__main__":
    init_db()
    print("Base de datos e hilos de persistencia inicializados.")
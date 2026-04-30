from peewee import SqliteDatabase
from backend.config import DATABASE_PATH
from backend.db.base import db_proxy
from backend.db.models import Nodo, Usuario, Archivo, UbicacionArchivo

def inicializar_bd():
    """
    Inicializa la conexión a la base de datos y crea las tablas necesarias.
    """
    # 1. Creamos la instancia de la base de datos de SQLite usando tu ruta
    db = SqliteDatabase(DATABASE_PATH)
    
    # 2. Inicializamos el proxy con la base de datos real
    db_proxy.initialize(db)
    
    # 3. Nos conectamos y creamos las tablas
    db.connect()
    
    # create_tables crea las tablas solo si no existen (safe=True por defecto)
    db.create_tables([Nodo, Usuario, Archivo, UbicacionArchivo])
    
    print(f"Base de datos inicializada correctamente en: {DATABASE_PATH}")
    
    # Cerramos la conexión al terminar la inicialización
    db.close()

if __name__ == "__main__":
    # Si ejecutas este archivo directamente (python -m backend.db.init_db), 
    # se inicializará la base de datos.
    inicializar_bd()
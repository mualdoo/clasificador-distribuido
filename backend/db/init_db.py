import logging
from peewee import SqliteDatabase
from backend.config import DATABASE_PATH
from backend.db.base import db_proxy
from backend.db.models import Nodo, Usuario, Archivo, UbicacionArchivo

def inicializar_bd():
    """
    Inicializa la conexión, crea las tablas y asegura la existencia de un administrador.
    """
    # 1. Configuración de la instancia de SQLite
    db = SqliteDatabase(DATABASE_PATH)
    
    # 2. Inicialización del proxy (vincula los modelos a esta base de datos)
    db_proxy.initialize(db)
    
    # 3. Conexión y creación de tablas
    db.connect()
    # safe=True evita errores si las tablas ya existen
    db.create_tables([Nodo, Usuario, Archivo, UbicacionArchivo], safe=True)
    
    logging.info(f"Base de datos inicializada en: {DATABASE_PATH}")

    # 4. Sembrado (Seeding) del Administrador
    # Importamos el servicio aquí para evitar importaciones circulares
    from backend.services.services import UsuarioService
    usuario_service = UsuarioService()

    # Verificamos si ya existe algún administrador
    admin_existe = Usuario.select().where(Usuario.rol == 'admin').exists()

    if not admin_existe:
        logging.info("No se detectó un administrador. Creando credenciales por defecto...")
        try:
            usuario_service.create(
                nombre="admin",
                contrasena="admin123",
                rol="admin",
                intereses=["administración", "sistemas"]
            )
            logging.info("Usuario administrador creado exitosamente (admin / admin123)")
        except Exception as e:
            logging.error(f"Error al crear el administrador inicial: {e}")
    else:
        logging.info("El usuario administrador ya existe en el sistema.")

    # 5. Cerramos la conexión inicial
    db.close()
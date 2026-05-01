import base64
import logging
from datetime import datetime
from backend.services.services import UsuarioService, ArchivoService, UbicacionArchivoService, NodoService
from backend.services.io_service import IOService
from backend.db.models import Archivo, UbicacionArchivo # Necesarios para consultas directas de relaciones

# Inicialización de servicios
usuario_service = UsuarioService()
archivo_service = ArchivoService()
ubicacion_service = UbicacionArchivoService()
nodo_service = NodoService()
io_service = IOService()

def handle_ping(payload: dict) -> dict:
    """Responde a un ping básico para verificar que el nodo está vivo."""
    return {"mensaje": "pong"}

def handle_recibir_cambios(payload: dict) -> dict:
    """Procesa un paquete de cambios empujado proactivamente por otro nodo."""
    cambios = payload.get("cambios", {})
    estadisticas = {"usuarios": 0, "nodos": 0, "archivos": 0, "ubicaciones": 0}

    # 1. Procesar Usuarios
    for u in cambios.get("usuarios", []):
        if usuario_service.model.select().where(usuario_service.model.id == u['id']).exists():
            usuario_service.update(u['id'], is_sync=True, **u)
        else:
            usuario_service.create(is_sync=True, **u)
        estadisticas["usuarios"] += 1

    # 2. Procesar Nodos
    for n in cambios.get("nodos", []):
        if nodo_service.model.select().where(nodo_service.model.id == n['id']).exists():
            nodo_service.update(n['id'], is_sync=True, **n)
        else:
            nodo_service.create(is_sync=True, **n)
        estadisticas["nodos"] += 1

    # 3. Procesar Archivos (Solo metadatos, el contenido físico debe pedirse aparte si interesa)
    for a in cambios.get("archivos", []):
        if archivo_service.model.select().where(archivo_service.model.id == a['id']).exists():
            archivo_service.update(a['id'], is_sync=True, **a)
        else:
            archivo_service.create(is_sync=True, **a)
        estadisticas["archivos"] += 1

    # 4. Procesar Ubicaciones
    for ubi in cambios.get("ubicaciones", []):
        if ubicacion_service.model.select().where(ubicacion_service.model.id == ubi['id']).exists():
            ubicacion_service.update(ubi['id'], is_sync=True, **ubi)
        else:
            ubicacion_service.create(is_sync=True, **ubi)
        estadisticas["ubicaciones"] += 1

    return {"status": "ok", "mensaje": "Cambios integrados exitosamente", "procesados": estadisticas}

def handle_obtener_cambios(payload: dict) -> dict:
    """
    Devuelve un diccionario consolidado con todas las tablas modificadas
    desde un timestamp específico.
    """
    timestamp_str = payload.get("timestamp")
    if not timestamp_str:
        return {"error": "Se requiere un timestamp"}
        
    try:
        # Asumiendo que mandas el timestamp en formato ISO (ej. 2023-10-25T14:30:00)
        since = datetime.fromisoformat(timestamp_str)
    except ValueError:
        return {"error": "Formato de timestamp inválido. Usa ISO 8601."}

    # Recopilamos todos los cambios usando la función get_all modificada
    cambios = {
        "usuarios": usuario_service.get_all(since_timestamp=since),
        "nodos": nodo_service.get_all(since_timestamp=since),
        "archivos": archivo_service.get_all(since_timestamp=since),
        "ubicaciones": ubicacion_service.get_all(since_timestamp=since)
    }
    return cambios

def handle_guardar_usuario(payload: dict) -> dict:
    """Guarda o actualiza un usuario que viene de otro nodo (is_sync=True)."""
    datos = payload.get("usuario", {})
    user_id = datos.get("id")
    
    if not user_id:
        return {"error": "Datos de usuario incompletos"}

    # Intentamos obtener el usuario (incluso si está soft-deleted, Peewee lanzará error 
    # si intentamos crear uno con el mismo ID, así que revisamos existencia cruda)
    existe = usuario_service.model.select().where(usuario_service.model.id == user_id).exists()
    
    if existe:
        usuario_service.update(user_id, is_sync=True, **datos)
    else:
        usuario_service.create(is_sync=True, **datos)
        
    return {"status": "ok", "mensaje": "Usuario sincronizado"}

def handle_eliminar_usuario(payload: dict) -> dict:
    """
    Soft-delete del usuario, soft-delete de sus archivos y ubicaciones, 
    y hard-delete de los archivos físicos.
    """
    usuario_id = payload.get("usuario_id")
    if not usuario_id:
        return {"error": "Falta usuario_id"}

    # 1. Buscar todos los archivos del usuario
    archivos = Archivo.select().where(Archivo.propietario == usuario_id)
    
    for archivo in archivos:
        # 2. Soft-delete de TODAS las ubicaciones de este archivo
        ubicaciones = UbicacionArchivo.select().where(UbicacionArchivo.archivo == archivo.id)
        for ubi in ubicaciones:
            ubicacion_service.delete(ubi.id)
            
        # 3. Hard-delete físico
        io_service.eliminar_archivo(usuario_id, str(archivo.id))
        
        # 4. Soft-delete del archivo en BD
        archivo_service.delete(archivo.id)

    # 5. Soft-delete del usuario
    exito = usuario_service.delete(usuario_id)
    
    if exito:
        return {"status": "ok", "mensaje": "Usuario y dependencias eliminadas"}
    return {"error": "Usuario no encontrado"}

def handle_guardar_metadatos_archivo(payload: dict) -> dict:
    """Guarda información del archivo y su ubicación SIN el archivo físico."""
    datos_archivo = payload.get("archivo")
    datos_ubi = payload.get("ubicacion")
    
    if not datos_archivo or not datos_ubi:
        return {"error": "Faltan datos del archivo o ubicación"}

    archivo_id = datos_archivo.get("id")
    
    # Upsert del archivo
    if Archivo.select().where(Archivo.id == archivo_id).exists():
        archivo_service.update(archivo_id, **datos_archivo)
    else:
        archivo_service.create(**datos_archivo)

    # Upsert de la ubicación (Asumimos que el ID de ubicación viene en el payload)
    ubi_id = datos_ubi.get("id")
    if ubi_id and UbicacionArchivo.select().where(UbicacionArchivo.id == ubi_id).exists():
        ubicacion_service.update(ubi_id, **datos_ubi)
    else:
        ubicacion_service.create(**datos_ubi)

    return {"status": "ok", "mensaje": "Metadatos guardados"}

def handle_guardar_archivo(payload: dict) -> dict:
    """Guarda archivo físico (desde Base64) y sus metadatos/ubicación en DB."""
    datos_archivo = payload.get("archivo", {})
    datos_ubi = payload.get("ubicacion", {})
    contenido_b64 = payload.get("contenido_b64")
    
    if not contenido_b64 or not datos_archivo:
        return {"error": "Faltan datos o contenido Base64"}

    try:
        # 1. Decodificar Base64 a bytes
        contenido_bytes = base64.b64decode(contenido_b64)
        
        # 2. Guardar físicamente
        usuario_id = datos_archivo.get("propietario")
        archivo_id = datos_archivo.get("id")
        tamano_real = io_service.guardar_archivo(usuario_id, archivo_id, contenido_bytes)
        
        # 3. Actualizar el tamaño en los metadatos y guardar en BD
        datos_archivo["tamano_bytes"] = tamano_real
        
        # Upsert Archivo
        if Archivo.select().where(Archivo.id == archivo_id).exists():
            archivo_service.update(archivo_id, **datos_archivo)
        else:
            archivo_service.create(**datos_archivo)

        # Upsert Ubicacion
        if datos_ubi:
            ubi_id = datos_ubi.get("id")
            if ubi_id and UbicacionArchivo.select().where(UbicacionArchivo.id == ubi_id).exists():
                ubicacion_service.update(ubi_id, **datos_ubi)
            else:
                ubicacion_service.create(**datos_ubi)

        return {"status": "ok", "mensaje": "Archivo y metadatos guardados correctamente"}
    except Exception as e:
        logging.error(f"Error guardando archivo físico: {e}")
        return {"error": f"Fallo al procesar el archivo: {str(e)}"}

def handle_enviar_archivo(payload: dict) -> dict:
    """Lee el archivo físico y lo envía convertido en Base64."""
    usuario_id = payload.get("usuario_id")
    archivo_id = payload.get("archivo_id")
    
    if not usuario_id or not archivo_id:
        return {"error": "Se requiere usuario_id y archivo_id"}

    try:
        # Leer bytes del disco
        contenido_bytes = io_service.leer_archivo(usuario_id, archivo_id)
        
        # Convertir a Base64 y luego a string para el JSON
        contenido_b64 = base64.b64encode(contenido_bytes).decode('utf-8')
        
        return {
            "status": "ok",
            "archivo_id": archivo_id,
            "contenido_b64": contenido_b64
        }
    except FileNotFoundError:
        return {"error": "El archivo físico no existe en este nodo"}
    except Exception as e:
        return {"error": f"Error leyendo archivo: {str(e)}"}

def handle_eliminar_archivo(payload: dict) -> dict:
    """Soft-delete a DB (Archivo y TODAS sus Ubicaciones) y Hard-delete físico."""
    usuario_id = payload.get("usuario_id")
    archivo_id = payload.get("archivo_id")

    if not usuario_id or not archivo_id:
        return {"error": "Falta usuario_id o archivo_id"}

    # 1. Eliminar TODAS las ubicaciones conocidas de este archivo
    ubicaciones = UbicacionArchivo.select().where(UbicacionArchivo.archivo == archivo_id)
    for ubi in ubicaciones:
        ubicacion_service.delete(ubi.id)

    # 2. Hard-delete físico
    io_service.eliminar_archivo(usuario_id, archivo_id)

    # 3. Soft-delete del archivo
    exito = archivo_service.delete(archivo_id)

    if exito:
        return {"status": "ok", "mensaje": "Archivo eliminado completamente"}
    return {"error": "El archivo no existía en la base de datos"}


def registrar_handlers(message_handler):
    """
    Función utilitaria para conectar fácilmente estos controladores
    con la clase MessageHandler que creamos en el archivo anterior.
    """
    message_handler.registrar("ping", handle_ping)
    message_handler.registrar("recibir_cambios", handle_recibir_cambios)
    message_handler.registrar("obtener_cambios", handle_obtener_cambios)
    message_handler.registrar("guardar_usuario", handle_guardar_usuario)
    message_handler.registrar("eliminar_usuario", handle_eliminar_usuario)
    message_handler.registrar("guardar_metadatos_archivo", handle_guardar_metadatos_archivo)
    message_handler.registrar("guardar_archivo", handle_guardar_archivo)
    message_handler.registrar("enviar_archivo", handle_enviar_archivo)
    message_handler.registrar("eliminar_archivo", handle_eliminar_archivo)
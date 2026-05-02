from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from backend.api.auth import requerir_admin

from backend.services.services import UsuarioService, NodoService, ArchivoService, UbicacionArchivoService
from backend.services.io_service import IOService
from backend.network.client import P2PClient
from backend.db.models import Archivo, UbicacionArchivo

router = APIRouter(prefix="/admin", tags=["Administración"])

# Instancias de servicios
usuario_service = UsuarioService()
nodo_service = NodoService()
archivo_service = ArchivoService()
ubicacion_service = UbicacionArchivoService()
io_service = IOService()
p2p_client = P2PClient()

PUERTO_TCP_RED = 5555  # Asumimos el puerto estándar de tu red P2P

# --- Tareas en Segundo Plano ---
def propagar_eliminacion_usuario_red(usuario_id: str):
    """
    Envía el comando de eliminación (soft-delete y hard-delete de archivos)
    a todos los nodos activos de la red.
    """
    nodos_activos = [n for n in nodo_service.get_all() if n.get('activo')]
    for nodo in nodos_activos:
        p2p_client.eliminar_usuario_remoto(nodo['ip'], PUERTO_TCP_RED, usuario_id)


# --- Endpoints de Administración ---

@router.get("/nodos")
def obtener_nodos(admin_data: dict = Depends(requerir_admin)):
    """Devuelve la lista de todos los nodos conocidos en la red P2P."""
    nodos = nodo_service.get_all()
    return {"nodos": nodos}


@router.get("/usuarios")
def obtener_usuarios(admin_data: dict = Depends(requerir_admin)):
    """Devuelve todos los usuarios registrados."""
    usuarios = usuario_service.get_all()
    
    # Limpiamos el hash de la contraseña por seguridad antes de enviar el JSON
    for u in usuarios:
        u.pop('contrasena', None)
        
    return {"usuarios": usuarios}


@router.delete("/usuarios/{usuario_id}")
def eliminar_usuario(
    usuario_id: str, 
    background_tasks: BackgroundTasks, 
    admin_data: dict = Depends(requerir_admin)
):
    """
    Elimina a un usuario. Localmente aplica el borrado en cascada
    (libera espacio, soft-delete al usuario y sus archivos, hard-delete a los físicos) 
    y luego propaga la orden a la red.
    """
    # 1. Verificar que el usuario existe
    usuario_db = usuario_service.get_one(usuario_id)
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    # 2. Eliminación Local en cascada y contabilidad de espacio
    archivos = Archivo.select().where(Archivo.propietario == usuario_id)
    
    for archivo in archivos:
        # Buscamos todas las ubicaciones donde estaba guardado este archivo
        ubicaciones = UbicacionArchivo.select().where(UbicacionArchivo.archivo == archivo.id)
        tamano = archivo.tamano_bytes
        
        for ubi in ubicaciones:
            # MAGIA DE ESPACIO: Liberamos el espacio en el nodo correspondiente 
            # antes de borrar el registro de ubicación
            nodo_service.actualizar_espacio(ubi.nodo.id, tamano, sumar=False)
            ubicacion_service.delete(ubi.id)
            
        # Hard-delete del archivo físico
        try:
            io_service.eliminar_archivo(usuario_id, str(archivo.id))
        except Exception:
            pass # Si el archivo físico no estaba en este nodo local, ignoramos el error
            
        # Soft-delete de los metadatos
        archivo_service.delete(archivo.id)

    # 3. Soft-delete del usuario
    exito = usuario_service.delete(usuario_id)
    if not exito:
        raise HTTPException(status_code=500, detail="Error al eliminar el usuario localmente.")

    # 4. Propagar la decisión a la red P2P
    background_tasks.add_task(propagar_eliminacion_usuario_red, usuario_id)

    return {"mensaje": "Usuario eliminado, espacio liberado y orden de borrado enviada a la red P2P."}
import uuid
import base64
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, Query
from fastapi.responses import Response

from backend.api.auth import verificar_token
from backend.services.services import ArchivoService, UbicacionArchivoService, NodoService
from backend.services.io_service import IOService
from backend.network.client import P2PClient
from backend.config import get_mac_address

router = APIRouter(prefix="/archivos", tags=["Archivos"])

# Instancias de servicios
archivo_service = ArchivoService()
ubicacion_service = UbicacionArchivoService()
nodo_service = NodoService()
io_service = IOService()
p2p_client = P2PClient()

PUERTO_TCP_RED = 5555  # Asumimos este puerto para la comunicación P2P

# --- Función Helper Hardcodeada ---
def clasificador_ia_simulado(nombre_archivo: str):
    """Simula una IA que clasifica el archivo."""
    return "documentos", "general", 0.95

# --- Tareas en Segundo Plano (Distribución P2P) ---
def propagar_archivo_red(usuario_id: str, archivo_id: str, archivo_dict: dict, contenido_bytes: bytes):
    mi_mac = get_mac_address()
    nodos = nodo_service.get_all()
    nodos_activos = [n for n in nodos if n.get('activo')]

    nodos_activos.sort(
        key=lambda n: n.get('espacio_maximo', 0) - n.get('espacio_usado', 0), 
        reverse=True
    )

    nodos_top_2 = nodos_activos[:2]
    nodos_resto = nodos_activos[2:]

    # 1. Pre-generar la lista de ubicaciones ganadoras
    ubicaciones_globales = []
    for i, nodo in enumerate(nodos_top_2):
        ubicaciones_globales.append({
            "id": str(uuid.uuid4()),
            "nodo": nodo['id'],
            "archivo": archivo_id,
            "es_replica": (i > 0)
        })

    # 2. Distribuir la carga física a los Top 2, pasándoles la lista COMPLETA
    for i, nodo in enumerate(nodos_top_2):
        if nodo['id'] == mi_mac:
            io_service.guardar_archivo(usuario_id, archivo_id, contenido_bytes)
            # Guardamos todas las ubicaciones en nuestra DB local
            for ubi in ubicaciones_globales:
                if not ubicacion_service.model.select().where(ubicacion_service.model.id == ubi['id']).exists():
                    ubicacion_service.create(**ubi)
        else:
            p2p_client.enviar_archivo_desde_memoria(
                nodo['ip'], PUERTO_TCP_RED, archivo_dict, ubicaciones_globales, contenido_bytes
            )

    # 3. Enviar solo metadatos al resto de la red (con la lista COMPLETA)
    for nodo in nodos_resto:
        if nodo['id'] != mi_mac: 
            p2p_client.sincronizar_metadatos_archivo(
                nodo['ip'], PUERTO_TCP_RED, archivo_dict, ubicaciones_globales
            )

def propagar_eliminacion_red(usuario_id: str, archivo_id: str):
    """Manda el comando de eliminación a todos los nodos activos."""
    nodos_activos = [n for n in nodo_service.get_all() if n.get('activo')]
    for nodo in nodos_activos:
        p2p_client.eliminar_archivo_remoto(nodo['ip'], PUERTO_TCP_RED, usuario_id, archivo_id)


# --- Endpoints Públicos ---
@router.post("/")
async def subir_archivo(
    background_tasks: BackgroundTasks,
    archivo: UploadFile = File(...),
    datos_token: dict = Depends(verificar_token)
):
    usuario_id = datos_token['id']
    nuevo_id = str(uuid.uuid4())
    
    # 1. Leer contenido en la memoria RAM
    contenido_bytes = await archivo.read()
    
    # El tamaño lo calculamos directamente de la memoria
    tamano = len(contenido_bytes) 
    
    # Ya NO guardamos en el io_service aquí
    
    # 2. Clasificación simulada
    categoria, subcategoria, confianza = clasificador_ia_simulado(archivo.filename)
    
    # 3. Guardar metadatos localmente (siempre debemos tenerlos)
    archivo_dict = archivo_service.create(
        id=nuevo_id,
        nombre=archivo.filename,
        categoria=categoria,
        subcategoria=subcategoria,
        confianza=confianza,
        tamano_bytes=tamano,
        propietario=usuario_id
    )
    
    # 4. Delegar la distribución y pasamos el contenido en crudo
    background_tasks.add_task(propagar_archivo_red, usuario_id, nuevo_id, archivo_dict, contenido_bytes)
    
    return {
        "mensaje": "Archivo subido a memoria, metadatos creados y distribución P2P iniciada",
        "archivo": archivo_dict
    }

@router.get("/")
def obtener_metadatos_archivos(
    usuario_id: str = Query(None, description="Filtrar por ID de usuario (Solo Admin)"),
    datos_token: dict = Depends(verificar_token)
):
    rol = datos_token.get('rol')
    id_solicitante = datos_token.get('id')

    # Validación de seguridad
    if rol == 'usuario':
        # Un usuario normal solo puede ver sus cosas, ignoramos el query param
        target_usuario = id_solicitante
    elif rol == 'admin':
        # El admin puede ver de uno específico o de todos si no manda el parámetro
        target_usuario = usuario_id
    else:
        raise HTTPException(status_code=403, detail="Rol desconocido.")

    archivos = archivo_service.get_all()
    
    if target_usuario:
        archivos = [a for a in archivos if str(a.get('propietario')) == str(target_usuario)]
        
    return {"archivos": archivos}


@router.get("/{archivo_id}/descargar")
def descargar_archivo(archivo_id: str, datos_token: dict = Depends(verificar_token)):
    usuario_id = datos_token.get('id')
    rol = datos_token.get('rol')
    
    # 1. Verificar que el archivo existe y tenemos permisos
    archivo_db = archivo_service.get_one(archivo_id)
    if not archivo_db:
        raise HTTPException(status_code=404, detail="Archivo no encontrado.")
        
    if rol != 'admin' and str(archivo_db.get('propietario')) != str(usuario_id):
        raise HTTPException(status_code=403, detail="No tienes permiso para descargar este archivo.")

    propietario_real_id = str(archivo_db.get('propietario'))

    # 2. Intentar leerlo del disco local primero (es lo más rápido)
    try:
        contenido_bytes = io_service.leer_archivo(propietario_real_id, archivo_id)
        return Response(
            content=contenido_bytes, 
            media_type="application/pdf", # Puedes hacerlo dinámico después
            headers={"Content-Disposition": f'attachment; filename="{archivo_db.get("nombre")}"'}
        )
    except FileNotFoundError:
        pass # No está localmente, procedemos a buscarlo en la red

    # 3. Si no está local, buscar en la BD qué nodos lo tienen
    ubicaciones = ubicacion_service.model.select().where(ubicacion_service.model.archivo == archivo_id)
    nodos_con_archivo = [ubi.nodo.id for ubi in ubicaciones]

    if not nodos_con_archivo:
        raise HTTPException(status_code=404, detail="El archivo existe en BD pero no tiene ubicaciones físicas conocidas.")

    # 4. Pedir el archivo al primer nodo activo que lo tenga
    for nodo_id in nodos_con_archivo:
        nodo_info = nodo_service.get_one(nodo_id)
        if nodo_info and nodo_info.get('activo'):
            exito, respuesta = p2p_client.solicitar_descarga_archivo(
                nodo_info['ip'], PUERTO_TCP_RED, propietario_real_id, archivo_id
            )
            
            if exito and "contenido_bytes" in respuesta:
                return Response(
                    content=respuesta["contenido_bytes"], 
                    media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="{archivo_db.get("nombre")}"'}
                )

    raise HTTPException(status_code=503, detail="Ningún nodo que contiene el archivo está activo actualmente.")


@router.delete("/{archivo_id}")
def eliminar_archivo(archivo_id: str, background_tasks: BackgroundTasks, datos_token: dict = Depends(verificar_token)):
    usuario_id = datos_token.get('id')
    rol = datos_token.get('rol')

    archivo_db = archivo_service.get_one(archivo_id)
    if not archivo_db:
        raise HTTPException(status_code=404, detail="Archivo no encontrado.")

    if rol != 'admin' and str(archivo_db.get('propietario')) != str(usuario_id):
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este archivo.")

    propietario_real_id = str(archivo_db.get('propietario'))

    # 1. Eliminación Local
    # Borrar ubicaciones
    ubis = ubicacion_service.model.select().where(ubicacion_service.model.archivo == archivo_id)
    for ubi in ubis:
        ubicacion_service.delete(ubi.id)
        
    # Borrar físico y metadatos
    io_service.eliminar_archivo(propietario_real_id, archivo_id)
    archivo_service.delete(archivo_id)

    # 2. Propagar eliminación a toda la red en segundo plano
    background_tasks.add_task(propagar_eliminacion_red, propietario_real_id, archivo_id)

    return {"mensaje": "Archivo eliminado y orden de borrado enviada a la red."}
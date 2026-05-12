import uuid
import logging
from backend.db.models import UbicacionArchivo, Archivo
from backend.services.services import UbicacionArchivoService, NodoService, ArchivoService
from backend.services.io_service import IOService
from backend.network.client import P2PClient
from backend.config import NODE_ID

def evaluar_re_replicacion(nodo_muerto_id: str):
    """
    Se ejecuta en TODOS los nodos activos.
    Cada nodo revisa si es el portador de la última réplica viva de un archivo.
    Si es así, asume la responsabilidad de re-replicarlo de inmediato.
    """
    ubicacion_service = UbicacionArchivoService()
    nodo_service = NodoService()
    archivo_service = ArchivoService()
    io_service = IOService()
    p2p_client = P2PClient()
    mi_mac = NODE_ID
    PUERTO_TCP_RED = 5555

    # 1. Archivos que estaban en el nodo que murió (ignorando borrados)
    ubicaciones_afectadas = UbicacionArchivo.select().join(Archivo).where(
        (UbicacionArchivo.nodo == nodo_muerto_id) &
        (UbicacionArchivo.deleted_at.is_null()) &
        (Archivo.deleted_at.is_null())
    )

    for ubi_afectada in ubicaciones_afectadas:
        archivo_id = str(ubi_afectada.archivo.id)
        propietario_id = str(ubi_afectada.archivo.propietario)

        # 2. Examinar el estado actual de la red para ESTE archivo
        todas_ubicaciones_db = UbicacionArchivo.select().where(
            (UbicacionArchivo.archivo == archivo_id) &
            (UbicacionArchivo.deleted_at.is_null())
        )

        nodos_vivos_ids = []
        ubicaciones_globales_dicts = []
        yo_tengo_el_archivo = False

        for ubi in todas_ubicaciones_db:
            nodo = nodo_service.get_one(str(ubi.nodo.id))
            ubicaciones_globales_dicts.append(ubicacion_service._to_dict(ubi))
            
            if nodo and nodo.get('activo'):
                nodos_vivos_ids.append(nodo['id'])
                # Verificamos si nuestra MAC está en la lista de nodos vivos con el archivo
                if nodo['id'] == mi_mac:
                    yo_tengo_el_archivo = True

        # --- FILTRO 1: ¿Aún quedan suficientes réplicas? ---
        if len(nodos_vivos_ids) >= 2:
            continue

        # --- FILTRO 2: Si no quedan suficientes, ¿lo tengo yo? ---
        # Si no lo tengo, simplemente no puedo hacer nada, otro nodo actuará
        if not yo_tengo_el_archivo:
            continue

        # Si el código llega aquí, el archivo está en peligro (1 réplica) y NOSOTROS somos esa réplica.
        logging.info(f"El archivo {archivo_id} perdió réplicas. Yo tengo la copia local, iniciando re-replicación...")
        archivo_dict = archivo_service.get_one(archivo_id)

        # 3. Buscar el mejor candidato disponible
        todos_nodos = nodo_service.get_all()
        nodos_candidatos = [
            n for n in todos_nodos 
            if n.get('activo') and n['id'] not in nodos_vivos_ids and n['id'] != nodo_muerto_id
        ]

        if not nodos_candidatos:
            logging.warning(f"Red saturada o sin nodos. No se puede re-replicar el archivo {archivo_id}.")
            continue

        # Ordenar por espacio y tomar al mejor
        nodos_candidatos.sort(key=lambda n: n.get('espacio_maximo', 0) - n.get('espacio_usado', 0), reverse=True)
        mejor_candidato = nodos_candidatos[0]

        # 4. Crear la nueva ubicación en BD local
        nueva_ubi_dict = {
            "id": str(uuid.uuid4()),
            "nodo": mejor_candidato['id'],
            "archivo": archivo_id,
            "es_replica": True
        }

        # Guardar en BD (y actualizar contabilidad de espacio si implementaste la Opción 1 del paso anterior)
        ubicacion_service.create(**nueva_ubi_dict)
        # Si NO sobreescribiste el create del servicio, debes sumar el espacio manualmente:
        nodo_service.actualizar_espacio(mejor_candidato['id'], archivo_dict['tamano_bytes'], sumar=True)
        
        ubicaciones_globales_dicts.append(nueva_ubi_dict)

        # 5. Enviar el archivo
        try:
            contenido_bytes = io_service.leer_archivo(propietario_id, archivo_id)
            exito, _ = p2p_client.enviar_archivo_desde_memoria(
                mejor_candidato['ip'], 
                PUERTO_TCP_RED, 
                archivo_dict, 
                ubicaciones_globales_dicts, 
                contenido_bytes
            )

            if exito:
                logging.info(f"Réplica enviada exitosamente al nodo {mejor_candidato['id']}.")
                
                # 6. Avisar a los nodos pasivos de la nueva ubicación
                otros_nodos = [
                    n for n in todos_nodos 
                    if n.get('activo') and n['id'] not in [mi_mac, mejor_candidato['id']]
                ]
                
                for o_nodo in otros_nodos:
                    p2p_client.sincronizar_metadatos_archivo(
                        o_nodo['ip'], 
                        PUERTO_TCP_RED, 
                        archivo_dict, 
                        ubicaciones_globales_dicts
                    )
        except Exception as e:
            logging.error(f"Error al intentar re-replicar el archivo {archivo_id}: {str(e)}")
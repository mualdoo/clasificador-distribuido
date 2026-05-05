import uuid
import logging
from backend.db.models import UbicacionArchivo, Archivo
from backend.services.services import UbicacionArchivoService, NodoService, ArchivoService
from backend.services.io_service import IOService
from backend.network.client import P2PClient
from backend.config import get_mac_address

def evaluar_re_replicacion(nodo_muerto_id: str):
    """
    Evalúa si los archivos del nodo caído están en peligro (menos de 2 réplicas).
    Si es así, el nodo sobreviviente con la MAC más baja asume el liderazgo
    y envía su copia física a un nuevo nodo.
    """
    ubicacion_service = UbicacionArchivoService()
    nodo_service = NodoService()
    archivo_service = ArchivoService()
    io_service = IOService()
    p2p_client = P2PClient()
    mi_mac = get_mac_address()
    PUERTO_TCP_RED = 5555

    # 1. Obtenemos solo ubicaciones válidas de archivos que NO han sido borrados
    # El JOIN nos permite filtrar por el deleted_at de ambas tablas en una sola consulta
    ubicaciones_afectadas = UbicacionArchivo.select().join(Archivo).where(
        (UbicacionArchivo.nodo == nodo_muerto_id) &
        (UbicacionArchivo.deleted_at.is_null()) &
        (Archivo.deleted_at.is_null())
    )

    for ubi_afectada in ubicaciones_afectadas:
        archivo_id = str(ubi_afectada.archivo.id)
        propietario_id = str(ubi_afectada.archivo.propietario)

        # 2. Buscar todas las ubicaciones "vivas" de este archivo
        todas_ubicaciones_db = UbicacionArchivo.select().where(
            (UbicacionArchivo.archivo == archivo_id) &
            (UbicacionArchivo.deleted_at.is_null())
        )

        nodos_vivos_ids = []
        ubicaciones_globales_dicts = []

        for ubi in todas_ubicaciones_db:
            nodo = nodo_service.get_one(str(ubi.nodo.id))
            # Construimos la lista completa de ubicaciones para mandarla en los metadatos
            ubicaciones_globales_dicts.append(ubicacion_service._to_dict(ubi))
            
            if nodo and nodo.get('activo'):
                nodos_vivos_ids.append(nodo['id'])

        # --- REGLA DE NEGOCIO 1: Ya hay suficientes réplicas ---
        if len(nodos_vivos_ids) >= 2:
            logging.info(f"Archivo {archivo_id} a salvo. Tiene {len(nodos_vivos_ids)} réplicas activas.")
            continue

        # --- REGLA DE NEGOCIO 2: Tragedia de red ---
        if not nodos_vivos_ids:
            logging.error(f"¡ALERTA! El archivo {archivo_id} no tiene nodos vivos. Se ha perdido temporalmente.")
            continue

        # 3. DETERMINISMO: Elegimos al líder de la recuperación
        nodos_vivos_ids.sort()
        lider = nodos_vivos_ids[0]

        if mi_mac == lider:
            logging.info(f"Soy el líder para recuperar el archivo {archivo_id}. Buscando candidato...")
            archivo_dict = archivo_service.get_one(archivo_id)

            # Buscar a los nodos que están vivos y que NO tienen el archivo todavía
            todos_nodos = nodo_service.get_all()
            nodos_candidatos = [
                n for n in todos_nodos 
                if n.get('activo') and n['id'] not in nodos_vivos_ids and n['id'] != nodo_muerto_id
            ]

            if not nodos_candidatos:
                logging.warning(f"No hay nodos disponibles para alojar la nueva réplica de {archivo_id}.")
                continue

            # El candidato ideal es el que tenga más espacio libre
            nodos_candidatos.sort(key=lambda n: n.get('espacio_maximo', 0) - n.get('espacio_usado', 0), reverse=True)
            mejor_candidato = nodos_candidatos[0]

            # 4. Registrar la nueva ubicación localmente
            nueva_ubi_id = str(uuid.uuid4())
            nueva_ubi_dict = {
                "id": nueva_ubi_id,
                "nodo": mejor_candidato['id'],
                "archivo": archivo_id,
                "es_replica": True
            }

            ubicacion_service.create(**nueva_ubi_dict)
            nodo_service.actualizar_espacio(mejor_candidato['id'], archivo_dict['tamano_bytes'], sumar=True)
            
            # Agregamos la nueva ubicación a la lista que enviaremos por red
            ubicaciones_globales_dicts.append(nueva_ubi_dict)

            # 5. Extraer el archivo del disco local y enviarlo
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
                logging.error(f"Fallo crítico al recuperar el archivo {archivo_id}: {str(e)}")
                
        # (Si no somos el líder, el 'else' está implícito: no hacemos nada y 
        # confiamos en que el líder hará el trabajo descrito arriba).
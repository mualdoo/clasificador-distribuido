import datetime
import logging
from backend.services.services import NodoService, UsuarioService, ArchivoService, UbicacionArchivoService
from backend.network.client import P2PClient

# Inicializamos los servicios
nodo_service = NodoService()
usuario_service = UsuarioService()
archivo_service = ArchivoService()
ubicacion_service = UbicacionArchivoService()

def handle_saludo(payload: dict) -> dict:
    mac = payload.get("id")
    puerto_tcp = payload.get("puerto_tcp")
    
    # PRIORIDAD A TU IDEA: Usamos la IP explícita del payload. Si no viene, usamos la del socket.
    ip_origen = payload.get("ip_nodo") or payload.get("ip_origen_udp") 
    
    espacio_maximo = payload.get("espacio_maximo", 104857600)
    espacio_usado = payload.get("espacio_usado", 0)

    if not mac or not puerto_tcp:
        logging.warning("Mensaje de saludo ignorado por falta de MAC o puerto TCP")
        return {"error": "Datos incompletos"}

    # 1. Buscamos si el nodo ya existía
    nodo_existente = nodo_service.get_one(mac)
    ultima_conexion = datetime.datetime.min

    if nodo_existente:
        ultima_conexion = nodo_existente.get("ultima_conexion")
        if isinstance(ultima_conexion, str):
            try:
                ultima_conexion = datetime.datetime.fromisoformat(ultima_conexion)
            except ValueError:
                ultima_conexion = datetime.datetime.min

        # Actualizamos su estado a activo y su nueva IP por si cambió
        nodo_service.update(
            mac, 
            ip=ip_origen, 
            espacio_maximo=espacio_maximo, 
            espacio_usado=espacio_usado, 
            activo=True, 
            ultima_conexion=datetime.datetime.now()
        )
        logging.info(f"Nodo {mac} ({ip_origen}) reconectado. Preparando sincronización...")
    else:
        # Es un nodo totalmente nuevo
        nodo_service.create(
            id=mac, 
            ip=ip_origen, 
            espacio_maximo=espacio_maximo, 
            espacio_usado=espacio_usado, 
            activo=True, 
            ultima_conexion=datetime.datetime.now()
        )
        logging.info(f"Nuevo nodo descubierto: {mac} ({ip_origen}).")

    # 2. Enviar cambios TCP (solo si nosotros tenemos los datos actualizados)
    cambios = {
        "usuarios": usuario_service.get_all(since_timestamp=ultima_conexion),
        "nodos": nodo_service.get_all(since_timestamp=ultima_conexion),
        "archivos": archivo_service.get_all(since_timestamp=ultima_conexion),
        "ubicaciones": ubicacion_service.get_all(since_timestamp=ultima_conexion)
    }

    # 3. Enviamos la información por TCP al puerto que nos indicó
    # Al estar en un hilo en segundo plano (el del listener UDP), esta llamada de red 
    # no congelará el nodo.
    cliente_tcp = P2PClient()
    exito, respuesta = cliente_tcp.enviar_cambios(ip_origen, puerto_tcp, cambios)

    if not exito:
        logging.warning(f"No se le pudieron enviar los cambios al nodo {mac}: {respuesta.get('error')}")

    return {"status": "ok", "mensaje": "Saludo procesado"}


def registrar_broadcast_handlers(message_handler):
    message_handler.registrar("saludo", handle_saludo)
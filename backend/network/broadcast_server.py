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
    """
    Registra/actualiza un nodo que acaba de conectarse y le envía 
    los cambios ocurridos desde su última conexión vía TCP.
    """
    mac = payload.get("id")
    puerto_tcp = payload.get("puerto_tcp")
    ip_origen = payload.get("ip_origen") # Inyectado por nuestro listener UDP
    espacio_maximo = payload.get("espacio_maximo", 104857600)
    espacio_usado = payload.get("espacio_usado", 0)

    if not mac or not puerto_tcp:
        logging.warning("Mensaje de saludo ignorado por falta de MAC o puerto TCP")
        return {"error": "Datos incompletos"}

    # 1. Buscamos si el nodo ya existía en nuestra base de datos
    nodo_existente = nodo_service.get_one(mac)
    ultima_conexion = datetime.datetime.min

    if nodo_existente:
        # Extraemos su fecha de última conexión para saber qué mandarle
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

    # 2. Recopilamos todos los cambios desde su última conexión
    # Si ultima_conexion es None (nodo nuevo), los get_all devolverán toda la BD.
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


def handle_despedida(payload: dict) -> dict:
    """
    Marca un nodo como inactivo porque nos avisó que se va a desconectar.
    """
    mac = payload.get("id")
    if not mac:
        return {"error": "Falta ID del nodo"}

    nodo_existente = nodo_service.get_one(mac)
    if nodo_existente:
        # Se marca como inactivo y guardamos cuándo fue la última vez que lo vimos
        nodo_service.update(mac, activo=False, ultima_conexion=datetime.datetime.now())
        logging.info(f"El nodo {mac} se ha desconectado limpiamente.")
        return {"status": "ok", "mensaje": "Nodo marcado como inactivo"}
    
    return {"error": "Nodo no encontrado"}


def registrar_broadcast_handlers(message_handler):
    """
    Conecta estas funciones a un enrutador MessageHandler para UDP.
    """
    message_handler.registrar("saludo", handle_saludo)
    message_handler.registrar("despedida", handle_despedida)
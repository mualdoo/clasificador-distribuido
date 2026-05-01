import sys
import threading
import uuid
import os

# --- Base de datos ---
from backend.db.init_db import inicializar_bd

# --- Capa de Red TCP (ZeroMQ) ---
from backend.network.handler import MessageHandler
from backend.network.server import registrar_handlers
from backend.network.p2p import iniciar_listener
from backend.network.client import P2PClient

# --- Capa de Red UDP (Broadcast) ---
from backend.network.broadcast import iniciar_listener_broadcast
from backend.network.broadcast_client import BroadcastClient
from backend.network.broadcast_server import registrar_broadcast_handlers

# --- Servicios ---
from backend.services.services import UsuarioService, ArchivoService, UbicacionArchivoService, NodoService
from backend.services.io_service import IOService

def obtener_mac_local() -> str:
    """Obtiene la dirección MAC real de la computadora en formato XX:XX:XX:XX:XX:XX"""
    mac = uuid.getnode()
    return ':'.join(('%012X' % mac)[i:i+2] for i in range(0, 12, 2)).upper()

def imprimir_ayuda():
    print("\n--- Comandos Disponibles ---")
    print("  ping <ip> <puerto>                     : Verifica si un nodo está vivo")
    print("  crear_usuario <nombre> <contrasena>    : Crea un usuario en la BD local")
    print("  ver_usuarios                           : Lista los usuarios locales y sus IDs")
    print("  subir_archivo <user_id> <ruta_local>   : Guarda un archivo de tu PC en este nodo")
    print("  ver_archivos                           : Lista los archivos locales")
    print("  enviar_archivo <ip> <puerto> <file_id> : Envía un archivo físico a otro nodo")
    print("  ver_nodos                              : Lista los nodos descubiertos en la red")
    print("  salir                                  : Cierra el nodo y avisa a la red")
    print("----------------------------\n")

def main():
    # 1. Obtenemos el puerto TCP por argumento de consola (por defecto 5555)
    puerto_tcp = 5555
    if len(sys.argv) > 1:
        try:
            puerto_tcp = int(sys.argv[1])
        except ValueError:
            print("El puerto debe ser un número. Usando 5555 por defecto.")

    # Obtenemos nuestra MAC
    mi_mac = obtener_mac_local()

    # 2. Inicializar Base de Datos
    print(f"[{puerto_tcp}] Inicializando base de datos...")
    inicializar_bd()

    # 3. Iniciar Servidor TCP (ZeroMQ)
    enrutador_tcp = MessageHandler()
    registrar_handlers(enrutador_tcp)
    hilo_tcp = threading.Thread(
        target=iniciar_listener, 
        args=(puerto_tcp, enrutador_tcp),
        daemon=True
    )
    hilo_tcp.start()
    print(f"[{puerto_tcp}] Servidor P2P (TCP) escuchando en puerto {puerto_tcp}")

    # 4. Iniciar Servidor UDP (Broadcast)
    # Todos los nodos de tu red usarán este mismo puerto para los gritos UDP
    puerto_udp_red = 5556 
    enrutador_udp = MessageHandler()
    registrar_broadcast_handlers(enrutador_udp)
    hilo_udp = threading.Thread(
        target=iniciar_listener_broadcast, 
        args=(puerto_udp_red, enrutador_udp),
        daemon=True
    )
    hilo_udp.start()
    print(f"[{puerto_tcp}] Escuchando descubrimientos (UDP) en puerto {puerto_udp_red}")

    # 5. Saludar a la red (Avisar que existimos)
    cliente_broadcast = BroadcastClient(puerto_udp_red=puerto_udp_red)
    print("Anunciando presencia a la red local...")
    # Asumimos que inicialmente tenemos 100MB libres
    cliente_broadcast.enviar_saludo(mi_mac, puerto_tcp_local=puerto_tcp, espacio_maximo=104857600, espacio_usado=0)

    # 6. Instanciar cliente y servicios para la terminal local
    cliente_p2p = P2PClient()
    usuario_service = UsuarioService()
    archivo_service = ArchivoService()
    nodo_service = NodoService()
    io_service = IOService()

    imprimir_ayuda()

    # 7. Bucle del Cliente (CLI Interactivo)
    while True:
        try:
            comando_crudo = input(f"Nodo:{puerto_tcp} > ").strip().split()
            if not comando_crudo:
                continue

            accion = comando_crudo[0].lower()
            args = comando_crudo[1:]

            if accion == "salir":
                print("Avisando a la red que me desconecto...")
                cliente_broadcast.enviar_despedida(mi_mac)
                print("Cerrando nodo...")
                break
                
            elif accion == "ayuda":
                imprimir_ayuda()

            elif accion == "ping":
                if len(args) != 2:
                    print("Uso: ping <ip> <puerto>")
                    continue
                ip, port_destino = args[0], int(args[1])
                exito, resp = cliente_p2p.enviar_ping(ip, port_destino)
                print(f"Resultado: Exito={exito}, Respuesta={resp}")

            elif accion == "crear_usuario":
                if len(args) != 2:
                    print("Uso: crear_usuario <nombre> <contrasena>")
                    continue
                user = usuario_service.create(
                    nombre=args[0], 
                    contrasena=args[1], 
                    rol="usuario", 
                    intereses=["test"]
                )
                print(f"Usuario creado exitosamente. ID: {user['id']}")

            elif accion == "ver_usuarios":
                usuarios = usuario_service.get_all()
                for u in usuarios:
                    estado = "(Borrado)" if u.get('deleted_at') else ""
                    print(f" - {u['id']} | {u['nombre']} {estado}")
                    
            elif accion == "ver_nodos":
                nodos = nodo_service.get_all()
                for n in nodos:
                    estado = "Activo" if n['activo'] else "Inactivo"
                    print(f" - {n['id']} | IP: {n['ip']} | Estado: {estado} | Editado: {n['edited_at']}")

            elif accion == "subir_archivo":
                if len(args) != 2:
                    print("Uso: subir_archivo <user_id> <ruta_local_del_archivo>")
                    continue
                
                user_id = args[0]
                ruta_local = args[1]
                
                if not os.path.exists(ruta_local):
                    print(f"El archivo {ruta_local} no existe en tu computadora.")
                    continue
                
                nuevo_id = str(uuid.uuid4())
                nombre_archivo = os.path.basename(ruta_local)
                
                with open(ruta_local, 'rb') as f:
                    contenido = f.read()
                    
                tamano = io_service.guardar_archivo(user_id, nuevo_id, contenido)
                
                archivo_service.create(
                    id=nuevo_id,
                    nombre=nombre_archivo,
                    categoria="test",
                    subcategoria="test",
                    confianza=1.0,
                    tamano_bytes=tamano,
                    propietario=user_id
                )
                print(f"Archivo '{nombre_archivo}' guardado localmente con ID: {nuevo_id}")

            elif accion == "ver_archivos":
                archivos = archivo_service.get_all()
                for a in archivos:
                    estado = "(Borrado)" if a.get('deleted_at') else ""
                    print(f" - {a['id']} | {a['nombre']} ({a.get('tamano_bytes', 0)} bytes) {estado}")

            elif accion == "enviar_archivo":
                if len(args) != 3:
                    print("Uso: enviar_archivo <ip> <puerto> <file_id>")
                    continue
                
                ip, port_destino, file_id = args[0], int(args[1]), args[2]
                archivo_dict = archivo_service.get_one(file_id)
                
                if not archivo_dict:
                    print("Archivo no encontrado en BD local.")
                    continue
                
                ubicacion_dict = {
                    "nodo": mi_mac,
                    "archivo": file_id,
                    "es_replica": True
                }
                
                print("Enviando archivo por la red...")
                exito, resp = cliente_p2p.enviar_archivo_fisico(ip, port_destino, archivo_dict, ubicacion_dict)
                print(f"Resultado: Exito={exito}, Respuesta={resp}")

            else:
                print(f"Comando desconocido: {accion}. Escribe 'ayuda'.")

        except Exception as e:
            print(f"Error ejecutando el comando: {e}")

if __name__ == "__main__":
    # /media/aldo/Data/Tareas/8vo-semestre/Redes/practica3.pdf
    # 192.168.100.16
    main()
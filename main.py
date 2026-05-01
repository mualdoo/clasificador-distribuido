import sys
import threading
import uuid
import os

from backend.db.init_db import inicializar_bd
from backend.network.handler import MessageHandler
from backend.network.server import registrar_handlers
from backend.network.p2p import iniciar_listener
from backend.network.client import P2PClient

from backend.services.services import UsuarioService, ArchivoService, UbicacionArchivoService
from backend.services.io_service import IOService

def imprimir_ayuda():
    print("\n--- Comandos Disponibles ---")
    print("  ping <ip> <puerto>                     : Verifica si un nodo está vivo")
    print("  crear_usuario <nombre> <contrasena>    : Crea un usuario en la BD local")
    print("  ver_usuarios                           : Lista los usuarios locales y sus IDs")
    print("  subir_archivo <user_id> <ruta_local>   : Guarda un archivo de tu PC en este nodo")
    print("  ver_archivos                           : Lista los archivos locales")
    print("  enviar_archivo <ip> <puerto> <file_id> : Envía un archivo físico a otro nodo")
    print("  salir                                  : Cierra el nodo")
    print("----------------------------\n")

def main():
    # 1. Obtenemos el puerto por argumento de consola (por defecto 5555)
    puerto = 5555
    if len(sys.argv) > 1:
        try:
            puerto = int(sys.argv[1])
        except ValueError:
            print("El puerto debe ser un número. Usando 5555 por defecto.")

    # 2. Inicializar Base de Datos
    print(f"[{puerto}] Inicializando base de datos...")
    inicializar_bd()

    # 3. Configurar e iniciar el Servidor (Listener) en un hilo secundario
    enrutador = MessageHandler()
    registrar_handlers(enrutador)
    
    hilo_servidor = threading.Thread(
        target=iniciar_listener, 
        args=(puerto, enrutador),
        daemon=True # Se cerrará automáticamente cuando salgamos del programa
    )
    hilo_servidor.start()
    print(f"[{puerto}] Servidor P2P escuchando en el puerto {puerto}")

    # 4. Instanciar cliente y servicios para la terminal local
    cliente_p2p = P2PClient()
    usuario_service = UsuarioService()
    archivo_service = ArchivoService()
    ubicacion_service = UbicacionArchivoService()
    io_service = IOService()

    imprimir_ayuda()

    # 5. Bucle del Cliente (CLI Interactivo)
    while True:
        try:
            comando_crudo = input(f"Nodo:{puerto} > ").strip().split()
            if not comando_crudo:
                continue

            accion = comando_crudo[0].lower()
            args = comando_crudo[1:]

            if accion == "salir":
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
                    print(f" - {u['id']} | {u['nombre']}")

            elif accion == "subir_archivo":
                if len(args) != 2:
                    print("Uso: subir_archivo <user_id> <ruta_local_del_archivo_de_prueba>")
                    continue
                
                user_id = args[0]
                ruta_local = args[1]
                
                if not os.path.exists(ruta_local):
                    print(f"El archivo {ruta_local} no existe en tu computadora.")
                    continue
                
                nuevo_id = str(uuid.uuid4())
                nombre_archivo = os.path.basename(ruta_local)
                
                # Leemos de tu PC y lo guardamos en el storage del nodo
                with open(ruta_local, 'rb') as f:
                    contenido = f.read()
                    
                tamano = io_service.guardar_archivo(user_id, nuevo_id, contenido)
                
                # Guardamos en base de datos
                archivo_service.create(
                    id=nuevo_id,
                    nombre=nombre_archivo,
                    categoria="test",
                    subcategoria="test",
                    confianza=1.0,
                    tamano_bytes=tamano,
                    propietario=user_id
                )
                print(f"Archivo '{nombre_archivo}' guardado en el nodo con ID: {nuevo_id}")

            elif accion == "ver_archivos":
                archivos = archivo_service.get_all()
                for a in archivos:
                    print(f" - {a['id']} | {a['nombre']} ({a['tamano_bytes']} bytes)")

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
                    "nodo": "00:00:00:00:00:00", # Placeholder para pruebas
                    "archivo": file_id,
                    "es_replica": True
                }
                
                print("Enviando archivo por la red...")
                exito, resp = cliente_p2p.enviar_archivo_fisico(ip, port_destino, archivo_dict, ubicacion_dict)
                print(f"Resultado: Exito={exito}, Respuesta={resp}")

            else:
                print(f"Comando desconocido: {accion}. Escribe 'ayuda' para ver las opciones.")

        except Exception as e:
            print(f"Error ejecutando el comando: {e}")

if __name__ == "__main__":
    # /media/aldo/Data/Tareas/8vo-semestre/Redes/practica3.pdf
    main()
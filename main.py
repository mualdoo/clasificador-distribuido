import threading
import uuid
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI

# --- Base de datos ---
from backend.db.init_db import inicializar_bd

# --- Capa de Red TCP (ZeroMQ) ---
from backend.network.handler import MessageHandler
from backend.network.server import registrar_handlers
from backend.network.p2p import iniciar_listener, enviar_mensaje

# --- Capa de Red UDP (Broadcast) ---
from backend.network.broadcast import iniciar_listener_broadcast
from backend.network.broadcast_client import BroadcastClient
from backend.network.broadcast_server import registrar_broadcast_handlers

# --- Servicios ---
from backend.services.services import NodoService

# --- Routers de FastAPI ---
from backend.api.auth import router as auth_router
from backend.api.archivos import router as archivos_router
from backend.api.admin import router as admin_router

from backend.config import get_mac_address

PUERTO_TCP_P2P = 5555
PUERTO_UDP_RED = 5556

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ==========================================
    # EVENTOS DE INICIO (STARTUP)
    # ==========================================
    print(f"[*] Inicializando base de datos local...")
    inicializar_bd()

    mi_mac = get_mac_address()

    # 1. Iniciar Servidor TCP (ZeroMQ) en segundo plano
    enrutador_tcp = MessageHandler()
    registrar_handlers(enrutador_tcp)
    hilo_tcp = threading.Thread(
        target=iniciar_listener, 
        args=(PUERTO_TCP_P2P, enrutador_tcp),
        daemon=True
    )
    hilo_tcp.start()
    print(f"[*] Servidor P2P (TCP) escuchando en puerto {PUERTO_TCP_P2P}")

    # 2. Iniciar Servidor UDP (Broadcast) en segundo plano
    enrutador_udp = MessageHandler()
    registrar_broadcast_handlers(enrutador_udp)
    hilo_udp = threading.Thread(
        target=iniciar_listener_broadcast, 
        args=(PUERTO_UDP_RED, enrutador_udp),
        daemon=True
    )
    hilo_udp.start()
    print(f"[*] Escuchando descubrimientos (UDP) en puerto {PUERTO_UDP_RED}")

    # 3. Saludar a la red (Anunciar presencia)
    cliente_broadcast = BroadcastClient(puerto_udp_red=PUERTO_UDP_RED)
    print("[*] Anunciando presencia a la red local...")
    # Asumimos que inicialmente tenemos 100MB libres
    cliente_broadcast.enviar_saludo(mi_mac, puerto_tcp_local=PUERTO_TCP_P2P, espacio_maximo=104857600, espacio_usado=0)

    # Entregar el control a FastAPI para que procese peticiones HTTP
    yield 

    # ==========================================
    # EVENTOS DE APAGADO (SHUTDOWN)
    # ==========================================
    print("\n[*] Deteniendo servidor. Avisando a la red que me desconecto de forma segura (TCP)...")
    
    nodo_service = NodoService()
    nodos_amigos = nodo_service.model.select().where(nodo_service.model.activo == True)
    
    for amigo in nodos_amigos:
        if str(amigo.id) != mi_mac:
            try:
                # Enviamos el mensaje directo TCP que orquestamos en el paso anterior
                enviar_mensaje(amigo.ip, PUERTO_TCP_P2P, "nodo_inactivo", {"nodo_id": mi_mac})
            except Exception as e:
                pass # Ignoramos errores, nuestro objetivo principal es salir rápido
                
    print("[*] Nodo cerrado exitosamente.")

# --- Instancia de la Aplicación ---
app = FastAPI(
    title="Sistema de Archivos P2P",
    description="API para gestión descentralizada de archivos y nodos",
    version="1.0.0",
    lifespan=lifespan
)

# --- Inclusión de Rutas ---
app.include_router(auth_router)
app.include_router(archivos_router)
app.include_router(admin_router)
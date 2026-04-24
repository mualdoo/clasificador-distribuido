import threading
from src.database.models import init_db
from src.network.discovery import discovery
from src.network.rpc_handler import handle_rpc_request
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager

app = FastAPI()
init_db() # Crear tablas

@app.post("/rpc")
async def rpc_endpoint(request: Request):
    """Recibe las llamadas JSON-RPC de otros nodos."""
    body = await request.body()
    response = handle_rpc_request(body.decode())
    return response

def startup_event():
    # 1. Iniciar el hilo de escucha UDP
    thread = threading.Thread(target=discovery.start_listener, daemon=True)
    thread.start()
    
    # 2. Gritar "¡Hola!" a la red
    discovery.announce_presence()

def shutdown_event():
    # 3. Avisar que nos vamos
    discovery.send_goodbye()

@asynccontextmanager
async def lifespan(app: FastAPI):
    startup_event()
    yield
    shutdown_event()
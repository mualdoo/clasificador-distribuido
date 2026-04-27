from contextlib import asynccontextmanager
import os
import base64
import uuid
import threading
from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Importaciones locales
from src.config import NODE_ID, NODE_IP, STORAGE_PATH
from src.database.models import init_db, Nodo, Archivo, Usuario, db
from src.network.discovery import discovery
from src.network.rpc_handler import handle_rpc_request
from src.network.messenger import send_rpc, replicate_to_all
from src.ai_engine.extractor import extract_text_from_bytes
from src.ai_engine.classifier_engine import classifier
from src.services.file_service import file_service

app = FastAPI(title=f"P2P Node - {NODE_ID}")

# 1. Configuración de CORS para permitir acceso desde el Frontend (React) e Internet
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, usa la URL específica de Cloudflare/Frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- RUTAS DE LA API ---

@app.get("/")
async def root():
    return {
        "node_id": NODE_ID,
        "ip": NODE_IP,
        "status": "online",
        "service": "P2P Scientific Paper Classifier"
    }

@app.post("/rpc")
async def rpc_endpoint(request: Request):
    """Punto de entrada para que otros nodos se comuniquen con este."""
    body = await request.body()
    # Despacha la petición al rpc_handler
    response = handle_rpc_request(body.decode())
    return response

@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...), 
    usuario_id: str = Form(...)
):
    """Procesa, clasifica y distribuye un nuevo PDF en la red."""
    # A. Leer archivo en memoria
    pdf_content = await file.read()
    
    # B. Extraer texto y clasificar con Scikit-learn
    text = extract_text_from_bytes(pdf_content)
    if not text:
        raise HTTPException(status_code=400, detail="No se pudo procesar el contenido del PDF.")
    
    categoria, subcategoria, confianza = classifier.predict(text)

    # C. Lógica de Distribución: Elegir dónde guardar (Original y Réplica)
    nodo_primario, nodo_replica = file_service.choose_nodes_for_storage()
    
    file_uuid = str(uuid.uuid4())
    metadata = {
        "id": file_uuid,
        "nombre": file.filename,
        "clasificacion": categoria,
        "subcategoria": subcategoria,
        "confianza": confianza,
        "propietario_id": usuario_id,
        "nodo_id": nodo_primario.id if hasattr(nodo_primario, 'id') else NODE_ID,
        "ruta_relativa": f"{categoria}/{file.filename}"
    }

    # D. Envío físico del archivo
    encoded_pdf = base64.b64encode(pdf_content).decode('utf-8')
    
    # Guardar en el primario
    if nodo_primario == NODE_ID:
        file_service.save_local_file(pdf_content, metadata)
    else:
        send_rpc(nodo_primario.direccion_ip, "store_physical_file", {
            "file_bytes_b64": encoded_pdf,
            "metadata": metadata
        })

    # Guardar réplica si existe un segundo nodo
    if nodo_replica:
        send_rpc(nodo_replica.direccion_ip, "store_physical_file", {
            "file_bytes_b64": encoded_pdf,
            "metadata": metadata
        })

    # E. Replicación de Metadatos: Avisar a todos los nodos
    vecinos = Nodo.select()
    replicate_to_all(vecinos, "replicate_file_metadata", metadata)

    return {
        "message": "Archivo distribuido con éxito",
        "metadata": metadata
    }

@app.get("/files")
async def list_files():
    """Devuelve la lista global de archivos conocidos por este nodo."""
    archivos = list(Archivo.select().dicts())
    return archivos

@app.get("/nodes")
async def list_nodes():
    """Devuelve la lista de nodos activos descubiertos en la red."""
    nodos = list(Nodo.select().dicts())
    return nodos

# --- EVENTOS DE CICLO DE VIDA ---

def startup_event():
    # 1. Inicializar Base de Datos (Crear tablas si no existen)
    init_db()
    
    # 2. Iniciar el hilo de escucha para el descubrimiento UDP (Discovery)
    discovery_thread = threading.Thread(target=discovery.start_listener, daemon=True)
    discovery_thread.start()
    
    # 3. Anunciar presencia a la red local
    discovery.announce_presence()
    print(f"🚀 Nodo {NODE_ID} iniciado correctamente en {NODE_IP}")

def shutdown_event():
    # 3. Avisar que nos vamos
    discovery.send_goodbye()

@asynccontextmanager
async def lifespan(app: FastAPI):
    startup_event()
    yield
    shutdown_event()




if __name__ == "__main__":
    import uvicorn
    # Ejecución manual (aunque se recomienda usar python -m uvicorn)
    uvicorn.run(app, host="0.0.0.0", port=5000)
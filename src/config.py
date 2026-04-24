import os
import socket
import uuid

def get_mac_address():
    """
    Obtiene la dirección MAC del sistema en formato hexadecimal (XX:XX:XX:XX:XX:XX).
    """
    # uuid.getnode() obtiene un entero de 48 bits que representa la MAC
    mac_int = uuid.getnode()
    
    # Convertimos el entero a una cadena hexadecimal y formateamos con ":"
    mac_hex = iter(hex(mac_int)[2:].zfill(12))
    mac_address = ":".join(a + b for a, b in zip(mac_hex, mac_hex))
    
    return mac_address.upper()

# --- CONFIGURACIÓN DE RED ---
def get_local_ip():
    """Detecta la IP real de la máquina en la red local (LAN)"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # No necesita conexión real, solo para detectar la interfaz activa
        s.connect(('8.8.8.8', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

# Identidad del Nodo
NODE_IP = get_local_ip()
NODE_ID = get_mac_address()

# Puertos
RPC_PORT = 5000         # Puerto para JSON-RPC y API Web
UDP_PORT = 41234        # Puerto para Discovery (Broadcast)

# --- INTELIGENCIA ARTIFICIAL (OLLAMA) ---
# En Docker para Windows/Mac usamos 'host.docker.internal'
# OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
# OLLAMA_MODEL = "llama3" # O el modelo que prefieran (phi3, mistral, etc.)

# --- RUTAS DE ARCHIVOS ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORAGE_PATH = os.path.join(BASE_DIR, "data", "library")
DB_PATH = os.path.join(BASE_DIR, "data", "local_db.sqlite")

# Asegurar que la carpeta de almacenamiento existe
os.makedirs(STORAGE_PATH, exist_ok=True)
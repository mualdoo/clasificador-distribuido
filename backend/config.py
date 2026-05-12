import uuid
import socket
from pathlib import Path

# ── Nodo ──────────────────────────────────────────────────────────────────────
def get_mac_address() -> str:
    mac = uuid.getnode()
    return ':'.join(f'{(mac >> (8 * i)) & 0xFF:02x}' for i in reversed(range(6)))

def get_local_ip() -> str:
    """
    Intenta conectarse a una IP externa (no necesita internet real)
    para forzar al SO a revelar qué interfaz usaría para salir a la red.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # No importa si esta IP existe, el SO elige la interfaz de salida
        s.connect(('8.8.8.8', 80))
        ip_local = s.getsockname()[0]
    except Exception:
        # Fallback en caso de que no haya ninguna red
        ip_local = '127.0.0.1'
    finally:
        s.close()
    return ip_local

NODE_ID: str = get_mac_address()
NODE_IP: str = get_local_ip()

# ── Red / P2P ──────────────────────────────────────────────────────────────
REQUEST_TIMEOUT = 2500  # Milisegundos que esperamos antes de considerar que falló un intento
REQUEST_RETRIES = 3     # Cuántas veces reintentamos antes de dar el nodo por muerto

# ── Red / ZeroMQ ──────────────────────────────────────────────────────────────
ZMQ_BROADCAST_PORT: int = 5555   # PUB/SUB  — mensajes a todos los nodos
ZMQ_DIRECT_PORT: int    = 5556   # DEALER/ROUTER — mensajes punto a punto
SPACE_QUERY_TIMEOUT_MS: int = 3000  # tiempo máximo esperando respuestas de espacio

# ── Almacenamiento ────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parent
STORAGE_DIR: Path = BASE_DIR / "storage"
STORAGE_DIR.mkdir(exist_ok=True)

# ── Base de datos ─────────────────────────────────────────────────────────────
DATABASE_PATH: Path = BASE_DIR / "db" / "database.db"

# ── ML ────────────────────────────────────────────────────────────────────────
ML_DIR         = BASE_DIR / "ml"
MODEL_PATH     = ML_DIR / "model.pkl"
ENCODER_PATH   = ML_DIR / "label_encoder.pkl"

# ── API ───────────────────────────────────────────────────────────────────────
API_HOST: str = "0.0.0.0"
API_PORT: int = 8000
SECRET_KEY: str = "cambia-esto-por-una-clave-segura"
SESSION_MAX_AGE: int = 86400  # segundos — 1 día

# ── Roles ─────────────────────────────────────────────────────────────────────
ROLE_USER  = "user"
ROLE_ADMIN = "admin"
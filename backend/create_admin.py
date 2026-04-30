"""
Ejecutar una sola vez para crear el usuario admin inicial.
Uso: python create_admin.py
"""

from backend.db.database import init_db
from backend.db.models import MODELS, Usuario
from backend.config import ROLE_ADMIN
from passlib.context import CryptContext
import unicodedata

init_db(MODELS)

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

ADMIN_NOMBRE    = "admin"
ADMIN_CONTRASENA = "admin123"  # cámbiala

def _preparar_contrasena(contrasena: str) -> str:
    """
    Normaliza la contraseña antes de hashear.
    - Normalización Unicode (NFC) — evita diferencias de encoding entre OS
    - Truncar a 72 bytes — límite de bcrypt
    """
    import unicodedata
    # NFC asegura que el mismo caracter tenga la misma representación binaria
    # en todos los sistemas operativos
    normalizada = unicodedata.normalize("NFC", contrasena)
    encoded = normalizada.encode("utf-8")
    if len(encoded) > 72:
        encoded = encoded[:72]
    return encoded.decode("utf-8", errors="ignore")

if Usuario.select().where(Usuario.nombre == ADMIN_NOMBRE).exists():
    print(f"El usuario '{ADMIN_NOMBRE}' ya existe.")
else:
    Usuario.create(
        nombre=ADMIN_NOMBRE,
        contrasena=_pwd.hash(_preparar_contrasena(ADMIN_CONTRASENA)),
        rol=ROLE_ADMIN,
        intereses="",
    )
    print(f"Admin '{ADMIN_NOMBRE}' creado correctamente.")
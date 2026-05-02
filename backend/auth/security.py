import jwt
import datetime

# IMPORTANTE: En producción, esto debe venir de variables de entorno (.env)
SECRET_KEY = "super_secreto_para_desarrollo_cambialo"
ALGORITHM = "HS256"
EXPIRATION_HOURS = 24

def crear_token(usuario_id: str, rol: str) -> str:
    """Genera un JWT válido por 24 horas."""
    payload = {
        "sub": str(usuario_id), # Subject (quién es el dueño del token)
        "rol": rol,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=EXPIRATION_HOURS),
        "iat": datetime.datetime.utcnow() # Issued at (cuándo se emitió)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decodificar_token(token: str) -> str:
    """
    Decodifica el JWT y retorna el ID del usuario.
    Si el token expiró o es inválido, retorna None.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
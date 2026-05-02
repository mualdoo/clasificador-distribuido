from fastapi import APIRouter, HTTPException, Response, Request, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import List

from backend.auth.security import crear_token, decodificar_token
from backend.services.services import UsuarioService, NodoService
from backend.network.client import P2PClient

EXPIRATION_HOURS = 24

router = APIRouter(prefix="/auth", tags=["Autenticación"])

# Instanciamos los servicios
usuario_service = UsuarioService()
nodo_service = NodoService()
p2p_client = P2PClient()

# --- Modelos de validación (Pydantic) ---
class RegistroRequest(BaseModel):
    nombre: str
    contrasena: str
    intereses: List[str] = []

class LoginRequest(BaseModel):
    nombre: str
    contrasena: str

# --- Tareas en Segundo Plano ---
def notificar_red_nuevo_usuario(usuario_dict: dict):
    """Envía el nuevo usuario a todos los nodos activos de la red."""
    # Obtenemos los nodos activos directamente del modelo
    nodos_activos = nodo_service.model.select().where(nodo_service.model.activo == True) # TODO: cambiar si hay problemas con broadcast
    
    # Asumimos que todos los nodos usan el puerto 5555 para ZeroMQ. 
    # Si guardaste el puerto TCP en tu modelo Nodo, extráelo de ahí.
    PUERTO_TCP_RED = 5555 
    
    for nodo in nodos_activos:
        # Enviar de forma segura a través de nuestra capa de red
        p2p_client.sincronizar_usuario(nodo.ip, PUERTO_TCP_RED, usuario_dict)

def verificar_token(request: Request) -> dict:
    """Valida la cookie y extrae los datos del token sin tocar la BD."""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="No autorizado. Inicie sesión.")
        
    datos_token = decodificar_token(token)
    if not datos_token:
        raise HTTPException(status_code=401, detail="Token inválido o expirado.")
        
    return datos_token

def requerir_usuario_autenticado(datos_token: dict = Depends(verificar_token)):
    """Asegura que el usuario tenga un token válido (cualquier rol)."""
    return datos_token

def requerir_admin(datos_token: dict = Depends(verificar_token)):
    """Asegura que el usuario tenga un token válido Y sea administrador."""
    if datos_token.get("rol") != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado. Se requieren permisos de administrador.")
    return datos_token

# --- Endpoints ---

@router.post("/registro")
def registrar_usuario(datos: RegistroRequest, background_tasks: BackgroundTasks):
    # Validar si el nombre ya existe (opcional, pero recomendado)
    existe = usuario_service.model.select().where(usuario_service.model.nombre == datos.nombre).exists()
    if existe:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está en uso.")

    # Crear el usuario en la base de datos local
    nuevo_usuario = usuario_service.create(
        nombre=datos.nombre,
        contrasena=datos.contrasena, # El servicio ya se encarga de hashearla
        rol="usuario",
        intereses=datos.intereses
    )

    # Delegamos la replicación P2P a un hilo de fondo para no hacer esperar al cliente
    background_tasks.add_task(notificar_red_nuevo_usuario, nuevo_usuario)

    # Ocultamos el hash antes de devolver la respuesta
    nuevo_usuario.pop('contrasena', None)
    return {"mensaje": "Usuario registrado exitosamente", "usuario": nuevo_usuario}


@router.post("/login")
def iniciar_sesion(datos: LoginRequest, response: Response):
    # Buscar al usuario por nombre usando Peewee
    usuario_db = usuario_service.model.get_or_none(usuario_service.model.nombre == datos.nombre)
    
    if not usuario_db:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas.")
        
    # Usar el método de verificación que creamos en UsuarioService
    if not usuario_service.verify_password(datos.contrasena, usuario_db.contrasena):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas.")

    # Generar JWT
    token = crear_token(str(usuario_db.id), usuario_db.rol)

    # Inyectar la cookie HTTP-Only en la respuesta
    # SameSite='lax' protege contra la mayoría de ataques CSRF en navegadores modernos
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=EXPIRATION_HOURS * 3600,
        samesite="lax",
        secure=False # Cambiar a True en producción cuando tengas HTTPS
    )

    return {"mensaje": "Inicio de sesión exitoso"}


@router.post("/logout")
def cerrar_sesion(response: Response):
    # Para hacer logout con cookies, simplemente le decimos al navegador que borre la cookie
    response.delete_cookie(key="access_token")
    return {"mensaje": "Sesión cerrada correctamente"}


@router.get("/me")
def obtener_perfil(datos_token: dict = Depends(requerir_usuario_autenticado)):
    # Opcional: Si en /me quieres devolver todos los datos, aquí sí puedes 
    # hacer la consulta a la BD usando datos_token['id']. 
    # Si solo quieres devolver lo que hay en el token, retornas datos_token directo.
    usuario = usuario_service.get_one(datos_token['id'])
    if usuario:
        usuario.pop('contrasena', None)
    return {"usuario": usuario}
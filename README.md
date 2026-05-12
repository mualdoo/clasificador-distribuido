# Sistema de Archivos P2P Distribuido

Un sistema descentralizado de almacenamiento y compartición de archivos construido con Python y FastAPI. Este proyecto implementa una red *Peer-to-Peer* (P2P) tolerante a fallos, balanceo de carga de almacenamiento y descubrimiento automático de nodos en redes locales.

## Características Principales

* **Descubrimiento Automático:** Los nodos se encuentran entre sí automáticamente mediante ráfagas UDP (*Broadcast*).
* **Comunicación Confiable:** Mensajería en tiempo real y transferencia de archivos físicos mediante TCP usando ZeroMQ.
* **Tolerancia a Fallos y Auto-Sanación:** Si un nodo se desconecta o falla, la red re-replica automáticamente los archivos en peligro para garantizar su disponibilidad.
* **Balanceo de Carga:** Los archivos se distribuyen inteligentemente a los nodos con mayor espacio disponible.
* **Autenticación JWT:** Sistema de sesiones seguro mediante cookies *HTTP-Only* con roles de Usuario y Administrador.
* **Base de Datos Distribuida:** Cada nodo mantiene su propio estado local sincronizado usando SQLite y Peewee ORM.

## Tecnologías Utilizadas

* **Backend:** FastAPI, Python 3
* **Redes:** PyZMQ (ZeroMQ), Sockets nativos (UDP)
* **Base de Datos:** Peewee ORM, SQLite
* **Seguridad:** Bcrypt, PyJWT

---

## Requisitos Previos

* Python 3.8 o superior.
* Estar conectado a una red local (LAN o Wi-Fi).

## Configuración e Instalación

1. **Clonar el repositorio:**
```bash
git clone https://github.com/mualdoo/clasificador-distribuido
cd clasificador-distribuido

```

2. **Crear un entorno virtual (Recomendado):**
```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

```


3. **Instalar las dependencias:**
```bash
pip install -r requirements.txt

```



---

## Configuración de Red (Especial para Windows)

Para que los nodos puedan descubrirse y comunicarse correctamente a través de la red local, el Firewall de Windows debe permitir el tráfico en puertos específicos y responder a peticiones Ping.

Abre **PowerShell como Administrador** y ejecuta los siguientes comandos una sola vez:

**1. Permitir Descubrimiento de Nodos (UDP Broadcast):**

```powershell
New-NetFirewallRule -DisplayName "P2P_UDP_Descubrimiento" -Direction Inbound -Action Allow -Protocol UDP -LocalPort 5556

```

**2. Permitir Transferencia de Archivos y Sincronización (TCP ZeroMQ):**

```powershell
New-NetFirewallRule -DisplayName "P2P_TCP_Mensajeria" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 5555

```

**3. Permitir ser detectado en la red (Ping / ICMPv4):**

```powershell
New-NetFirewallRule -DisplayName "Permitir Ping (ICMPv4)" -Direction Inbound -Action Allow -Protocol ICMPv4

```

*(Si usas Linux/Ubuntu, asegúrate de permitir los puertos usando `sudo ufw allow 5555/tcp` y `sudo ufw allow 5556/udp`).*

---

## Cómo iniciar un Nodo

Para arrancar el servidor P2P y la API web simultáneamente, ejecuta:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

```

Al iniciar por primera vez, el sistema creará automáticamente la base de datos local (`database.db`) y generará un usuario administrador por defecto.

## Uso de la API

Una vez que el servidor esté corriendo, puedes acceder a la **Interfaz Interactiva de la API (Swagger UI)** desde cualquier navegador para probar los endpoints:

**[http://localhost:8000/docs](https://www.google.com/search?q=http://localhost:8000/docs)**

### Credenciales por defecto:

* **Usuario:** `admin`
* **Contraseña:** `admin123`

*(Utiliza el endpoint `POST /auth/login` con estas credenciales para obtener tu cookie de sesión y poder acceder a las rutas protegidas de subida de archivos y administración de red).*

---

*Desarrollado como proyecto de ingeniería de sistemas distribuidos.*
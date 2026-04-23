#  Gestor PDF

Interfaz del proyecto para organizar articulos en formato PDF por categorias y subcategorias. Esta version solo es visual y no tiene ninguna funcionalidad real (por el momento XD)
---

##  Instalación

```bash
# 1. Clona el repositorio
git clone https://github.com/mualdoo/clasificador-distribuido/tree/main/Gestor-Pdf
cd gestor-pdf

# 2. Instala las dependencias
npm install

# 3. Inicia la aplicación
npm run dev
```

Abre el navegador en `http://localhost:5173`

> **Credenciales de prueba:**
> - Administrador: usuario `admin` / contraseña `admin`
> - Usuario normal: cualquier usuario y contraseña

---

##  Funcionalidades 

Todo es solo visual, nada Tiene una funcionalidad real 

### Como usuario normal
- Iniciar sesión o crear una cuenta
- Ver tus archivos PDF organizados por categorías y subcategorías
- Crear y eliminar tus propias categorías y subcategorías desde el sidebar
- Filtrar archivos haciendo clic en una categoría o subcategoría
- Seleccionar uno o varios archivos con el checkbox de cada tarjeta
- Generar citas en formato **APA 7** de los archivos seleccionados y copiarlas al portapapeles
- Cargar nuevos archivos PDF — la app simula analizarlos y los asigna automáticamente a una categoría
- Descargar o eliminar archivos individuales

### Como administrador
- Ver el panel de gestión con la lista de todos los usuarios registrados
- Cambiar contraseñas, gestionar carpetas o dar de baja usuarios
- Eliminar cualquier carpeta, incluso si tiene archivos

---

##  Tecnologías usadas
- [React](https://react.dev/) + [TypeScript](https://www.typescriptlang.org/)
- [Vite](https://vitejs.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Lucide React](https://lucide.dev/) para los íconos

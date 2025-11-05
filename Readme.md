#  Proyecto Autotrust_DJ

Proyecto Django para la gestión de vehículos.

---

## ⚙️ Requisitos previos

- **Python 3.12** o superior  
- **Entorno virtual** (ya configurado en `.venv`)
- **SQLite** (ya incluido por defecto con Django)

---

## 🧱 Instalación y ejecución local

### 1️⃣ Clonar el repositorio
```bash
git clone https://github.com/SimonCastroV/Autotrust_DJ.git
cd Autotrust_DJ
```

### 2️⃣ Activar el entorno virtual
Si ya existe el entorno `.venv`, actívalo según tu sistema operativo:

#### 🪟 Windows (PowerShell)
```bash
.venv\Scripts\activate
```

#### 🍎 macOS / 🐧 Linux
```bash
source .venv/bin/activate
```

> 💡 Si ves el prefijo `(.venv)` al inicio de tu terminal, el entorno está activo correctamente.

---

### 3️⃣ Instalar dependencias
```bash
pip install -r requirements.txt
```

---

### 4️⃣ Aplicar migraciones
```bash
python manage.py migrate
```

---

### 5️⃣ Ejecutar el servidor local
```bash
python manage.py runserver
```

Abre en tu navegador 👉 **http://127.0.0.1:8000/**

---

## 🧰 Variables de entorno
Crea un archivo `.env` en la raíz del proyecto (o usa variables de entorno) con las claves que correspondan a tu despliegue.  
Ejemplo:
```env
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=<REEMPLAZA_CON_CLAVE_SEGURA>
DJANGO_ALLOWED_HOSTS=<HOST_1>,<HOST_2>
DJANGO_CSRF_TRUSTED_ORIGINS=<ORIGEN_HTTPS_1>,<ORIGEN_HTTPS_2>
DATABASE_URL=sqlite:////app/data/db.sqlite3  # Opcional: apunta a un archivo dentro de un volumen
REDIS_URL=<URL_REDIS_OPCIONAL>
DJANGO_STATIC_ROOT=/app/staticfiles
```
> Reemplaza los placeholders con tus propios valores. Si mantienes SQLite sin `DATABASE_URL`, la base de datos se creará en `/app/db.sqlite3` dentro del contenedor.

---
## Link para Formato JSON proveedor del Servicio

```bash
http://127.0.0.1:8000/api/vehicles/
```

---

## 🐋 Docker

### 1️⃣ Construir la imagen
```bash
docker build -t autotrust:latest .
```

### 2️⃣ Preparar variables
Guarda tus variables en un archivo (por ejemplo `docker.env`) para reutilizarlas:
```env
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=<REEMPLAZA_CON_CLAVE_SEGURA>
DJANGO_ALLOWED_HOSTS=<HOST_PRODUCCION>
DJANGO_CSRF_TRUSTED_ORIGINS=<ORIGEN_HTTPS_1>,<ORIGEN_HTTPS_2>
DATABASE_URL=sqlite:////app/data/db.sqlite3
```
> El path anterior asume que montas un volumen en `/app/data` para persistir la base de datos SQLite.

### 3️⃣ Crear un volumen (opcional pero recomendado para SQLite)
```bash
docker volume create autotrust_data
```

### 4️⃣ Ejecutar migraciones dentro de un contenedor efímero
```bash
docker run --rm \
  --env-file docker.env \
  -v autotrust_data:/app/data \
  autotrust:latest \
  python manage.py migrate
```

### 5️⃣ Levantar el contenedor en modo servicio
```bash
docker run -d \
  --name autotrust \
  --env-file docker.env \
  -v autotrust_data:/app/data \
  -p 8080:8080 \
  autotrust:latest
```

### 6️⃣ Verificar
```bash
docker logs -f autotrust
# y en otra terminal
curl http://localhost:8080/ --head
```

El contenedor expone Gunicorn en el puerto 8080 usando `autotrust.asgi:application` con trabajadores Uvicorn, e incluye archivos estáticos generados por `collectstatic` durante el build.

---

## 📂 Estructura del proyecto

```
Autotrust_DJ/
├── .venv/               # Entorno virtual
├── manage.py            # Script principal de Django
├── requirements.txt     # Dependencias del proyecto              # Archivos estáticos (CSS, JS, imágenes)
├── templates/           # Plantillas HTML
└── Vehicles/          # Aplicaciones Django (por ejemplo, vehicles/)
└── Account/
└── autotrust/
```

---

##  Autor
**Simon Castro** 
**Juan Andres Salcedo**  
**Santiago Villamizar**   


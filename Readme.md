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
Crea un archivo `.env` en la raíz del proyecto con tus configuraciones (si no existe aún).  
Ejemplo:
```env
DEBUG=True
SECRET_KEY=tu_clave_secreta
ALLOWED_HOSTS=127.0.0.1,localhost
```

---
## Link para Formato JSON proveedor del Servicio

```bash
http://127.0.0.1:8000/api/vehicles/
```

---

## 🐋 Docker


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


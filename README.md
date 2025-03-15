# 🚀 Money Manager - Sistema de Gestión Financiera Personal

![Money Manager Logo](https://via.placeholder.com/150x150.png?text=Money+Manager)

## 📋 Descripción

Money Manager es una aplicación web completa para la gestión de finanzas personales desarrollada con Django. Permite a los usuarios registrar, categorizar y visualizar sus ingresos y gastos, así como realizar transferencias entre usuarios, establecer presupuestos y monitorear su salud financiera a través de un intuitivo dashboard.

> ![TIP]
> Este proyecto fue diseñado con un enfoque modular para facilitar su mantenimiento y expansión.

---

## ✨ Características Principales

- **🏠 Dashboard Financiero**: Visualización gráfica de ingresos vs gastos
- **💸 Registro de Transacciones**: Gestión completa de ingresos y gastos con categorización
- **🔄 Transferencias**: Sistema para enviar y recibir dinero entre usuarios
- **📊 Presupuestos**: Definición de límites por categoría con alertas de excesos
- **👤 Perfiles Personalizados**: Configuración de moneda preferida y opciones de usuario
- **🔐 Sistema de Autenticación**: Registro, inicio de sesión y gestión de sesiones
- **🎨 Interfaz Responsiva**: Diseño adaptable a diferentes dispositivos

---

## 🛠️ Tecnologías Utilizadas

- **Backend**: Django 5.1, Python 3.9+
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 4.6
- **Visualización de Datos**: Chart.js
- **Iconos**: Font Awesome 5
- **Base de Datos**: SQLite (desarrollo), compatible con MySQL/PostgreSQL (producción)

> ![NOTE]
> Este proyecto utiliza una arquitectura MVT (Model-View-Template) típica de Django, pero con una organización modular mejorada.

---

## 📁 Estructura del Proyecto

```
money-manager-python/
│
├── finanzas/                # Aplicación principal
│   ├── admin/               # Configuración del panel de administración
│   ├── forms/               # Formularios para la entrada de datos
│   ├── migrations/          # Migraciones de la base de datos
│   ├── models/              # Modelos de datos (estructura de la BD)
│   ├── views/               # Vistas y lógica de negocio
│   ├── signals.py           # Señales para acciones automáticas
│   ├── apps.py              # Configuración de la aplicación
│   └── urls.py              # Rutas de la aplicación
│
├── money_manager/           # Configuración del proyecto
│   ├── settings.py          # Configuración principal
│   ├── urls.py              # Rutas del proyecto
│   ├── wsgi.py              # Configuración WSGI para despliegue
│   └── asgi.py              # Configuración ASGI para despliegue
│
├── templates/               # Plantillas HTML
│   ├── admin/               # Personalizaciones del admin
│   ├── finanzas/            # Plantillas de la aplicación
│   └── base.html            # Plantilla base
│
├── static/                  # Archivos estáticos (CSS, JS, imágenes)
│
├── manage.py                # Utilidad de línea de comandos
└── README.md                # Este archivo
```

---

## 🚀 Instalación y Configuración

### Prerrequisitos

- Python 3.9 o superior
- pip (gestor de paquetes de Python)
- Virtualenv (recomendado)

### Pasos de Instalación

1. **Clonar el repositorio**

```bash
git clone https://github.com/tu-usuario/money-manager-python.git
cd money-manager-python
```

2. **Crear y activar entorno virtual**

```bash
# En Windows
python -m venv venv
venv\Scripts\activate

# En macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

4. **Aplicar migraciones**

```bash
python manage.py migrate
```

5. **Crear superusuario**

```bash
python manage.py createsuperuser
```

6. **Iniciar servidor de desarrollo**

```bash
python manage.py runserver
```

> ![TIP]
> Para un entorno de producción, asegúrate de configurar un servidor web como Nginx o Apache junto con Gunicorn o uWSGI.



## 📸 Capturas de Pantalla

*(Reemplazar con capturas reales del proyecto)*

- **Dashboard Financiero**
- **Listado de Transacciones**
- **Formulario de Transferencia**
- **Panel de Presupuestos**
- **Perfil de Usuario**



## 🔧 Características Avanzadas

### Sistema de Signals

El proyecto utiliza el sistema de signals de Django para acciones automáticas:
- Creación automática de categorías predeterminadas para nuevos usuarios
- Actualización de saldos cuando se realizan transacciones

### Transacciones Atómicas

Las transferencias entre usuarios utilizan transacciones atómicas para garantizar la integridad de los datos, evitando problemas si una operación falla.

### Personalización del Admin

El panel de administración ha sido personalizado para proporcionar:
- Filtros específicos por usuario
- Visualización mejorada con gráficos
- Resúmenes y estadísticas

> ![TIP]
> Puedes extender fácilmente los modelos agregando nuevos archivos en la carpeta `models/` sin modificar la estructura existente.

---

## 👨‍💻 Desarrollado por

**Ing. Pontnau, Gonzalo Martín**

💼 [LinkedIn](https://linkedin.com/in/tu-perfil)
📧 [Email](mailto:tu-email@ejemplo.com)
🌐 [Portfolio](https://tu-sitio-web.com)

---

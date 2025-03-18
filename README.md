# 🚀 Money Manager - Sistema de Gestión Financiera Personal

![Web]()
[![Estado del Proyecto](https://img.shields.io/badge/Estado-Completado-success)](https://github.com/tu-usuario/money-manager-python)
[![Documentación](https://img.shields.io/badge/Documentación-Django-blue)](https://docs.djangoproject.com/)

## Descripción

Money Manager es una aplicación web completa para la gestión de finanzas personales desarrollada con Django. Permite a los usuarios registrar, categorizar y visualizar sus ingresos y gastos, así como realizar transferencias entre usuarios, establecer presupuestos y monitorear su salud financiera a través de un intuitivo dashboard.

> [!TIP]
> Este proyecto fue diseñado con un enfoque modular para facilitar su mantenimiento y expansión.

### Demostración

falta la demo

---

## Características Principales

- **Dashboard Financiero**: Visualización gráfica de ingresos vs gastos
- **Registro de Transacciones**: Gestión completa de ingresos y gastos con categorización
- **Transferencias**: Sistema para enviar y recibir dinero entre usuarios
- **Presupuestos**: Definición de límites por categoría con alertas de excesos
- **Perfiles Personalizados**: Configuración de moneda preferida y opciones de usuario
- **Sistema de Autenticación**: Registro, inicio de sesión y gestión de sesiones
- **Interfaz Responsiva**: Diseño adaptable a diferentes dispositivos
- **Notificaciones**: Alertas por correo electrónico para presupuestos y movimientos importantes
- **Búsqueda Avanzada**: Filtrado de transacciones por múltiples criterios

---

## Tecnologías Utilizadas

- **Backend**: Django 5, Python 3
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 4.6
- **Visualización de Datos**: Chart.js
- **Iconos**: Font Awesome 5
- **Base de Datos**:
  - **Desarrollo**: SQLite
  - **Producción**: PostgreSQL en Vercel (anteriormente MySQL)
- **Testing**: Django Test Framework, Pytest
- **Despliegue**: Vercel

> [!NOTE]
> Este proyecto utiliza una arquitectura MVT (Model-View-Template) típica de Django, pero con una organización modular mejorada.

---

## Estructura del Proyecto

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
│   ├── middleware.py        # Middleware personalizado para optimizaciones
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
├── static/                  # Archivos estáticos (CSS, JS)
│
├── manage.py                # Utilidad de línea de comandos
└── README.md                # Este archivo
```

---

## Instalación y Configuración

### Prerrequisitos

- Python 3.9 o superior
- pip (gestor de paquetes de Python)
- Virtualenv (recomendado)

### Pasos de Instalación

1. **Clonar el repositorio**

```bash
git clone https://github.com/PontnauGonzalo/money-manager-python
cd money-manager-python
```

2. **Crear y activar entorno virtual**

```bash
# En Windows
python -m venv venv
venv\Scripts\activate
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

> [!TIP]
> Para un entorno de producción, asegúrate de configurar un servidor web como Nginx o Apache junto con Gunicorn o uWSGI.

---

## 📸 Capturas de Pantalla

### Inicio de Sesión 
![Iniciar sesión](media/inicio-sesion.png)

### Dashboard Financiero
![Dashboard Financiero](media/dashboard.png)

### Listado de Transacciones
![Listado de Transacciones](media/transacciones-historial.png)

### Formulario de Transferencia
![Listado de Transacciones](media/formulario-transferencia.png)

---

## Características Avanzadas

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

> [!TIP]
> Puedes extender fácilmente los modelos agregando nuevos archivos en la carpeta `models/` sin modificar la estructura existente.

---

## Despliegue en Vercel

El proyecto está desplegado en Vercel, aprovechando su plataforma para aplicaciones web. Algunos aspectos importantes del despliegue:

### Migración de Base de Datos

- **Desarrollo**: Inicialmente se utilizaba SQLite para desarrollo local y MySQL para entornos de producción.
- **Producción actual**: Al migrar a Vercel, se cambió a PostgreSQL debido a su mejor compatibilidad con la plataforma y mayor rendimiento para aplicaciones web.
- **Adaptación**: El proyecto incluye configuraciones automáticas que detectan el entorno de despliegue y utilizan la base de datos apropiada sin necesidad de modificar el código.

### Optimizaciones Implementadas

- **Middleware de Caché**: middleware personalizado para mejorar el rendimiento mediante caché de recursos estáticos.
- **Consultas Optimizadas**: Se utilizan `select_related` y `prefetch_related` para reducir el número de consultas a la base de datos.
- **MutationObserver**: Reemplacé los intervals de sondeo por MutationObserver para mejorar el rendimiento del frontend.

---

## Estado del Proyecto

El proyecto está actualmente **completado** y en fase de mantenimiento. Se aceptan sugerencias y mejoras.

---

## Lecciones Aprendidas y Desafíos

- La importancia de una arquitectura modular para facilitar el mantenimiento
- Cómo implementar transacciones atómicas en Django
- La personalización del panel de administración para mejorar la usabilidad

### Migración de Base de Datos y Despliegue

- **Portabilidad de Django ORM**: El ORM de Django permitió migrar entre diferentes sistemas de bases de datos (SQLite, MySQL, PostgreSQL) con mínimos cambios de código.
- **Compatibilidad de Vercel**: Aprendí a configurar aplicaciones Django para Vercel, incluyendo la integración con PostgreSQL.
- **Uso de Variables de Entorno**: La configuración basada en variables de entorno facilitó el despliegue en distintos entornos sin cambios en el código.

Algunos de los desafíos enfrentados incluyen:

- Garantizar la integridad de los datos durante las transferencias
- Optimizar las consultas a la base de datos para mejorar el rendimiento
- Manejar la migración de datos entre diferentes sistemas de bases de datos

---

## 👨‍💻 Desarrollado por

**Ing. Pontnau, Gonzalo Martín**

💼 [LinkedIn](https://linkedin.com/in/gonzalopontnau)
📧 [Email](mailto:gonzalopontnau@gmail.com)

---

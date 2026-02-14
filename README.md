# Money Manager

**Sistema de gestión financiera personal con asistente de IA integrado**

[![Demo en vivo](https://img.shields.io/badge/Demo-Online-D4A574?style=for-the-badge&logo=vercel&logoColor=white)](https://money-manager-nine-umber.vercel.app/)
[![Django](https://img.shields.io/badge/Django-5-092E20?style=for-the-badge&logo=django&logoColor=white)](https://docs.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://docs.python.org/3/)

---

## Demo

### Inicio de Sesión

![demo-inicio-de-sesion](https://github.com/user-attachments/assets/fcf3ba73-6a65-4676-8ecc-53ed0bc90e3e)

### Dashboard Financiero

![demo-dashboard](https://github.com/user-attachments/assets/c9fb37fc-96da-4f89-a0e5-164169e6c77a)

### Registro Ingreso/Gasto

![demo-ingreso-gasto](https://github.com/user-attachments/assets/d58cea05-0bdc-471b-8161-0cf16a9e653f)

### Formulario de Transferencia

![demo-transferencia](https://github.com/user-attachments/assets/50f8105d-3f29-47fb-8c3e-f6869b5b3785)

---

## Características

### Gestión Financiera

- **Dashboard interactivo** — gráficos de ingresos vs gastos con Chart.js
- **Transacciones** — registro completo de ingresos y gastos con categorización
- **Transferencias** — envío y recepción de dinero entre usuarios con transacciones atómicas
- **Presupuestos** — límites por categoría con alertas de exceso
- **Filtrado avanzado** — búsqueda de transacciones por fecha, categoría, tipo y monto

### Asistente FinBot

- **Chat con IA** — consultas financieras en lenguaje natural (español e inglés)
- **RAG Pipeline** — búsqueda semántica sobre transacciones con Qdrant + HuggingFace
- **Contexto en tiempo real** — balance, gastos por categoría, presupuestos y últimas transacciones
- **Follow-up inteligente** — cuando la consulta necesita más información, sugiere opciones
- **Widget flotante** — accesible desde cualquier página sin interrumpir la navegación

### Infraestructura

- **Interfaz responsiva** — diseño adaptable a cualquier dispositivo
- **Design system** — dark mode con paleta dorada y tokens CSS
- **Auto-embedding** — cada transacción se vectoriza automáticamente vía signals
- **Despliegue serverless** — Vercel + Neon PostgreSQL

> [!NOTE]
> Consulta la [documentación completa del chatbot](docs/CHATBOT.md) y la [arquitectura del proyecto](docs/ARCHITECTURE.md) para información técnica detallada.

---

## Stack Tecnológico

| Capa                   | Tecnología                                            |
| ---------------------- | ----------------------------------------------------- |
| **Backend**            | Django 5 · Python 3                                   |
| **Frontend**           | HTML5 · CSS3 · JavaScript · Chart.js · Font Awesome 6 |
| **LLM**                | Groq API (compatible OpenAI)                          |
| **Embeddings**         | HuggingFace (`all-MiniLM-L6-v2`, 384 dims)            |
| **Vector DB**          | Qdrant Cloud (cosine similarity)                      |
| **BD relacional**      | SQLite (dev) · PostgreSQL / Neon (prod)               |
| **Hosting**            | Vercel (serverless)                                   |
| **Archivos estáticos** | WhiteNoise                                            |

---

## Estructura del Proyecto

```
money-manager-python/
│
├── chatbot/                    # App FinBot — Asistente IA
│   ├── models/                 # ConversationMessage
│   ├── prompts/                # System prompt del LLM
│   ├── services/               # RAG Pipeline, LLM, Embeddings, Qdrant,
│   │                           #   Financial Context, Follow-up Detector
│   ├── views/                  # API endpoints del chat
│   ├── signals.py              # Auto-embedding de transacciones
│   └── templatetags/           # Widget template tag
│
├── finanzas/                   # App principal — Gestión financiera
│   ├── admin/                  # Admin personalizado con gráficos
│   ├── forms/                  # Formularios de entrada
│   ├── models/                 # Categoria, Transaccion, Transferencia,
│   │                           #   PerfilUsuario, Presupuesto
│   ├── views/                  # Auth, Dashboard, Transacciones, Transferencias
│   ├── middleware.py           # CachingMiddleware
│   └── signals.py              # Categorías default + saldo inicial
│
├── money_manager/              # Configuración del proyecto Django
│   └── settings.py             # Auto-detección de entorno (dev/prod)
│
├── templates/                  # Plantillas HTML
│   ├── base.html               # Layout base + navbar + chatbot widget
│   ├── chatbot/                # Widget flotante
│   └── finanzas/               # Dashboard, login, transacciones, etc.
│
├── static/                     # CSS + JS
│   ├── css/styles.css          # Design system (dark mode dorado)
│   ├── css/chatbot.css         # Estilos del chat widget
│   └── js/chatbot.js           # Lógica del widget
│
├── docs/                       # Documentación
│   ├── ARCHITECTURE.md         # Arquitectura y diagramas
│   ├── CHATBOT.md              # Documentación del agente FinBot
│   └── API.md                  # Referencia de endpoints
│
├── requirements.txt
├── vercel.json
└── build_files.sh
```

---

## Instalación y Configuración

### Prerrequisitos

- Python 3.9+
- pip

### Instalación Local

```bash
# 1. Clonar el repositorio
git clone https://github.com/PontnauGonzalo/money-manager-python
cd money-manager-python

# 2. Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate    # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys (ver sección siguiente)

# 5. Aplicar migraciones
python manage.py migrate

# 6. Crear superusuario
python manage.py createsuperuser

# 7. Iniciar servidor
python manage.py runserver
```

### Variables de Entorno

Crear un archivo `.env` en la raíz del proyecto:

```env
# Django
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=true

# Base de datos (opcional, usa SQLite por defecto)
# DATABASE_URL=postgresql://user:pass@host:5432/dbname

# FinBot — Chatbot IA (requeridas para el asistente)
GROQ_API_KEY=gsk_xxxxx
GROQ_MODEL=openai/gpt-oss-120
QDRANT_URL=https://xxx.qdrant.io
QDRANT_API_KEY=xxxxx
HF_API_TOKEN=hf_xxxxx
```

> [!TIP]
> El chatbot funciona sin las API keys, pero las consultas de IA no estarán disponibles. El resto de la app funciona normalmente.

---

## Arquitectura del Chatbot

FinBot utiliza un pipeline **RAG (Retrieval-Augmented Generation)** que combina datos financieros reales con generación de texto por LLM:

```
Usuario → Intent Detection → Financial Context + Semantic Search → LLM → Respuesta
```

1. **Detección de intención** — clasifica la consulta y determina si necesita follow-up
2. **Contexto financiero** — obtiene balance, gastos, presupuestos desde Django ORM
3. **Búsqueda semántica** — genera embedding del mensaje y busca transacciones similares en Qdrant
4. **Generación** — envía todo al LLM (Groq) con el historial de conversación

> [!NOTE]
> Cada transacción se vectoriza automáticamente al crearse/editarse/eliminarse mediante Django signals, manteniendo Qdrant sincronizado.

**Documentación detallada:** [docs/CHATBOT.md](docs/CHATBOT.md) | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | [docs/API.md](docs/API.md)

---

## Características Técnicas Destacadas

### Transacciones Atómicas

Las transferencias entre usuarios utilizan `transaction.atomic()` para garantizar la integridad de los datos.

### Auto-Embedding de Transacciones

Los Django signals generan embeddings automáticamente al crear/editar/eliminar transacciones, manteniendo el vector store de Qdrant siempre sincronizado.

### Sistema de Signals

- **Categorías default** — se crean automáticamente al registrarse un usuario
- **Saldo inicial** — monto de prueba asignado a nuevos usuarios
- **Vectorización** — cada transacción se embede en Qdrant

### Middleware Personalizado

- `CachingMiddleware` para optimización de recursos estáticos
- `WhiteNoise` para servir archivos estáticos en producción
- `GZipMiddleware` para compresión de respuestas

### Admin Personalizado

Panel de administración con filtros por usuario, gráficos y estadísticas.

---

## Despliegue

El proyecto está desplegado en **Vercel** con **PostgreSQL en Neon** (serverless):

- Auto-detección de entorno (SQLite local ↔ PostgreSQL producción)
- WhiteNoise para archivos estáticos comprimidos
- CSRF + SSL correctamente configurados para HTTPS
- Variables de entorno gestionadas desde el dashboard de Vercel

---

## Documentación

| Documento                               | Descripción                                                 |
| --------------------------------------- | ----------------------------------------------------------- |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Arquitectura general, diagramas de flujo, stack tecnológico |
| [CHATBOT.md](docs/CHATBOT.md)           | Documentación completa del asistente FinBot                 |
| [API.md](docs/API.md)                   | Referencia de endpoints de la API                           |

---

## Desarrollado por

**Ing. Pontnau, Gonzalo Martín**

[LinkedIn](https://linkedin.com/in/gonzalopontnau) </br>
[Email](mailto:gonzalopontnau@gmail.com) </br>
[Portfolio](https://gonzalopontnau.vercel.app/)

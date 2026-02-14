# 🤖 FinBot — Asistente Financiero con IA

FinBot es un chatbot conversacional integrado en Money Manager que permite a los usuarios consultar su información financiera usando lenguaje natural. Utiliza una arquitectura **RAG (Retrieval-Augmented Generation)** para combinar datos reales del usuario con la capacidad generativa de un LLM.

---

## Características

- 💬 **Conversación natural** en español e inglés (detección automática de idioma)
- 📊 **Consultas financieras** sobre balance, gastos, ingresos, presupuestos y transferencias
- 🔍 **Búsqueda semántica** de transacciones usando embeddings vectoriales
- 🧠 **Contexto financiero en tiempo real** inyectado en cada consulta
- 🔄 **Follow-up inteligente** cuando la consulta necesita más detalle
- 💾 **Historial de conversación** persistente por sesión
- 🫧 **Widget flotante** no intrusivo en todas las páginas

---

## Arquitectura RAG

```
┌─────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Usuario    │───▶│ Intent Detector  │───▶│  Follow-up?     │
│  (mensaje)   │    │  (regex-based)   │    │  Sí → respuesta │
└─────────────┘    └──────────────────┘    │  No → continuar  │
                                           └────────┬────────┘
                                                    │
                   ┌────────────────────────────────┘
                   ▼
    ┌──────────────────────────┐
    │   Contexto Financiero    │  ← Django ORM queries
    │   (balance, gastos,      │
    │    presupuestos, etc.)   │
    └──────────────────────────┘
                   │
                   ▼
    ┌──────────────────────────┐    ┌─────────────────┐
    │   Embedding del mensaje  │───▶│  Qdrant Search   │
    │   (HuggingFace API)      │    │  (top-5 similar) │
    └──────────────────────────┘    └────────┬────────┘
                                             │
                   ┌─────────────────────────┘
                   ▼
    ┌──────────────────────────┐    ┌─────────────────┐
    │   System Prompt +        │───▶│   Groq LLM      │
    │   Contexto + RAG +       │    │   (respuesta)    │
    │   Historial conversación │    └────────┬────────┘
    └──────────────────────────┘             │
                                             ▼
                                    ┌─────────────────┐
                                    │ Respuesta final  │
                                    │ al usuario       │
                                    └─────────────────┘
```

---

## Componentes

### 1. RAG Pipeline (`services/rag_pipeline.py`)

Orquestador principal. Recibe un mensaje del usuario y coordina todos los pasos:

1. **Guarda** el mensaje del usuario en `ConversationMessage`
2. **Carga** el historial de conversación (últimos N mensajes)
3. **Detecta intención** y evalúa si necesita follow-up
4. **Construye contexto financiero** desde las queries de Django
5. **Genera embedding** del mensaje y busca transacciones similares en Qdrant
6. **Ensambla el prompt** con contexto + resultados RAG + historial
7. **Llama al LLM** y guarda la respuesta

### 2. Intent / Follow-up Detector (`services/followup_detector.py`)

Detecta la intención del usuario usando patrones de keywords y determina si se necesita una pregunta de follow-up:

| Intención            | Keywords (ejemplo)                 | Requiere            |
| -------------------- | ---------------------------------- | ------------------- |
| `balance_check`      | "saldo", "balance", "cuánto tengo" | —                   |
| `spending_query`     | "gastos", "cuánto gasté"           | Período temporal    |
| `category_query`     | "categoría", "en qué gasto"        | Período temporal    |
| `budget_status`      | "presupuesto", "límite"            | —                   |
| `transaction_search` | "buscar", "transacción"            | Detalle de búsqueda |
| `income_query`       | "ingreso", "salario"               | —                   |
| `transfer_query`     | "transferencia", "envié"           | —                   |

Si la consulta requiere información que no está presente (ej: "¿cuánto gasté?" sin período), el sistema genera una pregunta de follow-up con opciones clickeables.

### 3. Financial Context Builder (`services/financial_context.py`)

Construye un resumen textual del estado financiero del usuario que se inyecta en el prompt del LLM:

- **Balance actual** (ingresos totales - gastos totales)
- **Gastos del mes** desglosados por categoría
- **Estado de presupuestos** (porcentaje usado, excedidos)
- **Últimas 10 transacciones**
- **Categorías del usuario** (ingreso y gasto)

### 4. Embedding Service (`services/embedding_service.py`)

Cliente de la API de Inferencia de HuggingFace para generar embeddings con el modelo `sentence-transformers/all-MiniLM-L6-v2` (384 dimensiones).

### 5. Qdrant Service (`services/qdrant_service.py`)

Gestiona la base de datos vectorial Qdrant:

- **`ensure_collection()`** — Crea la colección si no existe
- **`upsert_transaction()`** — Inserta/actualiza un vector con payload financiero
- **`delete_point()`** — Elimina un vector cuando se borra una transacción
- **`search_similar()`** — Búsqueda semántica filtrada por usuario (cosine similarity)

> **Payload almacenado por cada transacción:**
> `user_id`, `tipo`, `monto`, `categoria`, `descripcion`, `fecha`

### 6. LLM Service (`services/llm_service.py`)

Cliente de la API de Groq (compatible con formato OpenAI chat completions):

- Modelo configurable vía `GROQ_MODEL`
- Temperature: 0.3 (respuestas focalizadas)
- Max tokens: 1024 (configurable)
- Timeout: 25 segundos

### 7. System Prompt (`prompts/system_prompts.py`)

El prompt del sistema instruye al LLM a:

- Responder en el **mismo idioma** que el usuario
- Usar **únicamente** los datos financieros proporcionados
- Formatear montos con `$` y dos decimales
- Ser conciso y usar bullet points
- Redirigir amablemente consultas no financieras

---

## Auto-Embedding vía Signals

Cuando una transacción se crea, edita o elimina, los **signals de Django** automáticamente:

```python
# chatbot/signals.py

@receiver(post_save, sender=Transaccion)
def embed_transaction_on_save(sender, instance, **kwargs):
    text = _generate_transaction_text(instance)  # "Gasto de $150 en Compras el 14/02/2026"
    embedding = get_embedding(text)               # → vector 384-dim
    upsert_transaction(instance, embedding)       # → Qdrant

@receiver(post_delete, sender=Transaccion)
def remove_transaction_embedding(sender, instance, **kwargs):
    delete_point(instance.id)                     # → elimina de Qdrant
```

Esto garantiza que el vector store está **siempre sincronizado** con la base de datos relacional.

---

## Modelo de Datos

```python
class ConversationMessage(Model):
    usuario       = ForeignKey(User)       # Propietario
    session_id    = CharField(max_length=64)# Agrupa mensajes en conversaciones
    role          = CharField()             # 'user' | 'assistant' | 'system'
    content       = TextField()             # Contenido del mensaje
    is_followup_question = BooleanField()   # ¿Es pregunta de follow-up?
    created_at    = DateTimeField()         # Timestamp
```

---

## API Endpoints

| Método | Endpoint                                    | Descripción                        |
| ------ | ------------------------------------------- | ---------------------------------- |
| `POST` | `/chatbot/api/chat/send/`                   | Enviar mensaje y recibir respuesta |
| `GET`  | `/chatbot/api/chat/history/?session_id=...` | Obtener historial de una sesión    |
| `POST` | `/chatbot/api/chat/new/`                    | Iniciar nueva conversación         |

Ver [API.md](API.md) para detalles completos.

---

## Frontend — Widget Flotante

El widget se compone de:

- **Template**: `templates/chatbot/chatbot_widget.html` — inyectado con template tag `{% chatbot_widget %}`
- **CSS**: `static/css/chatbot.css` — design system con tokens `--cb-*` vinculados a los globals
- **JS**: `static/js/chatbot.js` — IIFE con gestión de estado, DOM y fetch API

### Flujo UI

1. **Burbuja flotante** fija en esquina inferior derecha
2. Click → **panel de chat** se abre con animación
3. **Suggestion chips** para consultas rápidas ("Mi balance", "Gastos del mes", "Presupuestos")
4. Área de mensajes con burbujas diferenciadas usuario/asistente
5. **Indicador de escritura** animado mientras procesa
6. **Follow-up buttons** cuando el bot necesita más información
7. Botón **nueva conversación** para resetear sesión

---

## Configuración

Variables de entorno requeridas en `.env`:

```env
GROQ_API_KEY=gsk_xxxxx          # API key de Groq
GROQ_MODEL=openai/gpt-oss-120   # Modelo LLM (opcional)
QDRANT_URL=https://xxx.qdrant.io # URL del cluster Qdrant
QDRANT_API_KEY=xxxxx             # API key de Qdrant
HF_API_TOKEN=hf_xxxxx           # Token de HuggingFace
```

Parámetros en `settings.py`:

```python
CHATBOT_MAX_HISTORY = 10   # Mensajes de historial enviados al LLM
CHATBOT_MAX_TOKENS = 1024  # Max tokens en respuesta del LLM
```

# API Reference — Money Manager

## Autenticación

Todos los endpoints requieren que el usuario esté autenticado (session-based auth de Django). Las peticiones POST requieren el header `X-CSRFToken` con un token CSRF válido.

---

## Chatbot API

Base URL: `/chatbot/api/chat/`

### Enviar Mensaje

```
POST /chatbot/api/chat/send/
```

Envía un mensaje al asistente FinBot y recibe la respuesta generada por IA.

**Headers:**

```
Content-Type: application/json
X-CSRFToken: <csrf_token>
```

**Request Body:**

```json
{
  "message": "¿Cuál es mi balance actual?",
  "session_id": "chat_1707937200_abc123xyz"
}
```

| Campo        | Tipo   | Requerido | Descripción                        |
| ------------ | ------ | --------- | ---------------------------------- |
| `message`    | string | Sí        | Mensaje del usuario                |
| `session_id` | string | Sí        | Identificador de la sesión de chat |

**Response (200):**

```json
{
  "response": "Tu balance actual es de $850.00...",
  "is_followup": false,
  "followup_options": null,
  "session_id": "chat_1707937200_abc123xyz"
}
```

**Response con Follow-up (200):**

```json
{
  "response": "¿De qué período te gustaría saber tus gastos?",
  "is_followup": true,
  "followup_options": ["Este mes", "Último trimestre", "Este año", "Todo"],
  "session_id": "chat_1707937200_abc123xyz"
}
```

| Campo              | Tipo             | Descripción                            |
| ------------------ | ---------------- | -------------------------------------- |
| `response`         | string           | Respuesta del asistente                |
| `is_followup`      | boolean          | `true` si es una pregunta de follow-up |
| `followup_options` | string[] \| null | Opciones sugeridas para responder      |
| `session_id`       | string           | ID de sesión (eco)                     |

**Errores:**

| Status | Descripción                                        |
| ------ | -------------------------------------------------- |
| `400`  | JSON inválido, mensaje vacío o session_id faltante |
| `403`  | No autenticado                                     |

---

### Obtener Historial

```
GET /chatbot/api/chat/history/?session_id=<session_id>
```

Recupera el historial de mensajes de una sesión de chat.

**Query Params:**

| Parámetro    | Tipo   | Requerido | Descripción                |
| ------------ | ------ | --------- | -------------------------- |
| `session_id` | string | Sí        | Identificador de la sesión |

**Response (200):**

```json
{
  "messages": [
    {
      "role": "user",
      "content": "¿Cuánto gasté este mes?",
      "is_followup": false,
      "timestamp": "2026-02-14T17:30:00.000000+00:00"
    },
    {
      "role": "assistant",
      "content": "Este mes tus gastos ascienden a $450.00...",
      "is_followup": false,
      "timestamp": "2026-02-14T17:30:02.500000+00:00"
    }
  ],
  "session_id": "chat_1707937200_abc123xyz"
}
```

---

### Nueva Conversación

```
POST /chatbot/api/chat/new/
```

Placeholder para iniciar una nueva sesión de conversación. La generación de `session_id` se realiza del lado del cliente.

**Response (200):**

```json
{
  "status": "ok"
}
```

---

## Finanzas — Rutas Web

Las siguientes rutas corresponden a vistas web (renderizado HTML) y no son endpoints REST API.

| Ruta                            | Vista                   | Descripción                                           |
| ------------------------------- | ----------------------- | ----------------------------------------------------- |
| `/`                             | `dashboard`             | Dashboard principal con resumen financiero y gráficos |
| `/login/`                       | `login_view`            | Inicio de sesión                                      |
| `/register/`                    | `register`              | Registro de nuevo usuario                             |
| `/logout/`                      | `logout_view`           | Cerrar sesión                                         |
| `/transacciones/`               | `lista_transacciones`   | Listado de transacciones con filtros                  |
| `/transacciones/nueva/`         | `nueva_transaccion`     | Crear nueva transacción                               |
| `/transacciones/<id>/`          | `detalle_transaccion`   | Detalle de una transacción                            |
| `/transacciones/<id>/editar/`   | `editar_transaccion`    | Editar transacción existente                          |
| `/transacciones/<id>/eliminar/` | `eliminar_transaccion`  | Confirmar y eliminar transacción                      |
| `/transferencias/`              | `lista_transferencias`  | Listado de transferencias                             |
| `/transferencias/nueva/`        | `nueva_transferencia`   | Crear nueva transferencia                             |
| `/transferencias/<id>/`         | `detalle_transferencia` | Detalle de una transferencia                          |

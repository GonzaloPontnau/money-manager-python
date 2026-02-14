import re

# Intent patterns with keywords and follow-up requirements
INTENT_PATTERNS = {
    'balance_check': {
        'keywords': [
            'balance', 'saldo', 'cuanto tengo', 'cuánto tengo',
            'dinero disponible', 'how much', 'my balance', 'total',
        ],
        'requires': [],
    },
    'spending_query': {
        'keywords': [
            'gaste', 'gasté', 'gastos', 'cuanto gaste', 'cuánto gasté',
            'spent', 'spending', 'expenses', 'how much did i spend',
        ],
        'requires': ['time_period'],
        'followup_es': '¿De qué período te gustaría saber tus gastos?',
        'followup_en': 'What time period would you like to check your spending for?',
        'options': ['Este mes', 'Último trimestre', 'Este año', 'Todo'],
    },
    'category_query': {
        'keywords': [
            'categoria', 'categoría', 'en que gasto', 'en qué gasto',
            'donde gasto', 'dónde gasto', 'category', 'where do i spend',
            'what do i spend on',
        ],
        'requires': ['time_period'],
        'followup_es': '¿Qué período te interesa analizar?',
        'followup_en': 'What time period would you like to analyze?',
        'options': ['Este mes', 'Últimos 3 meses', 'Este año'],
    },
    'budget_status': {
        'keywords': [
            'presupuesto', 'budget', 'limite', 'límite', 'excedido',
            'over budget', 'budget status',
        ],
        'requires': [],
    },
    'transaction_search': {
        'keywords': [
            'transaccion', 'transacción', 'buscar', 'encontrar',
            'compra', 'pago', 'transaction', 'find', 'search', 'payment',
        ],
        'requires': ['search_detail'],
        'followup_es': '¿Podrías ser más específico? ¿Buscas por monto, descripción o categoría?',
        'followup_en': 'Could you be more specific? Are you searching by amount, description, or category?',
        'options': ['Por monto', 'Por descripción', 'Por categoría'],
    },
    'income_query': {
        'keywords': [
            'ingreso', 'ingresos', 'gano', 'gané', 'salario',
            'income', 'earnings', 'how much did i earn',
        ],
        'requires': [],
    },
    'transfer_query': {
        'keywords': [
            'transferencia', 'transferencias', 'envié', 'recibí',
            'transfer', 'sent', 'received',
        ],
        'requires': [],
    },
    'general': {
        'keywords': [],
        'requires': [],
    },
}

# Temporal markers that satisfy the 'time_period' requirement
TIME_MARKERS = [
    r'este mes', r'mes actual', r'this month',
    r'mes pasado', r'último mes', r'last month',
    r'esta semana', r'this week',
    r'hoy', r'today', r'ayer', r'yesterday',
    r'este año', r'this year', r'año pasado', r'last year',
    r'último trimestre', r'last quarter', r'trimestre',
    r'últimos \d+ meses', r'last \d+ months',
    r'enero|febrero|marzo|abril|mayo|junio',
    r'julio|agosto|septiembre|octubre|noviembre|diciembre',
    r'january|february|march|april|may|june',
    r'july|august|september|october|november|december',
    r'\d{4}',  # A year like 2025, 2026
    r'\d{1,2}/\d{1,2}',  # A date like 15/02
    r'todo', r'all', r'siempre', r'always',
]

# Detail markers that satisfy the 'search_detail' requirement
DETAIL_MARKERS = [
    r'\$?\d+[\.,]?\d*',  # An amount like $150 or 150.50
    r'monto', r'amount',
    r'descripcion', r'descripción', r'description',
    r'categoría', r'categoria', r'category',
]


def _detect_language(message):
    """Simple language detection based on common words and Spanish content words."""
    spanish_markers = [
        'mi', 'mis', 'el', 'la', 'los', 'las', 'de', 'en', 'que', 'qué',
        'cuanto', 'cuánto', 'como', 'cómo', 'donde', 'dónde', 'por', 'para',
    ]
    # Also detect Spanish from financial keywords in the message
    spanish_content = [
        'gasto', 'gastos', 'gaste', 'gasté', 'ingreso', 'ingresos',
        'saldo', 'balance', 'presupuesto', 'categoría', 'categoria',
        'transferencia', 'transaccion', 'transacción', 'salario',
        'cuanto', 'cuánto', 'envié', 'recibí', 'buscar', 'encontrar',
    ]
    english_markers = [
        'my', 'the', 'how', 'what', 'where', 'when', 'much', 'did',
        'spend', 'spent', 'income', 'budget', 'search', 'find',
    ]
    msg_lower = message.lower()
    words = msg_lower.split()
    es_score = sum(1 for w in words if w in spanish_markers or w in spanish_content)
    en_score = sum(1 for w in words if w in english_markers)
    if es_score > en_score:
        return 'es'
    if en_score > es_score:
        return 'en'
    # Default to Spanish (app's primary language)
    return 'es'


def _has_time_period(message):
    """Check if the message already contains a time period reference."""
    msg_lower = message.lower()
    return any(re.search(pattern, msg_lower) for pattern in TIME_MARKERS)


def _has_search_detail(message):
    """Check if the message contains enough detail for a search."""
    msg_lower = message.lower()
    return any(re.search(pattern, msg_lower) for pattern in DETAIL_MARKERS)


def detect_intent(message, last_bot_was_followup=False):
    """
    Detect user intent and determine if a follow-up question is needed.

    Args:
        message: The user's message text
        last_bot_was_followup: True if the previous bot message was a follow-up question

    Returns:
        (intent, needs_followup, followup_message, followup_options)
    """
    # If the user is answering a follow-up, skip detection
    if last_bot_was_followup:
        return ('general', False, None, None)

    msg_lower = message.lower()
    lang = _detect_language(message)

    # Match against intent patterns
    matched_intent = 'general'
    for intent_key, pattern in INTENT_PATTERNS.items():
        if intent_key == 'general':
            continue
        for keyword in pattern['keywords']:
            if keyword in msg_lower:
                matched_intent = intent_key
                break
        if matched_intent != 'general':
            break

    pattern = INTENT_PATTERNS.get(matched_intent, INTENT_PATTERNS['general'])
    requires = pattern.get('requires', [])

    # Check if required info is already in the message
    needs_followup = False
    if 'time_period' in requires and not _has_time_period(message):
        needs_followup = True
    if 'search_detail' in requires and not _has_search_detail(message):
        needs_followup = True

    if needs_followup:
        followup_key = 'followup_es' if lang == 'es' else 'followup_en'
        followup_msg = pattern.get(followup_key, pattern.get('followup_es', ''))
        options = pattern.get('options', [])
        return (matched_intent, True, followup_msg, options)

    return (matched_intent, False, None, None)

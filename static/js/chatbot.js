(function () {
    'use strict';

    // --- State ---
    var sessionId = generateSessionId();
    var isOpen = false;
    var isProcessing = false;

    // --- DOM refs (set in init) ---
    var el = {};

    function init() {
        el = {
            toggle: document.getElementById('chatbot-toggle'),
            panel: document.getElementById('chatbot-panel'),
            close: document.getElementById('chatbot-close'),
            newChat: document.getElementById('chatbot-new-chat'),
            messages: document.getElementById('chatbot-messages'),
            input: document.getElementById('chatbot-input'),
            send: document.getElementById('chatbot-send'),
            typing: document.getElementById('chatbot-typing'),
            followupArea: document.getElementById('chatbot-followup-options'),
            suggestions: document.getElementById('chatbot-suggestions'),
        };

        if (!el.toggle) return; // User not authenticated

        el.toggle.addEventListener('click', toggleChat);
        el.close.addEventListener('click', toggleChat);
        el.send.addEventListener('click', sendMessage);
        el.newChat.addEventListener('click', startNewConversation);

        el.input.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // Suggestion chips
        var chips = document.querySelectorAll('.suggestion-chip');
        for (var i = 0; i < chips.length; i++) {
            chips[i].addEventListener('click', function () {
                el.input.value = this.getAttribute('data-message');
                sendMessage();
            });
        }
    }

    function toggleChat() {
        isOpen = !isOpen;
        if (isOpen) {
            el.panel.classList.add('open');
            el.toggle.classList.add('hidden');
            el.input.focus();
        } else {
            el.panel.classList.remove('open');
            el.toggle.classList.remove('hidden');
        }
    }

    function sendMessage() {
        var message = el.input.value.trim();
        if (!message || isProcessing) return;

        isProcessing = true;
        el.input.value = '';
        el.send.disabled = true;

        // Hide suggestions and follow-up options
        el.suggestions.classList.add('hidden');
        el.followupArea.classList.remove('visible');

        // Add user message to UI
        appendMessage('user', message);

        // Show typing indicator
        el.typing.classList.add('visible');
        scrollToBottom();

        // Send to backend
        fetch('/chatbot/api/chat/send/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify({
                message: message,
                session_id: sessionId,
            }),
        })
        .then(function (res) { return res.json(); })
        .then(function (data) {
            el.typing.classList.remove('visible');

            appendMessage('assistant', data.response);

            if (data.is_followup && data.followup_options) {
                showFollowupOptions(data.followup_options);
            }

            isProcessing = false;
            el.send.disabled = false;
        })
        .catch(function () {
            el.typing.classList.remove('visible');
            appendMessage(
                'assistant',
                'Lo siento, hubo un error al procesar tu consulta. Intenta de nuevo.'
            );
            isProcessing = false;
            el.send.disabled = false;
        });
    }

    function appendMessage(role, content) {
        var msgDiv = document.createElement('div');
        msgDiv.className = 'chat-message ' + role;

        var avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.innerHTML = role === 'assistant'
            ? '<i class="fas fa-robot"></i>'
            : '<i class="fas fa-user"></i>';

        var bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'message-bubble';
        bubbleDiv.textContent = content;

        msgDiv.appendChild(avatarDiv);
        msgDiv.appendChild(bubbleDiv);

        el.messages.appendChild(msgDiv);
        scrollToBottom();
    }

    function showFollowupOptions(options) {
        el.followupArea.innerHTML = '';
        for (var i = 0; i < options.length; i++) {
            var btn = document.createElement('button');
            btn.className = 'followup-btn';
            btn.textContent = options[i];
            btn.addEventListener('click', (function (opt) {
                return function () {
                    el.input.value = opt;
                    sendMessage();
                };
            })(options[i]));
            el.followupArea.appendChild(btn);
        }
        el.followupArea.classList.add('visible');
    }

    function startNewConversation() {
        sessionId = generateSessionId();
        el.messages.innerHTML = '';

        // Re-add welcome message
        appendMessage(
            'assistant',
            'Nueva conversación iniciada. ¿En qué puedo ayudarte?'
        );

        el.suggestions.classList.remove('hidden');
        el.followupArea.classList.remove('visible');
    }

    function scrollToBottom() {
        el.messages.scrollTop = el.messages.scrollHeight;
    }

    function generateSessionId() {
        return 'chat_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    function getCsrfToken() {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var c = cookies[i].trim();
            if (c.indexOf('csrftoken=') === 0) {
                return c.substring('csrftoken='.length);
            }
        }
        return '';
    }

    // --- Init on DOM ready ---
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();

// Состояние
let currentUserId = null;
let currentMode = 'study';

// DOM элементы
const chatMessages = document.getElementById('chat-messages');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const modeDisplay = document.getElementById('mode-display');

// Генерация или получение user_id из localStorage
function getUserId() {
    let userId = localStorage.getItem('fred_user_id');
    if (!userId) {
        userId = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 8);
        localStorage.setItem('fred_user_id', userId);
    }
    return userId;
}

// Добавление сообщения в чат
function addMessage(text, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : 'assistant'}`;
    messageDiv.innerHTML = text.replace(/\n/g, '<br>');
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return messageDiv;
}

// Добавление индикатора печати
function addTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message assistant typing';
    typingDiv.id = 'typing-indicator';
    typingDiv.innerHTML = 'Фрэд печатает...';
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return typingDiv;
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) indicator.remove();
}

// Отправка сообщения на сервер
async function sendMessage(message, mode) {
    const typingIndicator = addTypingIndicator();
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: currentUserId,
                message: message,
                mode: mode
            })
        });
        
        removeTypingIndicator();
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        addMessage(data.reply, false);
        
    } catch (error) {
        removeTypingIndicator();
        console.error('Ошибка:', error);
        addMessage('😕 Упс... Что-то пошло не так. Попробуй ещё раз.', false);
    }
}

// Обработка отправки сообщения
async function handleSend() {
    const message = messageInput.value.trim();
    if (!message) return;
    
    // Добавляем сообщение пользователя в чат
    addMessage(message, true);
    messageInput.value = '';
    messageInput.style.height = 'auto';
    
    // Отправляем на сервер
    await sendMessage(message, currentMode);
}

// Смена режима
function setMode(mode) {
    currentMode = mode;
    modeDisplay.textContent = mode;
    
    // Обновляем активную кнопку
    document.querySelectorAll('.mode-btn').forEach(btn => {
        if (btn.dataset.mode === mode) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    
    // Отправляем уведомление о смене режима
    addMessage(`🔄 Режим изменён на: ${mode === 'study' ? '📚 Учим новое' : mode === 'training' ? '⚡ Тренировка' : '🎯 Экзамен'}`, false);
}

// Обработка Enter (Shift+Enter для новой строки)
messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSend();
    }
});

// Авто-расширение textarea
messageInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 120) + 'px';
});

sendBtn.addEventListener('click', handleSend);

// Обработчики кнопок режимов
document.querySelectorAll('.mode-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        setMode(btn.dataset.mode);
    });
});

// Инициализация
currentUserId = getUserId();
setMode('study');

// Приветствие (уже есть в HTML, не добавляем лишнее)
console.log('Фрэд веб-клиент запущен. User ID:', currentUserId);
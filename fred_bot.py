import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from openai import OpenAI
from database import (
    init_db, get_or_create_user, update_last_seen, save_message, 
    get_recent_messages, clear_user_history, update_topic_score,
    get_weak_topics, get_topic_summary, get_user_mode, set_user_mode
)

load_dotenv()

# ========== НАСТРОЙКИ ==========
VSEGPT_API_KEY = "sk-or-vv-83d191cfb7900cb8eb369fe1850e6a9802f4e312b6a813fdf9d3536d714b585e"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not VSEGPT_API_KEY:
    print("❌ Ошибка: не найден VSEGPT_API_KEY")
    exit(1)
if not TELEGRAM_BOT_TOKEN:
    print("❌ Ошибка: не найден TELEGRAM_BOT_TOKEN в файле .env")
    exit(1)

deepseek_client = OpenAI(
    api_key=VSEGPT_API_KEY,
    base_url="https://api.vsegpt.ru/v1"
)
# ================================

# Инициализируем базу данных
init_db()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Хранилище истории для текущей сессии (для скорости)
session_history = {}

def get_system_prompt(mode='study'):
    """Возвращает системный промпт в зависимости от режима"""
    base_prompt = """Ты — Фрэд, репетитор по профильной математике ЕГЭ.
    
Твои правила:
1. НЕ решай за ученика. Задавай наводящие вопросы.
2. Объясняй шаг за шагом, от простого к сложному.
3. Если ученик ошибся — объясни, почему, и дай похожую задачу.
4. Используй аналогии из жизни, показывай связь математики с реальным миром.
5. Будь дружелюбным, терпеливым, с чувством юмора.
6. Когда говоришь о логарифмах — вспомни про шкалу Рихтера.
7. Когда говоришь о производной — объясни, что это скорость изменения."""
    
    if mode == 'exam':
        return base_prompt + "\n\nСЕЙЧАС РЕЖИМ ЭКЗАМЕНА: НЕ давай подсказок. Только проверяй ответы. Будь краток."
    elif mode == 'training':
        return base_prompt + "\n\nСЕЙЧАС РЕЖИМ ТРЕНИРОВКИ: Не давай готовых ответов. Только указывай на ошибки и дай направление."
    
    return base_prompt

def detect_topic(message):
    """Простое определение темы по ключевым словам"""
    message_lower = message.lower()
    if any(word in message_lower for word in ['логарифм', 'log', 'ln']):
        return 'A3'
    if any(word in message_lower for word in ['процент', '%']):
        return 'A1'
    if any(word in message_lower for word in ['производн', 'скорость изменения', 'касательная']):
        return 'A14'
    if any(word in message_lower for word in ['квадратн', 'дискриминант', 'ax²']):
        return 'A7'
    if any(word in message_lower for word in ['вероятност', 'шанс', 'случайн']):
        return 'B7'
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветствие с меню"""
    user = update.effective_user
    user_id = str(user.id)
    
    # Регистрируем пользователя в БД
    get_or_create_user(user_id, user.username, user.first_name)
    
    # Создаём клавиатуру
    keyboard = [
        [InlineKeyboardButton("📚 Учим новое", callback_data="mode_study"),
         InlineKeyboardButton("⚡ Тренировка", callback_data="mode_training")],
        [InlineKeyboardButton("🎯 Экзамен", callback_data="mode_exam"),
         InlineKeyboardButton("📊 Мой прогресс", callback_data="show_progress")],
        [InlineKeyboardButton("❓ Слабые темы", callback_data="weak_topics")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🧮 Привет! Я Фрэд — твой помощник по математике.\n\n"
        "Я помогаю готовиться к ЕГЭ по профильной математике.\n"
        f"Твой текущий режим: {get_user_mode(user_id)}\n\n"
        "Выбери режим работы:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает нажатия кнопок"""
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    data = query.data
    
    if data.startswith("mode_"):
        mode = data.split("_")[1]
        set_user_mode(user_id, mode)
        await query.edit_message_text(
            f"✅ Режим изменён на: {mode}\n\n"
            "Теперь задавай вопросы или решай задачи!"
        )
    
    elif data == "show_progress":
        topics = get_topic_summary(user_id)
        if not topics:
            await query.edit_message_text("Пока нет данных о прогрессе. Начни решать задачи!")
        else:
            message = "📊 Твой прогресс:\n\n"
            for topic_name, score, attempts in topics[:10]:
                if attempts > 0:
                    emoji = "🟢" if score >= 4 else "🟡" if score >= 3 else "🔴"
                    message += f"{emoji} {topic_name}: оценка {score} ({attempts} попыток)\n"
            await query.edit_message_text(message)
    
    elif data == "weak_topics":
        weak = get_weak_topics(user_id)
        if not weak:
            await query.edit_message_text("🎉 Отлично! У тебя нет явно слабых тем. Продолжай в том же духе!")
        else:
            message = "⚠️ Темы, которые нужно подтянуть:\n\n"
            for topic_name, score, attempts, correct in weak:
                message += f"• {topic_name} (оценка {score}, решено {correct}/{attempts})\n"
            await query.edit_message_text(message)

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Очистить историю диалога"""
    user_id = str(update.effective_user.id)
    clear_user_history(user_id)
    session_history[user_id] = []
    await update.message.reply_text("🧹 История диалога очищена. Начинаем с чистого листа!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает сообщения пользователя"""
    user = update.effective_user
    user_id = str(user.id)
    user_message = update.message.text
    
    # Регистрируем/обновляем пользователя
    get_or_create_user(user_id, user.username, user.first_name)
    update_last_seen(user_id)
    
    # Сохраняем сообщение
    save_message(user_id, "user", user_message)
    
    # Определяем тему (для трекера)
    topic_id = detect_topic(user_message)
    
    # Загружаем историю из БД
    history = get_recent_messages(user_id, limit=20)
    
    # Получаем текущий режим
    mode = get_user_mode(user_id)
    system_prompt = get_system_prompt(mode)
    
    # Формируем запрос
    messages = [{"role": "system", "content": system_prompt}] + history
    
    try:
        response = deepseek_client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=2000
        )
        
        answer = response.choices[0].message.content
        
        # Сохраняем ответ
        save_message(user_id, "assistant", answer)
        
        # Простая проверка: если в ответе есть поздравление с правильным решением
        # и мы определили тему, то обновляем прогресс
        if topic_id and any(word in answer.lower() for word in ['верно', 'правильно', 'молодец', 'отлично']):
            update_topic_score(user_id, topic_id, is_correct=True)
        elif topic_id and any(word in answer.lower() for word in ['неверно', 'ошибка', 'неправильно']):
            update_topic_score(user_id, topic_id, is_correct=False)
        
        await update.message.reply_text(answer)
        
    except Exception as e:
        logging.error(f"Ошибка при обращении к API: {e}")
        await update.message.reply_text("😕 Упс... Что-то пошло не так. Попробуй ещё раз.")

def main():
    print("🚀 Фрэд запускается...")
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Фрэд работает! Нажми Ctrl+C для остановки.")
    app.run_polling()

if __name__ == "__main__":
    main()
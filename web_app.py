import os
import sys
import logging
import sqlite3
import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn

# Импорты Фрэда
from database import (
    init_db, get_or_create_user, update_last_seen, save_message,
    get_recent_messages, update_topic_score, get_user_mode, set_user_mode,
    get_random_task, save_diagnostic_result, update_microtopic_progress,
    get_user_stats, update_user_stats, save_prediction
)

from predictor import (
    calculate_available_hours, calculate_nvb, primary_to_test,
    get_motivation_message, get_weekly_goal, EXAM_DATE
)

# Импорты генераторов
from generators import (
    generate_task, can_generate, generate_concept_question_llm,
    evaluate_concept_answer_llm, set_deepseek_client
)

# Импорт OpenAI
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ========== НАСТРОЙКИ ==========
# ВСТАВЬТЕ ВАШ РЕАЛЬНЫЙ КЛЮЧ VSEGPT
VSEGPT_API_KEY = "sk-or-vv-83d191cfb7900cb8eb369fe1850e6a9802f4e312b6a813fdf9d3536d714b585e"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not VSEGPT_API_KEY:
    print("❌ Ошибка: не найден VSEGPT_API_KEY")
    sys.exit(1)

# Создаём клиент DeepSeek
deepseek_client = OpenAI(
    api_key=VSEGPT_API_KEY,
    base_url="https://api.vsegpt.ru/v1"
)

# Устанавливаем клиент для генераторов
set_deepseek_client(deepseek_client)

# Инициализируем базу данных
init_db()

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создаём FastAPI приложение
app = FastAPI(title="Фрэд Репетитор API")

# Подключаем статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")

# Хранилище состояний диагностики
diagnostic_sessions = {}

# Модели запросов
class ChatRequest(BaseModel):
    user_id: str
    message: str
    mode: Optional[str] = "study"

class ChatResponse(BaseModel):
    reply: str


# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========

def get_system_prompt(mode='study'):
    """Возвращает системный промпт в зависимости от режима"""
    base_prompt = """Ты — Фрэд, репетитор по профильной математике ЕГЭ.
    
Твои правила:
1. НЕ решай за ученика. Задавай наводящие вопросы.
2. Объясняй шаг за шагом, от простого к сложному.
3. Если ученик ошибся — объясни, почему, и дай похожую задачу.
4. Используй аналогии из жизни, показывай связь математики с реальным миром.
5. Будь дружелюбным, терпеливым, с чувством юмора."""
    
    if mode == 'exam':
        return base_prompt + "\n\nСЕЙЧАС РЕЖИМ ЭКЗАМЕНА: НЕ давай подсказок. Только проверяй ответы. Будь краток."
    elif mode == 'training':
        return base_prompt + "\n\nСЕЙЧАС РЕЖИМ ТРЕНИРОВКИ: Не давай готовых ответов. Только указывай на ошибки и дай направление."
    
    return base_prompt

def detect_topic_simple(message):
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
    return None

def get_topic_name(topic_id):
    """Возвращает название темы по ID"""
    names = {
        "A1": "Проценты",
        "A2": "Степени и корни",
        "A3": "Логарифмы",
        "A7": "Квадратные уравнения",
        "A10": "Показательные уравнения",
        "A12": "Системы уравнений",  # <-- ДОБАВЬТЕ ЭТУ СТРОКУ
        "A14": "Производная",
        "B1": "Планиметрия"
    }
    return names.get(topic_id, topic_id)

def finalize_diagnostic(session, user_id):
    """Завершает диагностику и формирует результаты"""
    results = session['results']
    
    block1_status, block1_msg = evaluate_block_standalone(1, results)
    block2_status, block2_msg = evaluate_block_standalone(2, results)
    block3_status, block3_msg = evaluate_block_standalone(3, results)
    block4_status, block4_msg = evaluate_block_standalone(4, results)
    
    recommendations = []
    if block1_status != 'full':
        recommendations.append("📚 Начни с изучения теории и основного определения.")
    if block2_status != 'mastered':
        recommendations.append("📝 Потренируйся на простых задачах.")
    if block3_status != 'mastered':
        recommendations.append("🎯 После простых задач переходи к среднему уровню.")
    if block4_status == 'not_mastered':
        recommendations.append("⭐ Сложные задачи пока рановато. Освой сначала базу.")
    elif block4_status == 'partial':
        recommendations.append("🔥 Ты уже решаешь сложные задачи, но нужна доработка.")
    
    del diagnostic_sessions[user_id]
    
    return {
        "diagnostic_completed": True,
        "evaluations": {
            "block_1": {"status": block1_status, "message": block1_msg},
            "block_2": {"status": block2_status, "message": block2_msg},
            "block_3": {"status": block3_status, "message": block3_msg},
            "block_4": {"status": block4_status, "message": block4_msg}
        },
        "overall_level": sum([1 if block1_status=='full' else 0, 1 if block2_status=='mastered' else 0, 1 if block3_status=='mastered' else 0, 0.5 if block4_status=='partial' else 1 if block4_status=='mastered' else 0]),
        "recommendations": recommendations
    }

def evaluate_block_standalone(block, results):
    """Оценивает блок диагностики"""
    if block == 1:
        score = results.get('block_1', {}).get('score', 0)
        if score >= 80:
            return "full", "✅ Полностью понимает суть темы!"
        elif score >= 50:
            return "partial", "⚠️ Частично понимает, есть пробелы."
        return "none", "🔴 Не понимает суть, нужно начинать с теории."
    
    elif block == 2:
        correct = results.get('block_2', {}).get('correct', 0)
        total = results.get('block_2', {}).get('total', 5)
        if correct >= 4:
            return "mastered", f"✅ Простые задачи решает уверенно ({correct}/{total})"
        elif correct >= 2:
            return "partial", f"⚠️ С простыми задачами справляется частично ({correct}/{total})"
        return "not_mastered", f"🔴 Простые задачи пока не получаются ({correct}/{total})"
    
    elif block == 3:
        correct = results.get('block_3', {}).get('correct', 0)
        total = results.get('block_3', {}).get('total', 4)
        if correct >= 3:
            return "mastered", f"✅ Средние задачи решает уверенно ({correct}/{total})"
        elif correct >= 2:
            return "partial", f"⚠️ Со средними задачами справляется частично ({correct}/{total})"
        return "not_mastered", f"🔴 Средние задачи пока сложны ({correct}/{total})"
    
    elif block == 4:
        correct = results.get('block_4', {}).get('correct', 0)
        total = results.get('block_4', {}).get('total', 2)
        if correct == 2:
            return "mastered", f"✅ Сложные задачи решает отлично ({correct}/{total})"
        elif correct == 1:
            return "partial", f"⚠️ Сложные задачи решает частично ({correct}/{total})"
        return "not_mastered", f"🔴 Сложные задачи пока не решает ({correct}/{total})"
    
    return "unknown", ""


# ========== ОСНОВНЫЕ ЭНДПОИНТЫ ==========

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    user_id = request.user_id
    user_message = request.message
    mode = request.mode
    
    get_or_create_user(user_id, None, None)
    update_last_seen(user_id)
    set_user_mode(user_id, mode)
    save_message(user_id, "user", user_message)
    
    topic_id = detect_topic_simple(user_message)
    history = get_recent_messages(user_id, limit=20)
    system_prompt = get_system_prompt(mode)
    messages = [{"role": "system", "content": system_prompt}] + history
    
    try:
        response = deepseek_client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=2000,
            timeout=60.0
        )
        answer = response.choices[0].message.content
        save_message(user_id, "assistant", answer)
        
        if topic_id:
            if any(word in answer.lower() for word in ['верно', 'правильно', 'молодец', 'отлично', '✅']):
                update_topic_score(user_id, topic_id, is_correct=True)
            elif any(word in answer.lower() for word in ['неверно', 'ошибка', 'неправильно', '❌']):
                update_topic_score(user_id, topic_id, is_correct=False)
        
        return ChatResponse(reply=answer)
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        return ChatResponse(reply="😕 Ошибка, попробуй ещё раз.")


# ========== АPI ДЛЯ ДИАГНОСТИКИ ==========

@app.get("/api/diagnostic/topics")
async def get_diagnostic_topics():
    conn = sqlite3.connect('fred_users.db')
    c = conn.cursor()
    c.execute("SELECT topic_id, topic_name FROM topics ORDER BY topic_id")
    rows = c.fetchall()
    conn.close()
    topics = [{"id": row[0], "name": row[1]} for row in rows]
    return {"topics": topics}

@app.post("/api/diagnostic/start")
async def start_diagnostic(request: Request):
    data = await request.json()
    user_id = data.get('user_id')
    topic_id = data.get('topic_id')
    topic_name = get_topic_name(topic_id)
    
    if not user_id or not topic_id:
        raise HTTPException(status_code=400, detail="user_id и topic_id обязательны")
    
    diagnostic_sessions[user_id] = {
        'topic_id': topic_id,
        'topic_name': topic_name,
        'current_block': 1,
        'results': {
            'block_1': {'done': False, 'score': 0, 'answers': []},
            'block_2': {'done': False, 'correct': 0, 'total': 5, 'answers': []},
            'block_3': {'done': False, 'correct': 0, 'total': 4, 'answers': []},
            'block_4': {'done': False, 'correct': 0, 'total': 2, 'answers': []},
        }
    }
    return {"status": "started", "topic_id": topic_id, "current_block": 1}

@app.get("/api/diagnostic/next")
async def get_next_question(user_id: str):
    if user_id not in diagnostic_sessions:
        raise HTTPException(status_code=404, detail="Диагностика не найдена")
    
    session = diagnostic_sessions[user_id]
    topic_id = session['topic_id']
    topic_name = session.get('topic_name', topic_id)
    current_block = session['current_block']
    
    # Проверяем завершённость блоков
    if current_block == 1 and session['results']['block_1']['done']:
        session['current_block'] = 2
        current_block = 2
    elif current_block == 2 and session['results']['block_2']['done']:
        session['current_block'] = 3
        current_block = 3
    elif current_block == 3 and session['results']['block_3']['done']:
        session['current_block'] = 4
        current_block = 4
    elif current_block == 4 and session['results']['block_4']['done']:
        return {"completed": True, "message": "Диагностика завершена!"}
    
    session['current_block'] = current_block
    task = None
    
    # ========== ГЛАВНАЯ ЛОГИКА ПОЛУЧЕНИЯ ЗАДАНИЯ ==========
    if current_block == 1:
        # БЛОК 1: ВСЕГДА ГЕНЕРАЦИЯ ЧЕРЕЗ ИИ
        print(f"🎯 Генерация вопроса ИИ для темы: {topic_id} - {topic_name}")
        task = generate_concept_question_llm(topic_id, topic_name)
        if task:
            task['id'] = -1
            task['block'] = 1
            task['generated_by_llm'] = True
        else:
            # Если ИИ не сработал, используем запасной вопрос
            task = {
                "question": f"Опиши своими словами, что такое '{topic_name}'. Что это за понятие?",
                "question_type": "free_text",
                "id": -1,
                "block": 1
            }
    
    elif current_block == 2:
        # БЛОК 2: генерация или БД
        if can_generate(topic_id, current_block):
            task = generate_task(topic_id, current_block)
            if task:
                task['id'] = -1
                task['block'] = 2
        if not task:
            task = get_random_task(topic_id, current_block)
            if task:
                task['block'] = 2
                
    elif current_block == 3:
        # БЛОК 3: генерация или БД
        if can_generate(topic_id, current_block):
            task = generate_task(topic_id, current_block)
            if task:
                task['id'] = -1
                task['block'] = 3
                task['generated'] = True
        if not task:
            task = get_random_task(topic_id, current_block)
            if task:
                task['block'] = 3
                
    elif current_block == 4:
        # БЛОК 4: только БД
        task = get_random_task(topic_id, current_block)
        if task:
            task['block'] = 4
    
    # ========== ПРОВЕРКА ==========
    if not task:
        return {"error": f"Нет заданий для блока {current_block} темы {topic_id}. Добавьте задания в базу данных."}
    
    session['current_task'] = task
    
    return {
        "completed": False,
        "block": current_block,
        "task_id": task['id'],
        "question": task['question'],
        "question_type": task.get('question_type', 'text'),
        "options": task.get('options')
    }

@app.post("/api/diagnostic/answer")
async def submit_answer(request: Request):
    data = await request.json()
    user_id = data.get('user_id')
    task_id = data.get('task_id')
    user_answer = data.get('user_answer')
    response_time = data.get('response_time')
    
    if user_id not in diagnostic_sessions:
        raise HTTPException(status_code=404, detail="Диагностика не найдена")
    
    session = diagnostic_sessions[user_id]
    task = session.get('current_task')
    
    if not task or task['id'] != task_id:
        raise HTTPException(status_code=400, detail="Задание не найдено")
    
    topic_id = session['topic_id']
    topic_name = session.get('topic_name', topic_id)
    block = session['current_block']
    
    is_correct = False
    score = 0
    feedback_message = ""
    
    if block == 1:
        evaluation = evaluate_concept_answer_llm(user_answer, topic_id, topic_name)
        is_correct = evaluation['is_correct']
        score = evaluation['score']
        feedback_message = evaluation['feedback']
    elif block == 2:
        correct = task.get('correct_answer', '').lower()
        user = user_answer.strip().lower()
        is_correct = user == correct
        score = 100 if is_correct else 0
        feedback_message = "✅ Правильно!" if is_correct else "❌ Неправильно."
    elif block == 3:
        correct = task.get('correct_answer', '').lower()
        user = user_answer.strip().lower()
        is_correct = user == correct
        score = 100 if is_correct else 0
        feedback_message = "✅ Правильно!" if is_correct else "❌ Неправильно."
    elif block == 4:
        correct = task.get('correct_answer', '').lower()
        user = user_answer.strip().lower()
        is_correct = user == correct
        score = 100 if is_correct else 0
        feedback_message = "✅ Правильно!" if is_correct else "❌ Неправильно."
    else:
        correct = task.get('correct_answer', '').lower()
        user = user_answer.strip().lower()
        is_correct = user == correct
        score = 100 if is_correct else 0
        feedback_message = "✅ Правильно!" if is_correct else "❌ Неправильно."
    
    if task_id != -1:
        save_diagnostic_result(
            user_id=user_id, topic_id=topic_id, task_id=task_id,
            block=block, user_answer=user_answer, is_correct=is_correct,
            score=score, response_time=response_time
        )
    
    block_key = f"block_{block}"
    block_data = session['results'][block_key]
    block_data['answers'].append({'correct': is_correct, 'answer': user_answer, 'score': score})
    
    if block == 1:
        block_data['done'] = True
        block_data['score'] = score
        update_microtopic_progress(user_id, f"{topic_id}_concept", is_correct, score)
    else:
        if is_correct:
            block_data['correct'] += 1
        if len(block_data['answers']) >= block_data['total']:
            block_data['done'] = True
    
    session['results'][block_key] = block_data
    diagnostic_sessions[user_id] = session
    
    if block_data['done']:
        if block < 4:
            return {
                "block_completed": True,
                "next_block": block + 1,
                "message": f"Блок {block} завершён! {feedback_message}"
            }
        else:
            return finalize_diagnostic(session, user_id)
    else:
        return {
            "correct": is_correct,
            "block_completed": False,
            "message": feedback_message
        }
# ========== API ДЛЯ СТАТИСТИКИ ==========

@app.get("/api/stats")
async def get_stats(user_id: str):
    from datetime import date
    try:
        print(f"1. Получаем статистику для {user_id}")
        stats = get_user_stats(user_id)
        print(f"2. Статистика: {stats}")
        
        current_primary = stats['current_primary_score']
        print(f"3. Текущий первичный балл: {current_primary}")
        
        settings = {
            'hours_per_study_day': stats['hours_per_study_day'],
            'hours_per_holiday': stats['hours_per_holiday'],
            'other_subjects_count': stats['other_subjects_count']
        }
        print(f"4. Настройки: {settings}")
        
        available_hours = calculate_available_hours(settings)
        print(f"5. Доступно часов: {available_hours}")
        
        predicted_score = calculate_nvb(current_primary, available_hours)
        print(f"6. Прогноз: {predicted_score}")
        
        current_test = primary_to_test(current_primary)
        target_test = primary_to_test(stats['target_primary_score'])
        print(f"7. Баллы: текущий={current_test}, целевой={target_test}")
        
        motivation = get_motivation_message(current_primary, stats['target_primary_score'], available_hours, predicted_score)
        print(f"8. Мотивация получена")
        
        weekly_goal = get_weekly_goal(current_primary, available_hours)
        print(f"9. Недельная цель: {weekly_goal}")
        
        save_prediction(user_id, predicted_score, available_hours, current_primary)
        print(f"10. Прогноз сохранён")
        
        return {
            "current_score": current_test,
            "target_score": target_test,
            "predicted_score": predicted_score,
            "available_hours": available_hours,
            "days_until_exam": (EXAM_DATE - date.today()).days,
            "current_primary": current_primary,
            "target_primary": stats['target_primary_score'],
            "motivation_message": motivation,
            "weekly_goal": weekly_goal,
            "settings": settings
        }
    except Exception as e:
        print(f"ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

@app.post("/api/stats/settings")
async def update_stats_settings(request: Request):
    data = await request.json()
    user_id = data.get('user_id')
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id обязателен")
    update_user_stats(
        user_id,
        current_primary_score=data.get('current_primary_score'),
        target_primary_score=data.get('target_primary_score'),
        hours_per_study_day=data.get('hours_per_study_day'),
        hours_per_holiday=data.get('hours_per_holiday'),
        other_subjects_count=data.get('other_subjects_count')
    )
    return {"status": "updated"}

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    print("🚀 Веб-сервер Фрэда запускается...")
    print("📍 Открой в браузере: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
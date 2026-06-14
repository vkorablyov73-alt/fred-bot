import sqlite3
import json
from database import add_task, init_db

# Инициализируем базу
init_db()

# ========== ТЕМА: ЛОГАРИФМЫ (A3) ==========

# БЛОК 1. Понимание сути (1 вопрос)
tasks_block1 = [
    {
        "topic_id": "A3",
        "microtopic_id": "A3_1",
        "block": 1,
        "difficulty": 1,
        "question": "Что такое логарифм? Опиши своими словами.",
        "question_type": "text",
        "correct_answer": "показатель степени в которую нужно возвести основание чтобы получить число",
        "options": None,
        "explanation": "Логарифм числа b по основанию a (log_a b) — это показатель степени, в которую нужно возвести a, чтобы получить b."
    }
]

# БЛОК 2. Простые задания (5 примеров)
tasks_block2 = [
    {
        "topic_id": "A3",
        "microtopic_id": "A3_1",
        "block": 2,
        "difficulty": 1,
        "question": "Вычислите: log₂8",
        "question_type": "number",
        "correct_answer": "3",
        "options": None,
        "explanation": "2³ = 8, поэтому log₂8 = 3"
    },
    {
        "topic_id": "A3",
        "microtopic_id": "A3_1",
        "block": 2,
        "difficulty": 1,
        "question": "Вычислите: log₃81",
        "question_type": "number",
        "correct_answer": "4",
        "options": None,
        "explanation": "3⁴ = 81, поэтому log₃81 = 4"
    },
    {
        "topic_id": "A3",
        "microtopic_id": "A3_3",
        "block": 2,
        "difficulty": 1,
        "question": "Вычислите: log₅125",
        "question_type": "number",
        "correct_answer": "3",
        "options": None,
        "explanation": "5³ = 125, поэтому log₅125 = 3"
    },
    {
        "topic_id": "A3",
        "microtopic_id": "A3_4",
        "block": 2,
        "difficulty": 1,
        "question": "Вычислите: log₂16",
        "question_type": "number",
        "correct_answer": "4",
        "options": None,
        "explanation": "2⁴ = 16, поэтому log₂16 = 4"
    },
    {
        "topic_id": "A3",
        "microtopic_id": "A3_2",
        "block": 2,
        "difficulty": 1,
        "question": "Вычислите: log₇49",
        "question_type": "number",
        "correct_answer": "2",
        "options": None,
        "explanation": "7² = 49, поэтому log₇49 = 2"
    }
]

# БЛОК 3. Средние задания (4 примера)
tasks_block3 = [
    {
        "topic_id": "A3",
        "microtopic_id": "A3_3",
        "block": 3,
        "difficulty": 2,
        "question": "Вычислите: log₂8 + log₂4",
        "question_type": "number",
        "correct_answer": "5",
        "options": None,
        "explanation": "log₂8 = 3, log₂4 = 2, сумма = 5. Или по свойству: log₂(8·4) = log₂32 = 5"
    },
    {
        "topic_id": "A3",
        "microtopic_id": "A3_4",
        "block": 3,
        "difficulty": 2,
        "question": "Вычислите: log₂(16) - log₂(4)",
        "question_type": "number",
        "correct_answer": "2",
        "options": None,
        "explanation": "log₂16 = 4, log₂4 = 2, разность = 2. Или: log₂(16/4) = log₂4 = 2"
    },
    {
        "topic_id": "A3",
        "microtopic_id": "A3_3",
        "block": 3,
        "difficulty": 2,
        "question": "Вычислите: log₃9 + log₃27",
        "question_type": "number",
        "correct_answer": "5",
        "options": None,
        "explanation": "log₃9 = 2, log₃27 = 3, сумма = 5"
    },
    {
        "topic_id": "A3",
        "microtopic_id": "A3_4",
        "block": 3,
        "difficulty": 2,
        "question": "Вычислите: 2·log₅25",
        "question_type": "number",
        "correct_answer": "4",
        "options": None,
        "explanation": "log₅25 = 2, поэтому 2·2 = 4"
    }
]

# БЛОК 4. Сложные задания (2 примера из части 2 ЕГЭ)
tasks_block4 = [
    {
        "topic_id": "A3",
        "microtopic_id": "A3_6",
        "block": 4,
        "difficulty": 3,
        "question": "Решите уравнение: log₂(x+3) = 4",
        "question_type": "equation",
        "correct_answer": "x = 13",
        "options": None,
        "explanation": "По определению логарифма: x+3 = 2⁴ = 16, x = 13"
    },
    {
        "topic_id": "A3",
        "microtopic_id": "A3_6",
        "block": 4,
        "difficulty": 3,
        "question": "Решите уравнение: log₃(2x-1) = 2",
        "question_type": "equation",
        "correct_answer": "x = 5",
        "options": None,
        "explanation": "По определению: 2x-1 = 3² = 9, 2x = 10, x = 5"
    }
]

# ========== ДОБАВЛЕНИЕ В БАЗУ ==========

def add_tasks():
    print("Добавление заданий для темы 'Логарифмы' (A3)...")
    
    count = 0
    
    # Блок 1
    for task in tasks_block1:
        add_task(
            topic_id=task["topic_id"],
            microtopic_id=task["microtopic_id"],
            block=task["block"],
            difficulty=task["difficulty"],
            question=task["question"],
            correct_answer=task["correct_answer"],
            question_type=task["question_type"],
            options=task["options"],
            explanation=task["explanation"]
        )
        count += 1
        print(f"  ✅ Добавлено задание: {task['question'][:50]}...")
    
    # Блок 2
    for task in tasks_block2:
        add_task(
            topic_id=task["topic_id"],
            microtopic_id=task["microtopic_id"],
            block=task["block"],
            difficulty=task["difficulty"],
            question=task["question"],
            correct_answer=task["correct_answer"],
            question_type=task["question_type"],
            options=task["options"],
            explanation=task["explanation"]
        )
        count += 1
        print(f"  ✅ Добавлено задание: {task['question'][:50]}...")
    
    # Блок 3
    for task in tasks_block3:
        add_task(
            topic_id=task["topic_id"],
            microtopic_id=task["microtopic_id"],
            block=task["block"],
            difficulty=task["difficulty"],
            question=task["question"],
            correct_answer=task["correct_answer"],
            question_type=task["question_type"],
            options=task["options"],
            explanation=task["explanation"]
        )
        count += 1
        print(f"  ✅ Добавлено задание: {task['question'][:50]}...")
    
    # Блок 4
    for task in tasks_block4:
        add_task(
            topic_id=task["topic_id"],
            microtopic_id=task["microtopic_id"],
            block=task["block"],
            difficulty=task["difficulty"],
            question=task["question"],
            correct_answer=task["correct_answer"],
            question_type=task["question_type"],
            options=task["options"],
            explanation=task["explanation"]
        )
        count += 1
        print(f"  ✅ Добавлено задание: {task['question'][:50]}...")
    
    print(f"\n🎉 Готово! Добавлено {count} заданий по теме 'Логарифмы'.")
    print("\n📊 Статистика:")
    print(f"   Блок 1 (понимание сути): {len(tasks_block1)} задание")
    print(f"   Блок 2 (простые): {len(tasks_block2)} заданий")
    print(f"   Блок 3 (средние): {len(tasks_block3)} заданий")
    print(f"   Блок 4 (сложные): {len(tasks_block4)} заданий")

if __name__ == "__main__":
    add_tasks()
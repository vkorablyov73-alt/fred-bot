"""
Скрипт для добавления заданий в базу данных Фрэда
Темы: Проценты (A1), Производная (A14), Планиметрия (B1)
"""

import sqlite3
from database import add_task, init_db

DB_NAME = 'fred_users.db'

def add_tasks():
    """Добавляет задания для всех тем"""
    
    init_db()
    print("Добавление заданий в базу данных...\n")
    
    # ========== ТЕМА A1: ПРОЦЕНТЫ ==========
    print("📊 Тема: Проценты (A1)")
    
    # Блок 1: Понимание сути (готовый вопрос)
    add_task(
        topic_id="A1",
        microtopic_id="A1_1",
        block=1,
        difficulty=1,
        question="Что такое процент? Опиши своими словами. Как понять фразу '20% от числа'?",
        correct_answer="",
        question_type="free_text",
        explanation="Процент — это сотая часть числа. 1% = 1/100 = 0.01"
    )
    
    # Блок 3: Средние задания (готовые)
    tasks_block3_A1 = [
        {
            "microtopic": "A1_2",
            "question": "Цена товара была 500 рублей. После скидки стала 400 рублей. Сколько процентов составила скидка?",
            "answer": "20",
            "explanation": "Скидка = 500 - 400 = 100 рублей. 100/500 = 0.2 = 20%"
        },
        {
            "microtopic": "A1_3",
            "question": "Вкладчик положил в банк 10000 рублей под 10% годовых. Сколько будет на счету через год?",
            "answer": "11000",
            "explanation": "10% от 10000 = 1000. 10000 + 1000 = 11000"
        },
        {
            "microtopic": "A1_4",
            "question": "Число увеличили на 25%, получили 100. Найдите исходное число.",
            "answer": "80",
            "explanation": "Пусть x — исходное число. x + 0.25x = 1.25x = 100, x = 80"
        },
        {
            "microtopic": "A1_2",
            "question": "Товар стоил 2000 рублей. Цену снизили на 15%. Сколько стал стоить товар?",
            "answer": "1700",
            "explanation": "15% от 2000 = 300. 2000 - 300 = 1700"
        }
    ]
    
    for task in tasks_block3_A1:
        add_task(
            topic_id="A1",
            microtopic_id=task["microtopic"],
            block=3,
            difficulty=2,
            question=task["question"],
            correct_answer=task["answer"],
            question_type="number",
            explanation=task["explanation"]
        )
    
    # Блок 4: Сложные задания
    tasks_block4_A1 = [
        {
            "microtopic": "A1_5",
            "question": "Цену товара сначала повысили на 20%, а затем понизили на 20%. Как изменилась цена по сравнению с первоначальной?",
            "answer": "4",
            "explanation": "Было x. После повышения: 1.2x. После понижения: 0.8 × 1.2x = 0.96x. Цена снизилась на 4%"
        },
        {
            "microtopic": "A1_6",
            "question": "Вкладчик положил 50000 рублей под 8% годовых с капитализацией процентов (сложный процент). Сколько будет на счету через 2 года?",
            "answer": "58320",
            "explanation": "S = 50000 × (1 + 0.08)² = 50000 × 1.1664 = 58320"
        }
    ]
    
    for task in tasks_block4_A1:
        add_task(
            topic_id="A1",
            microtopic_id=task["microtopic"],
            block=4,
            difficulty=3,
            question=task["question"],
            correct_answer=task["answer"],
            question_type="number",
            explanation=task["explanation"]
        )
    
    print(f"  ✅ Добавлено: 1 (блок1) + {len(tasks_block3_A1)} (блок3) + {len(tasks_block4_A1)} (блок4) = {1 + len(tasks_block3_A1) + len(tasks_block4_A1)} заданий")


    # ========== ТЕМА A14: ПРОИЗВОДНАЯ ==========
    print("\n📈 Тема: Производная (A14)")
    
    # Блок 1: Понимание сути
    add_task(
        topic_id="A14",
        microtopic_id="A14_1",
        block=1,
        difficulty=1,
        question="Что такое производная функции? Опиши своими словами. Какой геометрический смысл производной?",
        correct_answer="",
        question_type="free_text",
        explanation="Производная — это скорость изменения функции. Геометрически — угловой коэффициент касательной к графику."
    )
    
    # Блок 3: Средние задания
    tasks_block3_A14 = [
        {
            "microtopic": "A14_2",
            "question": "Найдите производную функции f(x) = 3x² + 2x - 5",
            "answer": "6x+2",
            "explanation": "f'(x) = 3·2x + 2 = 6x + 2"
        },
        {
            "microtopic": "A14_2",
            "question": "Найдите производную функции f(x) = 5x³ - 4x² + x",
            "answer": "15x^2-8x+1",
            "explanation": "f'(x) = 5·3x² - 4·2x + 1 = 15x² - 8x + 1"
        },
        {
            "microtopic": "A14_3",
            "question": "Найдите производную функции f(x) = (2x + 3)(x - 1)",
            "answer": "4x+1",
            "explanation": "f(x) = 2x² - 2x + 3x - 3 = 2x² + x - 3, f'(x) = 4x + 1"
        },
        {
            "microtopic": "A14_4",
            "question": "Найдите значение производной функции f(x) = x² - 3x в точке x₀ = 2",
            "answer": "1",
            "explanation": "f'(x) = 2x - 3, f'(2) = 4 - 3 = 1"
        }
    ]
    
    for task in tasks_block3_A14:
        add_task(
            topic_id="A14",
            microtopic_id=task["microtopic"],
            block=3,
            difficulty=2,
            question=task["question"],
            correct_answer=task["answer"],
            question_type="text",
            explanation=task["explanation"]
        )
    
    # Блок 4: Сложные задания
    tasks_block4_A14 = [
        {
            "microtopic": "A14_5",
            "question": "Найдите угловой коэффициент касательной к графику функции f(x) = x³ - 2x² + 1 в точке x₀ = 1",
            "answer": "-1",
            "explanation": "f'(x) = 3x² - 4x, f'(1) = 3 - 4 = -1"
        },
        {
            "microtopic": "A14_6",
            "question": "Найдите точку максимума функции f(x) = -x² + 6x - 5",
            "answer": "3",
            "explanation": "f'(x) = -2x + 6 = 0, x = 3. Вторая производная: f''(x) = -2 < 0 → максимум"
        }
    ]
    
    for task in tasks_block4_A14:
        add_task(
            topic_id="A14",
            microtopic_id=task["microtopic"],
            block=4,
            difficulty=3,
            question=task["question"],
            correct_answer=task["answer"],
            question_type="number",
            explanation=task["explanation"]
        )
    
    print(f"  ✅ Добавлено: 1 (блок1) + {len(tasks_block3_A14)} (блок3) + {len(tasks_block4_A14)} (блок4) = {1 + len(tasks_block3_A14) + len(tasks_block4_A14)} заданий")


    # ========== ТЕМА B1: ПЛАНИМЕТРИЯ (ТРЕУГОЛЬНИКИ) ==========
    print("\n📐 Тема: Планиметрия (B1)")
    
    # Блок 1: Понимание сути
    add_task(
        topic_id="B1",
        microtopic_id="B1_1",
        block=1,
        difficulty=1,
        question="Что такое треугольник? Какие виды треугольников вы знаете? Назови их свойства.",
        correct_answer="",
        question_type="free_text",
        explanation="Треугольник — это фигура из трёх точек и трёх отрезков. Виды: равнобедренный, равносторонний, прямоугольный, разносторонний."
    )
    
    # Блок 3: Средние задания
    tasks_block3_B1 = [
        {
            "microtopic": "B1_2",
            "question": "В треугольнике ABC угол A = 50°, угол B = 60°. Найдите угол C.",
            "answer": "70",
            "explanation": "Сумма углов треугольника = 180°. Угол C = 180 - 50 - 60 = 70°"
        },
        {
            "microtopic": "B1_3",
            "question": "В прямоугольном треугольнике катеты равны 3 и 4. Найдите гипотенузу.",
            "answer": "5",
            "explanation": "По теореме Пифагора: c² = 3² + 4² = 9 + 16 = 25, c = 5"
        },
        {
            "microtopic": "B1_4",
            "question": "Найдите площадь треугольника с основанием 8 и высотой 5.",
            "answer": "20",
            "explanation": "S = ½ × основание × высота = 0.5 × 8 × 5 = 20"
        },
        {
            "microtopic": "B1_5",
            "question": "В равнобедренном треугольнике боковая сторона равна 10, основание 12. Найдите высоту, проведённую к основанию.",
            "answer": "8",
            "explanation": "Высота делит основание пополам. По Пифагору: h² = 10² - 6² = 100 - 36 = 64, h = 8"
        }
    ]
    
    for task in tasks_block3_B1:
        add_task(
            topic_id="B1",
            microtopic_id=task["microtopic"],
            block=3,
            difficulty=2,
            question=task["question"],
            correct_answer=task["answer"],
            question_type="number",
            explanation=task["explanation"]
        )
    
    # Блок 4: Сложные задания
    tasks_block4_B1 = [
        {
            "microtopic": "B1_6",
            "question": "В треугольнике ABC стороны равны AB = 13, BC = 14, AC = 15. Найдите площадь треугольника.",
            "answer": "84",
            "explanation": "По формуле Герона: p = (13+14+15)/2 = 21, S = √(21·(21-13)·(21-14)·(21-15)) = √(21·8·7·6) = √7056 = 84"
        },
        {
            "microtopic": "B1_7",
            "question": "В прямоугольном треугольнике ABC (угол C = 90°) катет AC = 6, гипотенуза AB = 10. Найдите синус угла B.",
            "answer": "0.6",
            "explanation": "sin B = противолежащий катет / гипотенуза = AC/AB = 6/10 = 0.6"
        }
    ]
    
    for task in tasks_block4_B1:
        add_task(
            topic_id="B1",
            microtopic_id=task["microtopic"],
            block=4,
            difficulty=3,
            question=task["question"],
            correct_answer=task["answer"],
            question_type="number",
            explanation=task["explanation"]
        )
    
    print(f"  ✅ Добавлено: 1 (блок1) + {len(tasks_block3_B1)} (блок3) + {len(tasks_block4_B1)} (блок4) = {1 + len(tasks_block3_B1) + len(tasks_block4_B1)} заданий")


    # ========== ИТОГО ==========
    print("\n" + "="*50)
    print("🎉 ГОТОВО! Добавлены задания для тем:")
    print("   • Проценты (A1)")
    print("   • Производная (A14)")
    print("   • Планиметрия (B1)")
    print("="*50)


if __name__ == "__main__":
    add_tasks()
    print("\n✅ Теперь можно проходить диагностику по этим темам!")
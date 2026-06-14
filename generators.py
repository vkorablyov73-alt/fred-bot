"""
Генераторы заданий для диагностики Фрэда
Поддерживает:
- Блок 1: генерация вопросов через ИИ
- Блок 2: генерация простых заданий по шаблонам
"""

import random
import math
import json
from typing import Dict, Any, Optional
from openai import OpenAI

# ========== НАСТРОЙКИ ==========
_deepseek_client = None

def set_deepseek_client(client):
    """Устанавливает клиент DeepSeek для использования в генераторах"""
    global _deepseek_client
    _deepseek_client = client


# ========== БЛОК 1: ГЕНЕРАЦИЯ ВОПРОСОВ ЧЕРЕЗ ИИ ==========

def generate_concept_question_llm(topic_id: str, topic_name: str) -> Dict[str, Any]:
    """
    Генерирует вопрос на понимание сути через DeepSeek API
    """
    global _deepseek_client
    
    if not _deepseek_client:
        return {
            "question": f"Опиши своими словами, что такое '{topic_name}'. Что это за понятие и зачем оно нужно?",
            "question_type": "free_text",
            "correct_answer": None,
            "explanation": None,
            "generated_by_llm": True
        }
    
    prompt = f"""Ты — Фрэд, репетитор по математике. 
Нужно задать ученику вопрос для проверки ПОНИМАНИЯ СУТИ темы "{topic_name}".

Правила:
1. Вопрос должен проверять понимание концепции, а не умение вычислять
2. Ученик должен ответить своими словами
3. Вопрос должен быть понятным для 17-летнего ученика
4. Не используй формулы в вопросе
5. Вопрос должен быть на русском языке

Пример для темы "Логарифмы":
"Объясни своими словами, что такое логарифм. Что он показывает? Как понять фразу 'логарифм числа b по основанию a'?"

Пример для темы "Производная":
"Что означает производная функции в точке? Объясни на примере движения автомобиля."

Сгенерируй один вопрос для темы "{topic_name}" в таком же стиле.
Выдай только текст вопроса, без пояснений, без кавычек."""

    try:
        response = _deepseek_client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=200
        )
        question = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Ошибка генерации вопроса через ИИ: {e}")
        question = f"Опиши своими словами, что такое '{topic_name}'. Что это за понятие и зачем оно нужно?"
    
    return {
        "question": question,
        "question_type": "free_text",
        "correct_answer": None,
        "explanation": None,
        "generated_by_llm": True
    }


def evaluate_concept_answer_llm(user_answer: str, topic_id: str, topic_name: str) -> Dict[str, Any]:
    """
    Оценивает ответ ученика на вопрос о понимании сути через ИИ
    Возвращает: is_correct (bool), score (int 0-100), feedback (str)
    """
    global _deepseek_client
    
    if not _deepseek_client:
        return {
            "is_correct": True,
            "score": 70,
            "feedback": "Спасибо за ответ!"
        }
    
    prompt = f"""Ты — Фрэд, репетитор по математике. Оцени ответ ученика на вопрос по теме "{topic_name}".

Ответ ученика:
"{user_answer}"

Оцени ответ по шкале:
- 90-100: Полностью понимает суть, объясняет верно и понятно
- 60-89: Понимает частично, есть неточности или неполный ответ
- 0-59: Не понимает суть, ответ неправильный или отсутствует

Выдай ТОЛЬКО JSON в формате:
{{"score": число_от_0_до_100, "feedback": "короткий комментарий для ученика"}}

Не пиши ничего кроме JSON."""

    try:
        response = _deepseek_client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=150
        )
        
        result_text = response.choices[0].message.content.strip()
        result = json.loads(result_text)
        score = min(100, max(0, result.get("score", 50)))
        feedback = result.get("feedback", "Понял, принято!")
        
        return {
            "is_correct": score >= 70,
            "score": score,
            "feedback": feedback
        }
    except Exception as e:
        print(f"Ошибка оценки ответа через ИИ: {e}")
        return {
            "is_correct": True,
            "score": 70,
            "feedback": "Спасибо за ответ!"
        }


# ========== БЛОК 2: ГЕНЕРАТОРЫ ПРОСТЫХ ЗАДАНИЙ ==========

def generate_log_simple() -> Dict[str, Any]:
    """Вычисление логарифма: logₐ(b) = ?"""
    bases = [2, 3, 4, 5, 7, 8, 9, 10]
    base = random.choice(bases)
    power = random.randint(1, 5)
    number = base ** power
    
    return {
        "question": f"Вычислите: log_{base}({number})",
        "correct_answer": str(power),
        "explanation": f"{base}^{power} = {number}, поэтому log_{base}({number}) = {power}",
        "question_type": "number",
        "difficulty": 1
    }


def generate_log_sum_simple() -> Dict[str, Any]:
    """Сумма логарифмов: logₐ(b) + logₐ(c) = ?"""
    bases = [2, 3, 5]
    base = random.choice(bases)
    power1 = random.randint(1, 4)
    power2 = random.randint(1, 4)
    num1 = base ** power1
    num2 = base ** power2
    
    return {
        "question": f"Вычислите: log_{base}({num1}) + log_{base}({num2})",
        "correct_answer": str(power1 + power2),
        "explanation": f"log_{base}({num1}) = {power1}, log_{base}({num2}) = {power2}, сумма = {power1 + power2}",
        "question_type": "number",
        "difficulty": 1
    }


def generate_percent_simple() -> Dict[str, Any]:
    """Процент от числа: X% от Y = ?"""
    number = random.randint(100, 1000)
    percent = random.choice([5, 10, 15, 20, 25, 30, 50, 75])
    result = round(number * percent / 100)
    
    return {
        "question": f"Найдите {percent}% от числа {number}",
        "correct_answer": str(result),
        "explanation": f"{number} × {percent}% = {number} × {percent}/100 = {result}",
        "question_type": "number",
        "difficulty": 1
    }


def generate_power_simple() -> Dict[str, Any]:
    """Возведение в степень: a^b = ?"""
    base = random.randint(2, 10)
    exponent = random.randint(2, 5)
    result = base ** exponent
    
    return {
        "question": f"Вычислите: {base}^{exponent}",
        "correct_answer": str(result),
        "explanation": f"{base} × {base} × ... ({exponent} раз) = {result}",
        "question_type": "number",
        "difficulty": 1
    }


def generate_square_root_simple() -> Dict[str, Any]:
    """Квадратный корень: √x = ?"""
    numbers = [16, 25, 36, 49, 64, 81, 100, 121, 144, 169, 196, 225]
    number = random.choice(numbers)
    result = int(math.sqrt(number))
    
    return {
        "question": f"Вычислите: √{number}",
        "correct_answer": str(result),
        "explanation": f"√{number} = {result}, так как {result}² = {number}",
        "question_type": "number",
        "difficulty": 1
    }


# ========== ГЕНЕРАТОРЫ ДЛЯ СИСТЕМ УРАВНЕНИЙ (A12) - БЛОК 2 ==========

def generate_system_simple_1() -> Dict[str, Any]:
    """
    Простая система уравнений для блока 2
    Пример: x + y = 5, x - y = 1 → x=3, y=2
    """
    x = random.randint(1, 10)
    y = random.randint(1, 10)
    
    # Первое уравнение: x + y
    sum_val = x + y
    
    # Второе уравнение: x - y или y - x
    if random.choice([True, False]):
        diff_val = x - y
        question = f"Решите систему уравнений:\nx + y = {sum_val}\nx - y = {diff_val}"
        answer = f"x = {x}, y = {y}"
        explanation = f"Складываем уравнения: 2x = {sum_val + diff_val} → x = {x}\n"
        explanation += f"Подставляем: {x} + y = {sum_val} → y = {y}"
    else:
        diff_val = y - x
        question = f"Решите систему уравнений:\nx + y = {sum_val}\ny - x = {diff_val}"
        answer = f"x = {x}, y = {y}"
        explanation = f"Складываем уравнения: 2y = {sum_val + diff_val} → y = {y}\n"
        explanation += f"Подставляем: x + {y} = {sum_val} → x = {x}"
    
    return {
        "question": question,
        "correct_answer": answer,
        "explanation": explanation,
        "question_type": "text",
        "difficulty": 1
    }


def generate_system_simple_2() -> Dict[str, Any]:
    """
    Простая система: y = kx + b и x + y = c
    Пример: y = 2x + 1, x + y = 10 → x=3, y=7
    """
    x = random.randint(1, 8)
    k = random.choice([2, 3, 4])
    b = random.randint(-3, 5)
    y = k * x + b
    
    c = x + y
    
    question = f"Решите систему уравнений:\ny = {k}x + {b}\nx + y = {c}"
    answer = f"x = {x}, y = {y}"
    explanation = f"Подставляем y из первого во второе:\n"
    explanation += f"x + ({k}x + {b}) = {c}\n"
    explanation += f"{k+1}x + {b} = {c}\n"
    explanation += f"{k+1}x = {c - b} → x = {x}\n"
    explanation += f"y = {k}·{x} + {b} = {y}"
    
    return {
        "question": question,
        "correct_answer": answer,
        "explanation": explanation,
        "question_type": "text",
        "difficulty": 1
    }


# ========== БЛОК 3: ГЕНЕРАТОРЫ СРЕДНИХ ЗАДАНИЙ ==========

import sympy as sp
from sympy import symbols, Eq, solve, simplify, Rational

def generate_log_equation_medium() -> Dict[str, Any]:
    """
    Генерирует логарифмическое уравнение среднего уровня
    Пример: log₂(x+3) + log₂(x-1) = 3
    """
    x = sp.Symbol('x', real=True)
    
    # Случайные параметры
    base = random.choice([2, 3, 5])
    a = random.randint(1, 5)
    b = random.randint(a + 1, a + 10)
    
    # Создаём уравнение: log_base(x + a) + log_base(x - 1) = log_base(b)
    # Преобразуем: log_base((x+a)/(x-1)) = log_base(b)
    # (x+a)/(x-1) = b
    # x + a = b(x - 1)
    # x + a = bx - b
    # bx - x = a + b
    # x(b - 1) = a + b
    # x = (a + b) / (b - 1)
    
    if b == 1:
        b = 2
    
    numerator = a + b
    denominator = b - 1
    
    if numerator % denominator == 0:
        solution = numerator // denominator
    else:
        solution = Rational(numerator, denominator)
    
    # Проверяем ОДЗ: x + a > 0, x - 1 > 0
    if isinstance(solution, sp.Rational):
        solution_float = float(solution)
        if solution_float <= 1 or solution_float <= -a:
            # Перегенерируем
            return generate_log_equation_medium()
    
    question = f"Решите уравнение: log_{base}(x + {a}) + log_{base}(x - 1) = log_{base}({b})"
    
    if isinstance(solution, sp.Rational):
        if solution.denominator == 1:
            answer = str(solution.numerator)
        else:
            answer = f"{solution.numerator}/{solution.denominator}"
    else:
        answer = str(solution)
    
    explanation = f"Сумма логарифмов: log_{base}((x+{a})(x-1)) = log_{base}({b})\n"
    explanation += f"(x+{a})(x-1) = {b}\n"
    explanation += f"x² + ({a}-1)x - {a} = {b}\n"
    explanation += f"x² + ({a-1})x - {a+b} = 0 → x = {answer}"
    
    return {
        "question": question,
        "correct_answer": answer,
        "explanation": explanation,
        "question_type": "text",
        "difficulty": 2
    }


def generate_derivative_medium() -> Dict[str, Any]:
    """
    Генерирует задание на производную среднего уровня
    Пример: Найдите производную функции f(x) = 3x²·sin(x)
    """
    x = sp.Symbol('x')
    
    # Типы функций
    func_types = [
        ('polynomial', lambda: random.choice([3, 4, 5]) * x**random.choice([2, 3, 4])),
        ('trig', lambda: random.choice([2, 3]) * sp.sin(x) + random.choice([1, 2]) * sp.cos(x)),
        ('product', lambda: (random.choice([2, 3]) * x**2) * sp.sin(x)),
        ('quotient', lambda: (x**2 + 1) / (x + 2))
    ]
    
    func_type, func_gen = random.choice(func_types)
    f = func_gen()
    
    # Вычисляем производную
    f_prime = sp.diff(f, x)
    
    # Упрощаем
    f_simplified = sp.simplify(f)
    f_prime_simplified = sp.simplify(f_prime)
    
    # Преобразуем в читаемый формат
    from sympy.printing import str as sympy_str
    question = f"Найдите производную функции: f(x) = {sympy_str(f_simplified)}"
    answer = sympy_str(f_prime_simplified)
    
    explanation = f"f'(x) = d/dx [{sympy_str(f_simplified)}] = {answer}"
    
    return {
        "question": question,
        "correct_answer": answer,
        "explanation": explanation,
        "question_type": "text",
        "difficulty": 2
    }


def generate_quadratic_equation_medium() -> Dict[str, Any]:
    """
    Генерирует квадратное уравнение с целыми корнями
    Пример: x² - 5x + 6 = 0 (корни 2 и 3)
    """
    # Генерируем два целых корня
    root1 = random.randint(-5, 5)
    root2 = random.randint(-5, 5)
    
    while root2 == root1:
        root2 = random.randint(-5, 5)
    
    # Строим уравнение: (x - root1)(x - root2) = 0
    # x² - (root1+root2)x + root1·root2 = 0
    a = 1
    b = -(root1 + root2)
    c = root1 * root2
    
    question = f"Решите уравнение: x² + ({b})x + ({c}) = 0"
    # Нормализуем знаки
    question = question.replace("+ (-", "- ").replace("+ (", "+ ").replace(" - (", " - ").replace("( -", "-")
    
    # Форматируем ответ
    if root1 == -root2:
        answer = f"x = ±{abs(root1)}"
    else:
        answer = f"x = {root1}, x = {root2}"
    
    explanation = f"Дискриминант: D = {b}² - 4·1·{c} = {b**2 - 4*c}\n"
    explanation += f"x₁ = {root1}, x₂ = {root2}"
    
    return {
        "question": question,
        "correct_answer": answer,
        "explanation": explanation,
        "question_type": "text",
        "difficulty": 2
    }


def generate_trig_equation_medium() -> Dict[str, Any]:
    """
    Генерирует тригонометрическое уравнение среднего уровня
    Пример: sin(x) = 0.5
    """
    # Стандартные углы
    angles = {
        0: (0, "0"),
        30: (1/2, "π/6"),
        45: (math.sqrt(2)/2, "π/4"),
        60: (math.sqrt(3)/2, "π/3"),
        90: (1, "π/2")
    }
    
    import math
    import random
    
    angle_deg = random.choice([30, 45, 60])
    func = random.choice(['sin', 'cos'])
    
    if func == 'sin':
        value = angles[angle_deg][0]
        angle_rad = angles[angle_deg][1]
        question = f"Решите уравнение: sin(x) = {value}"
        answer = f"x = {angle_rad} + 2πk, x = π - {angle_rad} + 2πk, k∈Z"
    else:
        value = angles[angle_deg][0]
        angle_rad = angles[angle_deg][1]
        question = f"Решите уравнение: cos(x) = {value}"
        answer = f"x = ±{angle_rad} + 2πk, k∈Z"
    
    explanation = f"cos({angle_deg}°) = {value}, sin({angle_deg}°) = {value}"
    
    return {
        "question": question,
        "correct_answer": answer,
        "explanation": explanation,
        "question_type": "text",
        "difficulty": 2
    }


def check_medium_answer(user_answer: str, correct_answer: str, question: str) -> tuple:
    """
    Проверяет ответ на среднее задание с учётом возможных форматов
    Возвращает (is_correct, score, feedback)
    """
    import re
    
    user = user_answer.lower().strip()
    correct = correct_answer.lower().strip()
    
    # Полное совпадение
    if user == correct:
        return True, 100, "✅ Верно!"
    
    # Для уравнений с двумя корнями (разный порядок)
    if 'x =' in user and 'x =' in correct:
        # Извлекаем числа
        user_numbers = set(re.findall(r'-?\d+', user))
        correct_numbers = set(re.findall(r'-?\d+', correct))
        if user_numbers == correct_numbers:
            return True, 100, "✅ Верно!"
    
    # Для тригонометрических уравнений (приближённо)
    if 'π' in user or 'pi' in user:
        # Допускаем различные формы записи
        user_clean = re.sub(r'[^0-9π/+\-k]', '', user)
        correct_clean = re.sub(r'[^0-9π/+\-k]', '', correct)
        if user_clean == correct_clean:
            return True, 100, "✅ Верно!"
    
    # Частично правильно (50%)
    if any(word in user for word in correct.split()[:2]):
        return False, 50, "⚠️ Частично верно. Проверь полное решение."
    
    return False, 0, "❌ Неправильно. Попробуй ещё раз."


# ========== ГЕНЕРАТОРЫ ДЛЯ ПРОЦЕНТОВ (A1) - БЛОК 3 ==========

def generate_percent_increase_medium() -> Dict[str, Any]:
    """
    Генерирует задание на процентное изменение
    Пример: Цену товара повысили на 25%, затем ещё на 10%. На сколько процентов повысилась цена?
    """
    # Генерируем два последовательных изменения
    percent1 = random.choice([10, 15, 20, 25, 30])
    percent2 = random.choice([5, 10, 15, 20])
    
    # Расчёт: 1.25 * 1.10 = 1.375 → 37.5%
    multiplier1 = 1 + percent1 / 100
    multiplier2 = 1 + percent2 / 100
    total_multiplier = multiplier1 * multiplier2
    total_percent = round((total_multiplier - 1) * 100, 1)
    
    # Если получилось не целое, округляем
    if total_percent.is_integer():
        total_percent = int(total_percent)
    
    question = f"Цену товара сначала повысили на {percent1}%, а затем ещё на {percent2}%. На сколько процентов повысилась цена по сравнению с первоначальной?"
    answer = str(total_percent)
    explanation = f"После первого повышения: 1 + {percent1/100} = {multiplier1}\n"
    explanation += f"После второго: {multiplier1} × {multiplier2} = {total_multiplier}\n"
    explanation += f"Итоговое изменение: ({total_multiplier} - 1) × 100% = {total_percent}%"
    
    return {
        "question": question,
        "correct_answer": answer,
        "explanation": explanation,
        "question_type": "number",
        "difficulty": 2
    }


def generate_percent_discount_medium() -> Dict[str, Any]:
    """
    Генерирует задание на нахождение первоначальной цены
    Пример: После скидки 20% товар стоит 800 рублей. Найдите первоначальную цену.
    """
    discount = random.choice([10, 15, 20, 25, 30])
    final_price = random.randint(500, 2000)
    
    # original * (1 - discount/100) = final_price
    # original = final_price / (1 - discount/100)
    multiplier = 1 - discount / 100
    original_price = final_price / multiplier
    
    if original_price.is_integer():
        original_price = int(original_price)
    else:
        original_price = round(original_price, 2)
        if original_price == int(original_price):
            original_price = int(original_price)
    
    question = f"После скидки {discount}% товар стоит {final_price} рублей. Найдите первоначальную цену товара."
    answer = str(original_price)
    explanation = f"Пусть x — первоначальная цена.\n"
    explanation += f"x × (1 - {discount}/100) = {final_price}\n"
    explanation += f"x × {multiplier} = {final_price}\n"
    explanation += f"x = {final_price} / {multiplier} = {original_price}"
    
    return {
        "question": question,
        "correct_answer": answer,
        "explanation": explanation,
        "question_type": "number",
        "difficulty": 2
    }


def generate_percent_interest_medium() -> Dict[str, Any]:
    """
    Генерирует задание на простые проценты (вклад)
    Пример: Вкладчик положил 10000 рублей под 8% годовых. Сколько будет через 2 года?
    """
    principal = random.randint(5000, 30000)
    rate = random.choice([5, 6, 7, 8, 9, 10])
    years = random.randint(2, 4)
    
    # Сложный процент
    final = principal * (1 + rate / 100) ** years
    
    if final.is_integer():
        final = int(final)
    else:
        final = round(final, 2)
        if final == int(final):
            final = int(final)
    
    question = f"Вкладчик положил в банк {principal} рублей под {rate}% годовых (с капитализацией процентов). Сколько рублей будет на счету через {years} года(лет)?"
    answer = str(final)
    explanation = f"Формула сложного процента: S = P × (1 + r/100)ⁿ\n"
    explanation += f"S = {principal} × (1 + {rate}/100)^{years} = {principal} × {round((1 + rate/100)**years, 4)} = {final}"
    
    return {
        "question": question,
        "correct_answer": answer,
        "explanation": explanation,
        "question_type": "number",
        "difficulty": 2
    }


# ========== ГЕНЕРАТОРЫ ДЛЯ ПЛАНИМЕТРИИ (B1) - БЛОК 3 ==========

def generate_triangle_area_medium() -> Dict[str, Any]:
    """
    Генерирует задание на площадь треугольника
    Пример: Найдите площадь треугольника со сторонами 5, 6, 7.
    """
    # Генерируем пифагоровы тройки или простые числа
    triangles = [
        {"a": 3, "b": 4, "c": 5, "area": 6},
        {"a": 5, "b": 12, "c": 13, "area": 30},
        {"a": 6, "b": 8, "c": 10, "area": 24},
        {"a": 8, "b": 15, "c": 17, "area": 60},
        {"a": 9, "b": 12, "c": 15, "area": 54},
    ]
    
    triangle = random.choice(triangles)
    
    question = f"Найдите площадь треугольника со сторонами {triangle['a']}, {triangle['b']}, {triangle['c']}."
    answer = str(triangle['area'])
    explanation = f"По формуле Герона: p = ({triangle['a']}+{triangle['b']}+{triangle['c']})/2 = {triangle['a']+triangle['b']+triangle['c']}/2 = {(triangle['a']+triangle['b']+triangle['c'])/2}\n"
    explanation += f"S = √(p(p-a)(p-b)(p-c)) = {triangle['area']}"
    
    return {
        "question": question,
        "correct_answer": answer,
        "explanation": explanation,
        "question_type": "number",
        "difficulty": 2
    }


def generate_right_triangle_medium() -> Dict[str, Any]:
    """
    Генерирует задание на прямоугольный треугольник
    Пример: В прямоугольном треугольнике катеты 6 и 8. Найдите гипотенузу.
    """
    # Пифагоровы тройки
    triples = [
        {"a": 3, "b": 4, "c": 5},
        {"a": 5, "b": 12, "c": 13},
        {"a": 6, "b": 8, "c": 10},
        {"a": 8, "b": 15, "c": 17},
        {"a": 7, "b": 24, "c": 25},
        {"a": 9, "b": 12, "c": 15},
    ]
    
    triple = random.choice(triples)
    
    # Выбираем, что просить: найти гипотенузу или катет
    question_type = random.choice(['hypotenuse', 'leg'])
    
    if question_type == 'hypotenuse':
        question = f"В прямоугольном треугольнике катеты равны {triple['a']} и {triple['b']}. Найдите гипотенузу."
        answer = str(triple['c'])
        explanation = f"По теореме Пифагора: c² = {triple['a']}² + {triple['b']}² = {triple['a']**2 + triple['b']**2}, c = {triple['c']}"
    else:
        # Найти катет по гипотенузе и другому катету
        question = f"В прямоугольном треугольнике гипотенуза равна {triple['c']}, а один из катетов равен {triple['a']}. Найдите второй катет."
        answer = str(triple['b'])
        explanation = f"По теореме Пифагора: {triple['b']}² = {triple['c']}² - {triple['a']}² = {triple['c']**2 - triple['a']**2}, {triple['b']} = {triple['b']}"
    
    return {
        "question": question,
        "correct_answer": answer,
        "explanation": explanation,
        "question_type": "number",
        "difficulty": 2
    }


def generate_circle_geometry_medium() -> Dict[str, Any]:
    """
    Генерирует задание на окружность
    Пример: Найдите длину окружности радиусом 5.
    """
    import math
    
    radius = random.randint(3, 12)
    diameter = 2 * radius
    
    question_type = random.choice(['circumference', 'area'])
    
    if question_type == 'circumference':
        question = f"Найдите длину окружности, радиус которой равен {radius} (π ≈ 3.14)."
        answer = str(round(2 * math.pi * radius, 2))
        explanation = f"Формула длины окружности: C = 2πR = 2 × 3.14 × {radius} = {answer}"
    else:
        question = f"Найдите площадь круга, радиус которого равен {radius} (π ≈ 3.14)."
        answer = str(round(math.pi * radius ** 2, 2))
        explanation = f"Формула площади круга: S = πR² = 3.14 × {radius}² = {answer}"
    
    return {
        "question": question,
        "correct_answer": answer,
        "explanation": explanation,
        "question_type": "number",
        "difficulty": 2
    }


def generate_triangle_similarity_medium() -> Dict[str, Any]:
    """
    Генерирует задание на подобие треугольников
    """
    # Коэффициенты подобия
    ratio = random.choice([2, 3, 4, 1.5])
    side1 = random.randint(5, 15)
    side2 = side1 * ratio
    
    if ratio == int(ratio):
        ratio = int(ratio)
    
    question = f"Треугольник ABC подобен треугольнику A₁B₁C₁. Сторона AB = {side1}, а соответствующая ей сторона A₁B₁ = {side2}. Найдите коэффициент подобия."
    answer = str(ratio)
    explanation = f"Коэффициент подобия k = A₁B₁ / AB = {side2} / {side1} = {ratio}"
    
    return {
        "question": question,
        "correct_answer": answer,
        "explanation": explanation,
        "question_type": "number",
        "difficulty": 2
    }


# ========== ГЕНЕРАТОРЫ ДЛЯ СТЕПЕНЕЙ И КОРНЕЙ (A2) - БЛОК 3 ==========

def generate_power_equation_medium() -> Dict[str, Any]:
    """
    Генерирует уравнение со степенями
    Пример: 2^(x+1) = 16
    """
    bases = [2, 3, 4, 5]
    base = random.choice(bases)
    
    # Генерируем правую часть как степень основания
    right_power = random.randint(2, 5)
    right_value = base ** right_power
    
    # Левая часть: base^(x + a) или base^(x - a)
    shift = random.randint(1, 3)
    if random.choice([True, False]):
        question = f"Решите уравнение: {base}^(x + {shift}) = {right_value}"
        # base^(x+shift) = base^right_power → x+shift = right_power
        solution = right_power - shift
    else:
        question = f"Решите уравнение: {base}^(x - {shift}) = {right_value}"
        solution = right_power + shift
    
    answer = str(solution)
    explanation = f"{base}^(x {'+' if shift > 0 else '-'} {shift}) = {base}^{right_power}\n"
    explanation += f"x {'+' if shift > 0 else '-'} {shift} = {right_power}\n"
    explanation += f"x = {solution}"
    
    return {
        "question": question,
        "correct_answer": answer,
        "explanation": explanation,
        "question_type": "number",
        "difficulty": 2
    }


def generate_root_equation_medium() -> Dict[str, Any]:
    """
    Генерирует уравнение с корнями
    Пример: √(x + 5) = 7
    """
    # Генерируем: √(x + a) = b
    a = random.randint(1, 10)
    b = random.randint(2, 8)
    
    # Решение: x + a = b² → x = b² - a
    solution = b**2 - a
    
    question = f"Решите уравнение: √(x + {a}) = {b}"
    answer = str(solution)
    explanation = f"Возводим обе части в квадрат: x + {a} = {b}² = {b**2}\n"
    explanation += f"x = {b**2} - {a} = {solution}\n"
    explanation += f"Проверка ОДЗ: x + {a} = {solution + a} = {b**2} ≥ 0"
    
    return {
        "question": question,
        "correct_answer": answer,
        "explanation": explanation,
        "question_type": "number",
        "difficulty": 2
    }


def generate_complex_root_medium() -> Dict[str, Any]:
    """
    Генерирует более сложное уравнение с корнями
    Пример: √(2x + 3) = 5
    """
    # √(ax + b) = c
    a = random.choice([2, 3, 4])
    c = random.randint(2, 6)
    
    # Генерируем b так, чтобы решение было целым
    # √(a*x + b) = c → a*x + b = c² → a*x = c² - b → x = (c² - b)/a
    # Нужно, чтобы (c² - b) делилось на a
    c_squared = c**2
    b = random.randint(1, c_squared - 1)
    
    while (c_squared - b) % a != 0:
        b = random.randint(1, c_squared - 1)
    
    solution = (c_squared - b) // a
    
    question = f"Решите уравнение: √({a}x + {b}) = {c}"
    answer = str(solution)
    explanation = f"Возводим в квадрат: {a}x + {b} = {c}² = {c_squared}\n"
    explanation += f"{a}x = {c_squared} - {b} = {c_squared - b}\n"
    explanation += f"x = {c_squared - b} / {a} = {solution}"
    
    return {
        "question": question,
        "correct_answer": answer,
        "explanation": explanation,
        "question_type": "number",
        "difficulty": 2
    }


# ========== ГЕНЕРАТОРЫ ДЛЯ ПОКАЗАТЕЛЬНЫХ УРАВНЕНИЙ (A10) - БЛОК 3 ==========

def generate_exponential_same_base_medium() -> Dict[str, Any]:
    """
    Генерирует показательное уравнение с одинаковыми основаниями
    Пример: 2^(x+1) = 2^(5)
    """
    base = random.choice([2, 3, 5, 7])
    
    # Генерируем правую степень
    right_power = random.randint(2, 6)
    
    # Левая часть: x + a или x - a
    shift = random.randint(1, 3)
    if random.choice([True, False]):
        question = f"Решите уравнение: {base}^(x + {shift}) = {base}^{right_power}"
        solution = right_power - shift
    else:
        question = f"Решите уравнение: {base}^(x - {shift}) = {base}^{right_power}"
        solution = right_power + shift
    
    answer = str(solution)
    explanation = f"Основания одинаковы, поэтому: x {'+' if shift > 0 else '-'} {shift} = {right_power}\n"
    explanation += f"x = {solution}"
    
    return {
        "question": question,
        "correct_answer": answer,
        "explanation": explanation,
        "question_type": "number",
        "difficulty": 2
    }


def generate_exponential_diff_bases_medium() -> Dict[str, Any]:
    """
    Генерирует показательное уравнение с разными основаниями, сводящееся к одинаковым
    Пример: 4^(x) = 2^(x+3)
    """
    # 4^x = 2^(2x) = 2^(x+3) → 2x = x+3 → x = 3
    base_left = 4
    base_right = 2
    shift = random.randint(2, 5)
    
    # 4^x = 2^(2x) = 2^(x + shift) → 2x = x + shift → x = shift
    solution = shift
    
    question = f"Решите уравнение: {base_left}^x = {base_right}^(x + {shift})"
    answer = str(solution)
    explanation = f"{base_left}^x = ({base_right}^2)^x = {base_right}^(2x)\n"
    explanation += f"Получаем: {base_right}^(2x) = {base_right}^(x + {shift})\n"
    explanation += f"2x = x + {shift}\n"
    explanation += f"x = {solution}"
    
    return {
        "question": question,
        "correct_answer": answer,
        "explanation": explanation,
        "question_type": "number",
        "difficulty": 2
    }


def generate_exponential_equation_medium() -> Dict[str, Any]:
    """
    Генерирует показательное уравнение: a^(x) = b
    Пример: 2^(x) = 8
    """
    base = random.choice([2, 3, 5])
    power = random.randint(2, 4)
    right_value = base ** power
    
    question = f"Решите уравнение: {base}^x = {right_value}"
    answer = str(power)
    explanation = f"{base}^x = {right_value} = {base}^{power}\n"
    explanation += f"Следовательно, x = {power}"
    
    return {
        "question": question,
        "correct_answer": answer,
        "explanation": explanation,
        "question_type": "number",
        "difficulty": 2
    }


# ========== ГЕНЕРАТОРЫ ДЛЯ СИСТЕМ УРАВНЕНИЙ (A12) - БЛОК 3 ==========

def generate_linear_system_medium() -> Dict[str, Any]:
    """
    Генерирует систему линейных уравнений с целыми решениями
    Пример:
    2x + y = 8
    x - y = 1
    Решение: x = 3, y = 2
    """
    # Генерируем решение x и y
    x = random.randint(-5, 10)
    y = random.randint(-5, 10)
    
    # Генерируем коэффициенты
    a1 = random.choice([1, 2, 3])
    b1 = random.choice([1, 2, 3])
    c1 = a1 * x + b1 * y
    
    a2 = random.choice([1, 2, 3])
    b2 = random.choice([1, 2, 3])
    # Избегаем пропорциональности
    while a1 * b2 == a2 * b1:
        a2 = random.choice([1, 2, 3])
        b2 = random.choice([1, 2, 3])
    c2 = a2 * x + b2 * y
    
    # Форматируем знаки
    def format_sign(coef, var):
        if coef == 0:
            return ""
        if coef == 1:
            return f"+ {var}"
        if coef == -1:
            return f"- {var}"
        if coef > 0:
            return f"+ {coef}{var}"
        return f"- {abs(coef)}{var}"
    
    eq1 = f"{a1}x {format_sign(b1, 'y')} = {c1}".replace("+ -", "- ").lstrip("+")
    eq2 = f"{a2}x {format_sign(b2, 'y')} = {c2}".replace("+ -", "- ").lstrip("+")
    
    question = f"Решите систему уравнений:\n{eq1}\n{eq2}\n\nВведите ответ в формате: x = число, y = число"
    answer = f"x = {x}, y = {y}"
    explanation = f"Решение: x = {x}, y = {y}\n"
    explanation += f"Проверка:\n"
    explanation += f"{a1}·{x} + {b1}·{y} = {a1*x + b1*y} = {c1}\n"
    explanation += f"{a2}·{x} + {b2}·{y} = {a2*x + b2*y} = {c2}"
    
    return {
        "question": question,
        "correct_answer": answer,
        "explanation": explanation,
        "question_type": "text",
        "difficulty": 2
    }


def generate_substitution_system_medium() -> Dict[str, Any]:
    """
    Генерирует систему уравнений для метода подстановки
    Пример:
    y = 2x + 1
    3x + y = 10
    """
    x = random.randint(-5, 10)
    k = random.choice([2, 3, 4])
    b = random.randint(-5, 5)
    
    # y = kx + b
    y = k * x + b
    
    # Второе уравнение: ax + by = c
    a = random.choice([1, 2, 3])
    b_coef = random.choice([1, 2, 3])
    c = a * x + b_coef * y
    
    eq1 = f"y = {k}x + {b}"
    if b < 0:
        eq1 = f"y = {k}x - {abs(b)}"
    
    eq2 = f"{a}x + {b_coef}y = {c}"
    
    question = f"Решите систему уравнений:\n{eq1}\n{eq2}\n\nВведите ответ в формате: x = число, y = число"
    answer = f"x = {x}, y = {y}"
    explanation = f"Подставляем y из первого уравнения во второе:\n"
    explanation += f"{a}x + {b_coef}({k}x + {b}) = {c}\n"
    explanation += f"{a}x + {b_coef*k}x + {b_coef*b} = {c}\n"
    explanation += f"{a + b_coef*k}x = {c - b_coef*b}\n"
    explanation += f"x = {x}, y = {y}"
    
    return {
        "question": question,
        "correct_answer": answer,
        "explanation": explanation,
        "question_type": "text",
        "difficulty": 2
    }

# ========== РЕГИСТРАЦИЯ ГЕНЕРАТОРОВ ПО ТЕМАМ ==========

# ========== РЕГИСТРАЦИЯ ГЕНЕРАТОРОВ ПО ТЕМАМ ==========

GENERATORS = {
    "A3": {  # Логарифмы
        "simple": [generate_log_simple, generate_log_sum_simple],
        "medium": [generate_log_equation_medium]
    },
    "A1": {  # Проценты
        "simple": [generate_percent_simple],
        "medium": [generate_percent_increase_medium, generate_percent_discount_medium, generate_percent_interest_medium]
    },
    "A2": {  # Степени и корни
        "simple": [generate_power_simple, generate_square_root_simple],
        "medium": [generate_power_equation_medium, generate_root_equation_medium, generate_complex_root_medium]
    },
    "A10": {  # Показательные уравнения
        "simple": [],
        "medium": [generate_exponential_same_base_medium, generate_exponential_diff_bases_medium, generate_exponential_equation_medium]
    },
    "A12": {  # Системы уравнений
        "simple": [generate_system_simple_1, generate_system_simple_2],
        "medium": [generate_linear_system_medium, generate_substitution_system_medium]
    },
    "A14": {  # Производная
        "simple": [],
        "medium": [generate_derivative_medium]
    },
    "A7": {  # Квадратные уравнения
        "simple": [],
        "medium": [generate_quadratic_equation_medium]
    },
    "B1": {  # Планиметрия
        "simple": [],
        "medium": [generate_triangle_area_medium, generate_right_triangle_medium, generate_circle_geometry_medium, generate_triangle_similarity_medium]
    }
}

def generate_task(topic_id: str, block: int, microtopic_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Генерирует задание для указанной темы и блока"""
    
    if topic_id not in GENERATORS:
        return None
    
    if block == 2:
        # Простые задания
        generators_list = GENERATORS[topic_id].get("simple", [])
        if not generators_list:
            return None
        generator = random.choice(generators_list)
        task = generator()
        task["topic_id"] = topic_id
        task["block"] = block
        return task
    
    elif block == 3:
        # Средние задания (НОВАЯ ФУНКЦИОНАЛЬНОСТЬ)
        generators_list = GENERATORS[topic_id].get("medium", [])
        if not generators_list:
            return None
        generator = random.choice(generators_list)
        task = generator()
        task["topic_id"] = topic_id
        task["block"] = block
        return task
    
    return None


def can_generate(topic_id: str, block: int) -> bool:
    """Проверяет, поддерживается ли генерация для данной темы и блока"""
    if topic_id not in GENERATORS:
        return False
    
    if block == 2:
        return bool(GENERATORS[topic_id].get("simple"))
    elif block == 3:
        return bool(GENERATORS[topic_id].get("medium"))
    
    return False
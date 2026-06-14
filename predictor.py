"""
Модуль расчёта прогнозов баллов ЕГЭ для Фрэда
"""

from datetime import datetime, date, timedelta

# Константы
EXAM_DATE = date(2027, 6, 8)  # дата ЕГЭ по профильной математике 2026
MAX_PRIMARY_SCORE = 32

def is_weekend(d):
    """Проверяет, является ли день выходным"""
    return d.weekday() >= 5

def is_holiday(d):
    """Проверяет, является ли день праздничным"""
    holidays = [
        date(2026, 1, 1), date(2026, 1, 2), date(2026, 1, 3), date(2026, 1, 4),
        date(2026, 1, 5), date(2026, 1, 6), date(2026, 1, 7), date(2026, 2, 23),
        date(2026, 3, 8), date(2026, 5, 1), date(2026, 5, 9)
    ]
    return d in holidays

def is_study_day(d):
    """Определяет, является ли день учебным"""
    if is_weekend(d) or is_holiday(d):
        return False
    return True

def calculate_available_hours(settings):
    """Рассчитывает доступные часы для подготовки к ЕГЭ"""
    today = date.today()
    exam_date = EXAM_DATE
    
    total_hours = 0
    current = today
    while current <= exam_date:
        if is_study_day(current):
            daily_hours = settings.get('hours_per_study_day', 2)
        else:
            daily_hours = settings.get('hours_per_holiday', 8)
        total_hours += daily_hours
        current += timedelta(days=1)
    
    other_subjects = settings.get('other_subjects_count', 3)
    total_hours = total_hours / (other_subjects + 1)
    total_hours = total_hours * 0.7
    
    return int(total_hours)

def primary_to_test(primary_score):
    """Переводит первичный балл в тестовый (стобалльный)"""
    if primary_score >= 30:
        return 100
    elif primary_score >= 28:
        return 96 + (primary_score - 28) * 2
    elif primary_score >= 24:
        return 86 + (primary_score - 24) * 2.5
    elif primary_score >= 17:
        return 70 + (primary_score - 17) * 2
    elif primary_score >= 12:
        return 50 + (primary_score - 12) * 3
    elif primary_score >= 7:
        return 30 + (primary_score - 7) * 4
    elif primary_score >= 5:
        return 20 + (primary_score - 5) * 5
    else:
        return primary_score * 4

def calculate_growth_rate(current_primary):
    """Определяет эффективность занятий (сколько баллов можно набрать за час)"""
    if current_primary < 10:
        return 0.20
    elif current_primary < 17:
        return 0.12
    else:
        return 0.06

def calculate_nvb(current_primary, available_hours):
    """Рассчитывает наиболее вероятный балл (НВБ)"""
    growth_rate = calculate_growth_rate(current_primary)
    potential_growth = available_hours * growth_rate
    final_primary = min(MAX_PRIMARY_SCORE, current_primary + potential_growth)
    final_test = primary_to_test(final_primary)
    return int(final_test)

def get_motivation_message(current_primary, target_primary, available_hours, predicted_score):
    """Генерирует мотивационное сообщение"""
    current_test = primary_to_test(current_primary)
    target_test = primary_to_test(target_primary)
    gap = target_test - predicted_score
    days_until_exam = (EXAM_DATE - date.today()).days
    monthly_potential = int(available_hours / (days_until_exam / 30) * 0.8)
    
    messages = []
    
    if predicted_score >= target_test:
        messages.append("🎉 Отлично! Ты на верном пути к цели!")
    elif gap > 30:
        messages.append(f"⚠️ До цели осталось {gap} баллов. Не отчаивайся!")
    elif gap > 15:
        messages.append(f"🎯 До цели осталось {gap} баллов. Ты можешь это сделать!")
    else:
        messages.append(f"💪 Всего {gap} баллов до цели! Не сдавайся!")
    
    messages.append(f"📈 В этом месяце ты можешь заработать до {monthly_potential} баллов!")
    
    if available_hours < 50:
        messages.append("⏰ Времени осталось немного. Каждый час на вес золота!")
    
    return "\n\n".join(messages)

def get_weekly_goal(current_primary, available_hours):
    """Рассчитывает цель на неделю"""
    days_until_exam = (EXAM_DATE - date.today()).days
    weeks_until_exam = max(1, days_until_exam / 7)
    weekly_hours = available_hours / weeks_until_exam
    weekly_growth = weekly_hours * calculate_growth_rate(current_primary)
    weekly_points = int(primary_to_test(current_primary + weekly_growth) - primary_to_test(current_primary))
    
    return {
        "hours_per_week": int(weekly_hours),
        "points_per_week": weekly_points
    }
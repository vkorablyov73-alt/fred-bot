import sqlite3
from datetime import datetime
import json
import logging

DB_NAME = 'fred_users.db'

def init_db():
    """Создаёт таблицы, если их нет"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Таблица пользователей
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id TEXT PRIMARY KEY,
                  username TEXT,
                  first_name TEXT,
                  first_seen TIMESTAMP,
                  last_seen TIMESTAMP,
                  total_messages INTEGER DEFAULT 0,
                  current_mode TEXT DEFAULT 'study')''')
    
    # Таблица сообщений (история диалогов)
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id TEXT,
                  role TEXT,
                  content TEXT,
                  timestamp TIMESTAMP)''')
    
    # Таблица тем (список всех тем ЕГЭ)
    c.execute('''CREATE TABLE IF NOT EXISTS topics
                 (topic_id TEXT PRIMARY KEY,
                  topic_name TEXT,
                  difficulty INTEGER)''')
    
    # Таблица прогресса по темам для каждого пользователя
    c.execute('''CREATE TABLE IF NOT EXISTS user_topics
                 (user_id TEXT,
                  topic_id TEXT,
                  score INTEGER DEFAULT 3,
                  attempts INTEGER DEFAULT 0,
                  correct INTEGER DEFAULT 0,
                  last_attempt TIMESTAMP,
                  PRIMARY KEY (user_id, topic_id))''')
    
    conn.commit()
    conn.close()
    logging.info("База данных инициализирована")
    
    # Заполняем темы, если таблица пуста
    _init_topics()
    
    # Инициализируем таблицы диагностики
    init_diagnostic_tables()

def _init_topics():
    """Заполняет список тем ЕГЭ"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Проверяем, есть ли уже темы
    c.execute("SELECT COUNT(*) FROM topics")
    if c.fetchone()[0] == 0:
        topics = [
            ("A1", "Проценты, отношения", 1),
            ("A2", "Степени и корни", 1),
            ("A3", "Логарифмы", 2),
            ("A4", "Тождественные преобразования", 1),
            ("A5", "Функции и графики", 1),
            ("A6", "Линейные уравнения", 1),
            ("A7", "Квадратные уравнения", 2),
            ("A8", "Рациональные уравнения", 2),
            ("A9", "Иррациональные уравнения", 2),
            ("A10", "Показательные уравнения", 2),
            ("A11", "Логарифмические уравнения", 2),
            ("A12", "Системы уравнений", 2),
            ("A13", "Текстовые задачи", 2),
            ("A14", "Производная (определение)", 2),
            ("A15", "Производная (исследование)", 2),
            ("B1", "Планиметрия (треугольники)", 1),
            ("B2", "Планиметрия (четырехугольники)", 2),
            ("B3", "Планиметрия (окружность)", 2),
            ("B4", "Стереометрия (многогранники)", 2),
            ("B5", "Стереометрия (тела вращения)", 2),
            ("B6", "Векторы", 1),
            ("B7", "Теория вероятностей", 2),
            ("B8", "Экономические задачи", 3),
        ]
        c.executemany("INSERT INTO topics (topic_id, topic_name, difficulty) VALUES (?, ?, ?)", topics)
        conn.commit()
        logging.info(f"Добавлено {len(topics)} тем")
    
    conn.close()

def init_diagnostic_tables():
    """Создаёт таблицы для диагностики, если их нет"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Таблица заданий
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic_id TEXT NOT NULL,
        microtopic_id TEXT,
        block INTEGER NOT NULL,
        difficulty INTEGER DEFAULT 1,
        question TEXT NOT NULL,
        question_type TEXT DEFAULT 'text',
        correct_answer TEXT NOT NULL,
        options TEXT,
        explanation TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('CREATE INDEX IF NOT EXISTS idx_tasks_topic ON tasks(topic_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_tasks_block ON tasks(block)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_tasks_microtopic ON tasks(microtopic_id)')
    
    # Таблица результатов диагностики
    c.execute('''CREATE TABLE IF NOT EXISTS diagnostic_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        topic_id TEXT NOT NULL,
        microtopic_id TEXT,
        task_id INTEGER,
        block INTEGER,
        user_answer TEXT,
        is_correct BOOLEAN,
        score INTEGER,
        response_time INTEGER,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (task_id) REFERENCES tasks(id)
    )''')
    
    c.execute('CREATE INDEX IF NOT EXISTS idx_results_user ON diagnostic_results(user_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_results_topic ON diagnostic_results(topic_id)')
    
    # Таблица прогресса по микротемам
    c.execute('''CREATE TABLE IF NOT EXISTS microtopic_progress (
        user_id TEXT NOT NULL,
        microtopic_id TEXT NOT NULL,
        status TEXT DEFAULT 'not_started',
        best_score INTEGER DEFAULT 0,
        attempts INTEGER DEFAULT 0,
        last_attempt TIMESTAMP,
        PRIMARY KEY (user_id, microtopic_id)
    )''')
    
    conn.commit()
    conn.close()
    logging.info("Таблицы для диагностики инициализированы")

def get_or_create_user(user_id, username=None, first_name=None):
    """Возвращает пользователя из БД или создаёт нового"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = c.fetchone()
    
    if user is None:
        now = datetime.now().isoformat()
        c.execute('''INSERT INTO users 
                     (user_id, username, first_name, first_seen, last_seen, total_messages)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (user_id, username, first_name, now, now, 0))
        conn.commit()
        logging.info(f"Новый пользователь: {user_id}")
        
        c.execute("SELECT topic_id FROM topics")
        topics = c.fetchall()
        for topic in topics:
            c.execute('''INSERT OR IGNORE INTO user_topics 
                         (user_id, topic_id, score, attempts, correct)
                         VALUES (?, ?, 3, 0, 0)''',
                      (user_id, topic[0]))
        conn.commit()
    
    conn.close()
    return user

def update_last_seen(user_id):
    """Обновляет время последнего визита"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("UPDATE users SET last_seen = ?, total_messages = total_messages + 1 WHERE user_id = ?",
              (now, user_id))
    conn.commit()
    conn.close()

def save_message(user_id, role, content):
    """Сохраняет сообщение в историю"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute('''INSERT INTO messages (user_id, role, content, timestamp)
                 VALUES (?, ?, ?, ?)''',
              (user_id, role, content, now))
    conn.commit()
    conn.close()

def get_recent_messages(user_id, limit=20):
    """Возвращает последние N сообщений пользователя"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''SELECT role, content FROM messages 
                 WHERE user_id = ? 
                 ORDER BY timestamp DESC LIMIT ?''',
              (user_id, limit))
    rows = c.fetchall()
    conn.close()
    
    messages = [{"role": row[0], "content": row[1]} for row in reversed(rows)]
    return messages

def clear_user_history(user_id):
    """Очищает историю сообщений пользователя"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def update_topic_score(user_id, topic_id, is_correct):
    """Обновляет оценку по теме на основе правильности ответа"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute("SELECT score, attempts, correct FROM user_topics WHERE user_id = ? AND topic_id = ?",
              (user_id, topic_id))
    row = c.fetchone()
    
    if row:
        current_score, attempts, correct = row
        attempts += 1
        if is_correct:
            correct += 1
        
        ratio = correct / attempts if attempts > 0 else 0.5
        
        if ratio >= 0.95:
            new_score = 5
        elif ratio >= 0.85:
            new_score = 4
        elif ratio >= 0.70:
            new_score = 3
        else:
            new_score = 2
        
        c.execute('''UPDATE user_topics 
                     SET score = ?, attempts = ?, correct = ?, last_attempt = ?
                     WHERE user_id = ? AND topic_id = ?''',
                  (new_score, attempts, correct, datetime.now().isoformat(), user_id, topic_id))
        
        logging.info(f"Обновлена тема {topic_id} для {user_id}: score={new_score}, ratio={ratio:.2f}")
    
    conn.commit()
    conn.close()

def get_weak_topics(user_id, limit=5):
    """Возвращает самые слабые темы пользователя"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''SELECT t.topic_name, ut.score, ut.attempts, ut.correct
                 FROM user_topics ut
                 JOIN topics t ON ut.topic_id = t.topic_id
                 WHERE ut.user_id = ? AND ut.attempts >= 2
                 ORDER BY ut.score ASC, ut.attempts DESC
                 LIMIT ?''', (user_id, limit))
    rows = c.fetchall()
    conn.close()
    return rows

def get_topic_summary(user_id):
    """Возвращает сводку по всем темам"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''SELECT t.topic_name, ut.score, ut.attempts
                 FROM user_topics ut
                 JOIN topics t ON ut.topic_id = t.topic_id
                 WHERE ut.user_id = ?
                 ORDER BY t.topic_id''', (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_user_mode(user_id):
    """Возвращает текущий режим пользователя"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT current_mode FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 'study'

def set_user_mode(user_id, mode):
    """Устанавливает режим пользователя"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET current_mode = ? WHERE user_id = ?", (mode, user_id))
    conn.commit()
    conn.close()

# ========== ФУНКЦИИ ДЛЯ ДИАГНОСТИКИ ==========

def add_task(topic_id, microtopic_id, block, difficulty, question, correct_answer, 
             question_type='text', options=None, explanation=None):
    """Добавляет новое задание в базу"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute('''INSERT INTO tasks 
                 (topic_id, microtopic_id, block, difficulty, question, 
                  question_type, correct_answer, options, explanation)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (topic_id, microtopic_id, block, difficulty, question, 
               question_type, correct_answer, json.dumps(options) if options else None, explanation))
    
    conn.commit()
    task_id = c.lastrowid
    conn.close()
    logging.info(f"Добавлено задание {task_id} для темы {topic_id}")
    return task_id

def get_tasks_by_topic(topic_id, block=None):
    """Получает все задания по теме"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    if block:
        c.execute('''SELECT id, topic_id, microtopic_id, block, difficulty, question, 
                            question_type, correct_answer, options, explanation
                     FROM tasks 
                     WHERE topic_id = ? AND block = ?
                     ORDER BY difficulty''', (topic_id, block))
    else:
        c.execute('''SELECT id, topic_id, microtopic_id, block, difficulty, question, 
                            question_type, correct_answer, options, explanation
                     FROM tasks 
                     WHERE topic_id = ?
                     ORDER BY block, difficulty''', (topic_id,))
    
    rows = c.fetchall()
    conn.close()
    
    tasks = []
    for row in rows:
        tasks.append({
            'id': row[0],
            'topic_id': row[1],
            'microtopic_id': row[2],
            'block': row[3],
            'difficulty': row[4],
            'question': row[5],
            'question_type': row[6],
            'correct_answer': row[7],
            'options': json.loads(row[8]) if row[8] else None,
            'explanation': row[9]
        })
    return tasks

def get_random_task(topic_id, block, difficulty=None):
    """Получает случайное задание по теме, блоку и сложности"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    if difficulty:
        c.execute('''SELECT id, question, question_type, correct_answer, options, explanation
                     FROM tasks 
                     WHERE topic_id = ? AND block = ? AND difficulty = ?
                     ORDER BY RANDOM() LIMIT 1''', (topic_id, block, difficulty))
    else:
        c.execute('''SELECT id, question, question_type, correct_answer, options, explanation
                     FROM tasks 
                     WHERE topic_id = ? AND block = ?
                     ORDER BY RANDOM() LIMIT 1''', (topic_id, block))
    
    row = c.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row[0],
            'question': row[1],
            'question_type': row[2],
            'correct_answer': row[3],
            'options': json.loads(row[4]) if row[4] else None,
            'explanation': row[5]
        }
    return None

def save_diagnostic_result(user_id, topic_id, task_id, block, user_answer, is_correct, score=None, response_time=None, microtopic_id=None):
    """Сохраняет результат выполнения задания"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute('''INSERT INTO diagnostic_results 
                 (user_id, topic_id, microtopic_id, task_id, block, user_answer, is_correct, score, response_time)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (user_id, topic_id, microtopic_id, task_id, block, user_answer, is_correct, score, response_time))
    
    conn.commit()
    conn.close()
    logging.info(f"Сохранён результат для пользователя {user_id}, задание {task_id}")

def get_topic_diagnostic_summary(user_id, topic_id):
    """Получает сводку по диагностике темы"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute('''SELECT block, 
                        COUNT(*) as total,
                        SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct
                 FROM diagnostic_results 
                 WHERE user_id = ? AND topic_id = ?
                 GROUP BY block''', (user_id, topic_id))
    
    rows = c.fetchall()
    conn.close()
    
    summary = {}
    for row in rows:
        block = row[0]
        total = row[1]
        correct = row[2] or 0
        summary[block] = {
            'total': total,
            'correct': correct,
            'percentage': (correct / total * 100) if total > 0 else 0
        }
    
    return summary

def update_microtopic_progress(user_id, microtopic_id, is_correct, score):
    """Обновляет прогресс по микротеме"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute('SELECT status, best_score, attempts FROM microtopic_progress WHERE user_id = ? AND microtopic_id = ?',
              (user_id, microtopic_id))
    row = c.fetchone()
    
    now = datetime.now().isoformat()
    
    if row is None:
        if is_correct and score >= 80:
            status = 'mastered'
        elif is_correct and score >= 50:
            status = 'partial'
        else:
            status = 'not_started'
        
        c.execute('''INSERT INTO microtopic_progress 
                     (user_id, microtopic_id, status, best_score, attempts, last_attempt)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (user_id, microtopic_id, status, score if is_correct else 0, 1, now))
    else:
        status, best_score, attempts = row
        new_attempts = attempts + 1
        new_best_score = max(best_score, score if is_correct else 0)
        
        if new_best_score >= 90:
            new_status = 'mastered'
        elif new_best_score >= 60:
            new_status = 'partial'
        else:
            new_status = 'not_mastered'
        
        c.execute('''UPDATE microtopic_progress 
                     SET status = ?, best_score = ?, attempts = ?, last_attempt = ?
                     WHERE user_id = ? AND microtopic_id = ?''',
                  (new_status, new_best_score, new_attempts, now, user_id, microtopic_id))
    
    conn.commit()
    conn.close()

def get_microtopic_progress(user_id, microtopic_id):
    """Получает прогресс по конкретной микротеме"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute('SELECT status, best_score, attempts, last_attempt FROM microtopic_progress WHERE user_id = ? AND microtopic_id = ?', (user_id, microtopic_id))
    row = c.fetchone()
    conn.close()
    
    if row:
        return {
            'status': row[0],
            'best_score': row[1],
            'attempts': row[2],
            'last_attempt': row[3]
        }
    return {'status': 'not_started', 'best_score': 0, 'attempts': 0}

def get_all_microtopic_progress(user_id):
    """Получает прогресс по всем микротемам для пользователя"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute('SELECT microtopic_id, status, best_score, attempts FROM microtopic_progress WHERE user_id = ?', (user_id,))
    rows = c.fetchall()
    conn.close()
    
    return {row[0]: {'status': row[1], 'best_score': row[2], 'attempts': row[3]} for row in rows}

# ========== ФУНКЦИИ ДЛЯ СТАТИСТИКИ ==========

def get_user_stats(user_id):
    """Получает статистику пользователя"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT current_primary_score, target_primary_score, hours_per_study_day, hours_per_holiday, other_subjects_count FROM user_stats WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    
    if row:
        return {
            'current_primary_score': row[0],
            'target_primary_score': row[1],
            'hours_per_study_day': row[2],
            'hours_per_holiday': row[3],
            'other_subjects_count': row[4]
        }
    return {
        'current_primary_score': 0,
        'target_primary_score': 17,
        'hours_per_study_day': 2,
        'hours_per_holiday': 8,
        'other_subjects_count': 3
    }

def update_user_stats(user_id, current_primary_score=None, target_primary_score=None, 
                      hours_per_study_day=None, hours_per_holiday=None, other_subjects_count=None):
    """Обновляет статистику пользователя"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    stats = get_user_stats(user_id)
    
    new_current = current_primary_score if current_primary_score is not None else stats['current_primary_score']
    new_target = target_primary_score if target_primary_score is not None else stats['target_primary_score']
    new_study_day = hours_per_study_day if hours_per_study_day is not None else stats['hours_per_study_day']
    new_holiday = hours_per_holiday if hours_per_holiday is not None else stats['hours_per_holiday']
    new_other = other_subjects_count if other_subjects_count is not None else stats['other_subjects_count']
    
    c.execute('''INSERT OR REPLACE INTO user_stats 
                 (user_id, current_primary_score, target_primary_score, 
                  hours_per_study_day, hours_per_holiday, other_subjects_count)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (user_id, new_current, new_target, new_study_day, new_holiday, new_other))
    
    conn.commit()
    conn.close()

def save_prediction(user_id, predicted_score, available_hours, current_primary):
    """Сохраняет прогноз в историю"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute('''INSERT INTO prediction_history 
                 (user_id, date, predicted_score, available_hours_remaining, current_primary_score)
                 VALUES (?, ?, ?, ?, ?)''',
              (user_id, now, predicted_score, available_hours, current_primary))
    conn.commit()
    conn.close()
import sqlite3

conn = sqlite3.connect('fred_users.db')
c = conn.cursor()

# Проверяем существующие таблицы
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
rows = c.fetchall()
print("Существующие таблицы:", [row[0] for row in rows])

# Создаём таблицы для статистики, если их нет
c.execute('''CREATE TABLE IF NOT EXISTS user_stats (
    user_id TEXT PRIMARY KEY,
    current_primary_score INTEGER DEFAULT 0,
    target_primary_score INTEGER DEFAULT 17,
    hours_per_study_day REAL DEFAULT 2,
    hours_per_holiday REAL DEFAULT 8,
    other_subjects_count INTEGER DEFAULT 3
)''')

c.execute('''CREATE TABLE IF NOT EXISTS study_schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    date TEXT NOT NULL,
    hours_planned REAL DEFAULT 0,
    hours_actual REAL DEFAULT 0,
    completed BOOLEAN DEFAULT 0,
    UNIQUE(user_id, date)
)''')

c.execute('''CREATE TABLE IF NOT EXISTS prediction_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    date TEXT NOT NULL,
    predicted_score INTEGER,
    available_hours_remaining INTEGER,
    current_primary_score INTEGER
)''')

conn.commit()
conn.close()

print("Таблицы для статистики созданы/обновлены")
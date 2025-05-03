import sqlite3

# Подключаемся к базе
conn = sqlite3.connect("evacuation_points.db")
cursor = conn.cursor()

# Выбираем все данные из таблицы
cursor.execute("SELECT * FROM evacuation_points")
rows = cursor.fetchall()

# Выводим результаты
for row in rows:
    print(row)

conn.close()

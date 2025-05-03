import requests
import sqlite3
import time

# 🔹 Укажи свой API-ключ 2ГИС
API_KEY = "14510794-de25-4a43-94d1-bc1cc433aa54"
REGION_ID = 11822966929096719  # ID Мангистауской области

# 🔹 Фразы для поиска
SEARCH_QUERIES = [
    "Пункт сбора, эвакуации и временного размещения населения",
    "Эвакуационный пункт",
    "Пункт временного размещения",
    "Пункт эвакуации"
]

# 🔹 Подключение к базе данных
conn = sqlite3.connect("evacuation.db")
cursor = conn.cursor()

# 🔹 Создание таблицы, если её нет
cursor.execute("""
CREATE TABLE IF NOT EXISTS evacuation_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    address TEXT,
    lat REAL,
    lon REAL,
    link TEXT
)
""")
conn.commit()

# 🔹 Функция для запроса к 2ГИС API
def fetch_data(query):
    url = "https://catalog.api.2gis.com/3.0/items"
    params = {
        "q": query,
        "region_id": REGION_ID,
        "key": API_KEY,
        "fields": "items.point,items.address_name,items.name,items.links",
        "page_size": 50
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if "error" in data["meta"]:
        print(f"Ошибка API: {data['meta']['error']['message']}")
        return []
    
    return data.get("result", {}).get("items", [])

# 🔹 Сбор данных по всем запросам
for query in SEARCH_QUERIES:
    print(f"🔍 Поиск: {query}")
    results = fetch_data(query)
    
    for item in results:
        name = item.get("name", "Неизвестно")
        address = item.get("address_name", "Адрес не указан")
        lat = item.get("point", {}).get("lat", 0)
        lon = item.get("point", {}).get("lon", 0)
        link = item.get("links", [{}])[0].get("href", "Нет ссылки")
        
        # 🔹 Запись в базу данных
        cursor.execute(
            "INSERT INTO evacuation_points (name, address, lat, lon, link) VALUES (?, ?, ?, ?, ?)",
            (name, address, lat, lon, link)
        )
        conn.commit()
        print(f"✅ Добавлен: {name} ({address})")

    # 🔹 Пауза между запросами, чтобы не забанили API
    time.sleep(1)

print("🎯 Данные успешно загружены в базу `evacuation.db`!")
conn.close()

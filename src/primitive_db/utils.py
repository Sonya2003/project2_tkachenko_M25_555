import json
import os

def load_metadata(filepath):
    """Загружает данные из JSON-файла. Если файл не найден, возвращает пустой словарь"""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
def save_metadata(filepath, data):
    """Сохраняет переданные данные в JSON-файл"""
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

def load_table_data(table_name):
    """Загружает данные таблицы из соответствующего JSON-файла в директории data/"""
    filepath = f"data/{table_name}.json"
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_table_data(table_name, data):
    """Сохраняет данные таблицы в соответствующий JSON-файл в директории data/"""
    os.makedirs("data", exist_ok=True)
    filepath = f"data/{table_name}.json"
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


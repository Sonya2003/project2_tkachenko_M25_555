import os
from .utils import load_table_data, save_table_data
from ..decorators import handle_db_errors, confirm_action, log_time, create_cacher

select_cacher = create_cacher()

@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    """Выбирает записи из табличных данных с возможностью фильтрации"""
    cache_key = f"select_{len(table_data)}_{str(where_clause)}"
    def perform_select():
        if where_clause is None:
            return table_data
        filtered_data = []
        for record in table_data:
            match = True
            for key, value in where_clause.items():
                if record.get(key) != value:
                    match = False
                    break
            if match:
                filtered_data.append(record)
    
        return filtered_data
    return select_cacher(cache_key, perform_select)

@handle_db_errors
def update(table_data, set_clause, where_clause):
    """Обновляет записи в табличных данных"""
    updated_count = 0
    for record in table_data:
        match = True
        for key, value in where_clause.items():
            if record.get(key) != value:
                match = False
                break
        
        if match:
            for key, value in set_clause.items():
                record[key] = value
            updated_count += 1
    
    print(f"Обновлено записей: {updated_count}")
    return table_data

@handle_db_errors
@confirm_action("удаление данных")
def delete(table_data, where_clause):
    """Удаляет записи из табличных данных"""
    if where_clause is None:
        deleted_count = len(table_data)
        table_data.clear()
    else:
        initial_count = len(table_data)
        table_data = [record for record in table_data if not all(
            record.get(key) == value for key, value in where_clause.items()
        )]
        deleted_count = initial_count - len(table_data)
    
    print(f"Удалено записей: {deleted_count}")
    return table_data

@handle_db_errors
@log_time
def insert(metadata, table_name, values):
    """Добавляет новую запись в таблицу"""
    if 'tables' not in metadata or table_name not in metadata['tables']:
        print(f"Ошибка: Таблица '{table_name}' не существует")
        return None
    
    table_info = metadata['tables'][table_name]
    columns = table_info['columns']
    
    expected_values_count = len(columns) - 1 
    if len(values) != expected_values_count:
        print(f"Ошибка: Ожидается {expected_values_count} значений, получено {len(values)}")
        return None
    
    table_data = load_table_data(table_name)
    
    if table_data:
        max_id = max(record.get('id', 0) for record in table_data)
        new_id = max_id + 1
    else:
        new_id = 1
    
    new_record = {'id': new_id}
    validation_errors = []
    
    for i, (col_name, col_type) in enumerate(columns[1:], start=0): 
        value = values[i]
        
        try:
            if col_type == 'int':
                validated_value = int(value)
            elif col_type == 'str':
                validated_value = str(value)
            elif col_type == 'bool':
                if isinstance(value, bool):
                    validated_value = value
                elif isinstance(value, str):
                    if value.lower() in ('true', '1', 'yes', 'да'):
                        validated_value = True
                    elif value.lower() in ('false', '0', 'no', 'нет'):
                        validated_value = False
                    else:
                        validation_errors.append(f"Столбец '{col_name}': неверное булево значение '{value}'")
                        continue
                else:
                    validated_value = bool(value)
            else:
                validation_errors.append(f"Столбец '{col_name}': неизвестный тип '{col_type}'")
                continue
                
            new_record[col_name] = validated_value
            
        except (ValueError, TypeError) as e:
            validation_errors.append(f"Столбец '{col_name}': ожидается тип '{col_type}', получено '{value}'")
    
    if validation_errors:
        print("Ошибки валидации данных:")
        for error in validation_errors:
            print(f"  - {error}")
        return None
    
    table_data.append(new_record)
    
    save_table_data(table_name, table_data)
    
    print(f"Запись успешно добавлена в таблицу '{table_name}' с ID={new_id}")
    return table_data

@handle_db_errors
def create_table(metadata, table_name, columns):
    """Создает новую таблицу в метаданных"""
    if 'tables' not in metadata:
        metadata['tables'] = {}
    if table_name in metadata['tables']:
        print(f"Ошибка: Таблица '{table_name}' уже существует")
        return metadata
   
    columns_with_id = [('id', 'int')]
    allowed_types = ['int', 'str', 'bool']
    for col_name, col_type in columns:
        if col_type not in allowed_types:
            print(
                f"Ошибка: Недопустимый тип '{col_type}' для столбца '{col_name}'. "
                f"Разрешены: {allowed_types}"
            )
            return metadata
        columns_with_id.append((col_name, col_type))
    metadata['tables'][table_name] = {
        'columns': columns_with_id
    }
    print(f"Таблица '{table_name}' успешно создана")
    return metadata

@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    """Удаляет таблицу из метаданных"""
    if 'tables' not in metadata or table_name not in metadata['tables']:
        print(f"Ошибка: Таблица '{table_name}' не существует")
        return metadata
    del metadata['tables'][table_name]
    filepath = f"data/{table_name}.json"
    if os.path.exists(filepath):
        os.remove(filepath)
    print(f"Таблица '{table_name}' успешно удалена")
    return metadata

def list_tables(metadata):
    """Возвращает список всех таблиц"""
    if not isinstance(metadata, dict):
        return []
    
    tables = metadata.get('tables', {})
    if not isinstance(tables, dict):
        return []
    
    return list(tables.keys())

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

	
def drop_table(metadata, table_name):
    """Удаляет таблицу из метаданных"""
    if 'tables' not in metadata or table_name not in metadata['tables']:
        print(f"Ошибка: Таблица '{table_name}' не существует")
        return metadata
    del metadata['tables'][table_name]
    print(f"Таблица '{table_name}' успешно удалена")
    return metadata

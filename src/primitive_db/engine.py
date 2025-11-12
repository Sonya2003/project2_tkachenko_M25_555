import prompt
import shlex
from prettytable import PrettyTable
from .utils import load_metadata, save_metadata, load_table_data, save_table_data
from src.primitive_db.core import create_table, drop_table, list_tables, insert, select, update, delete

METADATA_FILE = "db_meta.json"

def parse_columns(column_args):
    """Парсит аргументы столбцов в формат [(name, type), ...]"""
    columns = []
    for arg in column_args:
        if ':' in arg:
            name, col_type = arg.split(':', 1)  # разделяем по первому двоеточию
            columns.append((name.strip(), col_type.strip()))
        else:
            print(f"Ошибка: Неверный формат столбца '{arg}'. Используйте name:type")
            return None
    return columns

def parse_where_condition(where_str):
    """
    Парсит условие WHERE в словарь
    Пример: "age = 28" -> {'age': 28}, "name = 'John'" -> {'name': 'John'}
    """
    if not where_str:
        return None
    
    try:
        parts = where_str.split('=', 1)
        if len(parts) != 2:
            print("Ошибка: Неверный формат условия WHERE. Используйте: поле = значение")
            return None
        
        field = parts[0].strip()
        value = parts[1].strip()
        
        if (value.startswith("'") and value.endswith("'")) or (value.startswith('"') and value.endswith('"')):
            value = value[1:-1]  
        else:
            try:
                value = int(value)
            except ValueError:
                if value.lower() in ('true', 'false'):
                    value = value.lower() == 'true'
        
        return {field: value}
    
    except Exception as e:
        print(f"Ошибка парсинга условия WHERE: {e}")
        return None

def parse_set_clause(set_str):
    """
    Парсит SET clause в словарь
    Пример: "name = 'John', age = 25" -> {'name': 'John', 'age': 25}
    """
    if not set_str:
        return None
    
    try:
        set_clause = {}
        assignments = set_str.split(',')
        
        for assignment in assignments:
            parts = assignment.split('=', 1)
            if len(parts) != 2:
                print(f"Ошибка: Неверный формат присваивания '{assignment}'")
                return None
            
            field = parts[0].strip()
            value = parts[1].strip()
            
            if (value.startswith("'") and value.endswith("'")) or (value.startswith('"') and value.endswith('"')):
                value = value[1:-1] 
            else:
                try:
                    value = int(value)
                except ValueError:
                    if value.lower() in ('true', 'false'):
                        value = value.lower() == 'true'
            
            set_clause[field] = value
        
        return set_clause
    
    except Exception as e:
        print(f"Ошибка парсинга SET clause: {e}")
        return None

def display_table_data(data, table_name):
    """Выводит данные таблицы в красивом формате с помощью PrettyTable"""
    if not data:
        print(f"Таблица '{table_name}' пуста")
        return
    
    table = PrettyTable()
    
    table.field_names = list(data[0].keys())
    
    for row in data:
        table.add_row([row[field] for field in table.field_names])
    
    print(f"\nТаблица: {table_name}")
    print(table)
    print(f"Всего записей: {len(data)}")

def run():
     """Главная функция с основным циклом программы"""
     print("Добро пожаловать в Primitive DB!")
     print("Для справки введите 'help'")

     while True:
         metadata = load_metadata(METADATA_FILE)

         try:
             user_input = input("db> ").strip()
         except (EOFError, KeyboardInterrupt):
             print("\nВыход из программы...")
             break
         if not user_input:
             continue

         args = shlex.split(user_input)
         command = args[0].lower()
         try:     
             if command == "exit": 
                 print("Выход из программы...")
                 break
             elif command == "help":
                 print_help()
             elif command == "list_tables":               
                 tables = list_tables(metadata)
                 if tables:
                     print("Таблицы в базе данных:")
                     for table in tables:
                         print(f"  - {table}")
                 else:
                      print("В базе данных нет таблиц")    

             elif command == "create_table":
                 if len(args) < 3:
                     print("Ошибка: Использование: create_table <имя_таблицы> <столбец1:тип> [столбец2:тип ...]")
                 else:
                     table_name = args[1]
                     columns = parse_columns(args[2:])
                     if columns:
                         metadata = create_table(metadata, table_name, columns)
                         save_metadata(METADATA_FILE, metadata)
             elif command == "drop_table":
                 if len(args) < 2:
                     print("Ошибка: Использование: drop_table <имя_таблицы>")
                 else:
                     table_name = args[1]
                     metadata = drop_table(metadata, table_name)
                     save_metadata(METADATA_FILE, metadata)


             elif command == "insert":
                if len(args) < 3:
                    print("Использование: insert <таблица> <значение> ...")
                else:
                    table_name = args[1]
                    values = args[2:]
                    table_data = load_table_data(table_name)
                    if table_data is not None:
                        result = insert(metadata, table_name, values)
                        if result:
                            save_table_data(table_name, result)
             elif command == "select":
                if len(args) < 2:
                    print("Использование: select <таблица> [WHERE условие]")
                else:
                    table_name = args[1]
                    where_clause = None
                    
                    if len(args) > 2:
                        if args[2].lower() == "where" and len(args) > 3:
                            where_str = ' '.join(args[3:])
                            where_clause = parse_where_condition(where_str)
                        else:
                            print("Ошибка в WHERE")
                            continue
                    
                    table_data = load_table_data(table_name)
                    if table_data is not None:
                        result = select(table_data, where_clause)
                        display_table_data(result, table_name) 
             elif command == "update":
                if len(args) < 4:
                    print("Использование: update <таблица> SET <поле=значение> [WHERE условие]")
                else:
                    table_name = args[1]
                    
                    set_index = -1
                    where_index = -1
                    
                    for i, arg in enumerate(args):
                        if arg.upper() == "SET":
                            set_index = i
                        elif arg.upper() == "WHERE":
                            where_index = i
                    
                    if set_index == -1:
                        print("Ошибка: нет SET")
                        continue
                    
                    set_str = ' '.join(args[set_index+1:where_index] if where_index != -1 else args[set_index+1:])
                    where_str = ' '.join(args[where_index+1:]) if where_index != -1 else None
                    
                    set_clause = parse_set_clause(set_str)
                    where_clause = parse_where_condition(where_str) if where_str else None
                    
                    if set_clause is None:
                        print("Ошибка в SET")
                        continue
                    
                    table_data = load_table_data(table_name)
                    if table_data is not None:
                        result = update(table_data, set_clause, where_clause)
                        if result is not None:
                            save_table_data(table_name, result)

             elif command == "delete":
                if len(args) < 2:
                    print("Использование: delete <таблица> [WHERE условие]")
                else:
                    table_name = args[1]
                    where_clause = None
                    
                    if len(args) > 2:
                        if args[2].lower() == "where" and len(args) > 3:
                            where_str = ' '.join(args[3:])
                            where_clause = parse_where_condition(where_str)
                        else:
                            print("Ошибка в WHERE")
                            continue
                    
                    table_data = load_table_data(table_name)
                    if table_data is not None:
                        result = delete(table_data, where_clause)
                        save_table_data(table_name, result)




             else:
                 print(f"Функции {command} нет. Попробуйте снова.")       
         except ValueError as e:
             print(f"Некорректное значение: {e}. Попробуйте снова.")

def print_help():
    """Prints the help message for the current mode."""
   
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")
 
    print("\n***CRUD операции***")
    print("insert <таблица> <значение> ...")
    print("select <таблица> [WHERE условие]")
    print("update <таблица> SET поле=значение [WHERE условие]")
    print("delete <таблица> [WHERE условие]")

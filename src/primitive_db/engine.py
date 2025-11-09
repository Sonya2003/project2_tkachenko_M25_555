import prompt
import shlex
from .utils import load_metadata, save_metadata
from .core import create_table, drop_table

METADATA_FILE = "db_meta.json"

def welcome():
    """Функция приветствия и игрового цикла"""
    print("Первая попытка запустить проект!")
    print("***")
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")

    while True:

        command = prompt.string('Введите команду: ').strip().lower() 
        if command == "exit":
            print("Выход из программы...")
            break   
        elif command == "help":
            print("<command> exit – выйти из программы")
            print("<command> help – справочная информация")
        else:
            print(f"Неизвестная комманда:{command}")

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

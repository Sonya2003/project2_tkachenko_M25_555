import time


def handle_db_errors(func):
    """
    Декоратор для обработки ошибок базы данных
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            print(f"Ошибка: Обращение к несуществующему объекту - {e}")
            return None
        except ValueError as e:
            print(f"Ошибка валидации данных: {e}")
            return None
        except FileNotFoundError as e:
            print(f"Ошибка: Файл не найден - {e}")
            return None
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
            return None
    return wrapper

def confirm_action(action_name):
    """
    Декоратор для подтверждения опасных операций
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            response = input(
                f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            )
            if response.lower() != 'y':
                print("Операция отменена")
                return None
            return func(*args, **kwargs)
        return wrapper
    return decorator

def log_time(func):
    """
    Декоратор для замера времени выполнения функции
    """
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        end_time = time.monotonic()
        execution_time = end_time - start_time
        print(f"Функция {func.__name__} выполнилась за {execution_time:.3f} секунд")
        return result
    return wrapper

def create_cacher():
    """
    Фабрика функций для кэширования
    """
    cache = {}
    
    def cache_result(key, value_func):
        if key in cache:
            print(f"Использован кэш для ключа: {key}")
            return cache[key]
        else:
            result = value_func()
            cache[key] = result
            print(f"Добавлено в кэш для ключа: {key}")
            return result
    
    return cache_result

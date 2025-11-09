# project2_tkachenko_M25_555
# Primitive Database

Простая база данных на Python для учебного проекта.

## Управление таблицами

### Доступные команды:

- `create_table <имя> <столбец1:тип> [столбец2:тип ...]` - создать таблицу
- `drop_table <имя>` - удалить таблицу  
- `help` - показать справку
- `exit` - выйти из программы

### Пример использования:

```bash
# Создание таблицы пользователей
create_table users name:str email:str age:int

# Создание таблицы продуктов
create_table products title:str price:int

# Удаление таблицы
drop_table products

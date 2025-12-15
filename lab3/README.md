# Лабораторная работа №3
## Использование SQLModel

**Автор:** Софья Шипенкова

**Предметная область:** Библиотека

---

## Описание

Реализация моделей базы данных с использованием SQLModel и запросов для основных процессов библиотеки.

---

## Установка и настройка

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка базы данных

Создайте файл `.env` в корне проекта:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/library_db
```

Или установите переменную окружения:

```bash
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/library_db
```

### 3. Создание базы данных

Создайте базу данных в PostgreSQL:

```sql
CREATE DATABASE library_db;
```

### 4. Инициализация базы данных

Запустите скрипт для создания таблиц и заполнения тестовыми данными:

```bash
python seed_data.py
```

---

## Структура проекта

```
lab3/
├── models.py          # Модели SQLModel
├── database.py        # Настройка подключения к БД
├── requests.py        # Запросы к базе данных
├── seed_data.py       # Заполнение тестовыми данными
├── example_usage.py   # Примеры использования
├── requirements.txt   # Зависимости
└── README.md          # Документация
```

---

## Модели

Все модели определены в файле `models.py`:

- `Author` - Авторы книг
- `Publisher` - Издательства
- `Book` - Книги
- `BookCopy` - Экземпляры книг
- `Reader` - Читатели
- `Librarian` - Библиотекари
- `Loan` - Выдачи книг
- `Reservation` - Резервации

---

## Основные запросы

Все запросы реализованы в файле `requests.py`:

### Работа с книгами
- `get_all_books()` - Получить все книги
- `get_book_by_id()` - Получить книгу по ID
- `get_book_by_isbn()` - Получить книгу по ISBN
- `search_books_by_title()` - Поиск книг по названию
- `get_books_by_author()` - Получить книги автора
- `get_available_books()` - Получить доступные книги

### Работа с читателями
- `get_reader_by_card_number()` - Получить читателя по номеру билета
- `get_active_loans_for_reader()` - Получить активные выдачи читателя
- `can_reader_borrow_more()` - Проверить лимит выдач

### Работа с выдачами
- `create_loan()` - Создать выдачу
- `return_loan()` - Вернуть книгу
- `get_overdue_loans()` - Получить просроченные выдачи
- `get_loans_by_reader()` - Получить все выдачи читателя

### Работа с резервациями
- `create_reservation()` - Создать резервацию
- `get_active_reservations_for_book()` - Получить активные резервации
- `fulfill_reservation()` - Выполнить резервацию

### Статистика
- `get_library_statistics()` - Общая статистика
- `get_most_popular_books()` - Популярные книги
- `get_most_active_readers()` - Активные читатели

---

## Примеры использования

Запустите файл с примерами:

```bash
python example_usage.py
```

Или используйте функции напрямую:

```python
from database import get_session
from requests import get_all_books, search_books_by_title

with next(get_session()) as session:
    # Поиск книг
    books = search_books_by_title(session, "война")
    for book in books:
        print(book.title)
    
    # Получение всех книг
    all_books = get_all_books(session)
    print(f"Всего книг: {len(all_books)}")
```

---

## Примечания

- Все модели используют SQLModel для работы с PostgreSQL
- Поддерживаются связи один-ко-многим и многие-ко-многим
- Реализованы основные бизнес-процессы библиотеки
- Включены проверки лимитов и доступности


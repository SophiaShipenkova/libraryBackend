# Лабораторная работа №4
## Использование FastAPI

**Автор:** Софья Шипенкова

**Предметная область:** Библиотека

---

## Описание

REST API для системы управления библиотекой, реализованное с использованием FastAPI и SQLModel.

---

## Установка и запуск

### Вариант 1: Запуск через Docker (рекомендуется)

Самый простой способ - использовать Docker Compose из корня проекта:

```bash
# Из корня проекта
docker compose up -d

# Инициализация базы данных
docker compose --profile init run --rm init_db
```

API будет доступно по адресу: http://localhost:8000

Подробная документация: [DOCKER.md](../../DOCKER.md)

### Вариант 2: Локальный запуск

#### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

#### 2. Настройка базы данных

Создайте файл `.env` в корне проекта:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/library_db
```

Убедитесь, что база данных создана и заполнена данными (используйте скрипт из lab3/seed_data.py).

#### 3. Запуск приложения

```bash
uvicorn main:app --reload
```

Приложение будет доступно по адресу: http://localhost:8000

### 4. Документация API

После запуска приложения доступна интерактивная документация:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Структура проекта

```
lab4/
├── main.py          # FastAPI приложение с endpoints
├── models.py        # Модели SQLModel
├── schemas.py       # Pydantic схемы для API
├── database.py      # Настройка подключения к БД
├── requirements.txt # Зависимости
└── README.md        # Документация
```

---

## API Endpoints

### Книги

- `GET /books` - Получить список всех книг
- `GET /books/{book_id}` - Получить книгу по ID
- `GET /books/search/{title_query}` - Поиск книг по названию
- `POST /books` - Создать новую книгу
- `GET /books/{book_id}/copies` - Получить все экземпляры книги
- `GET /books/{book_id}/available` - Получить доступные экземпляры

### Читатели

- `GET /readers` - Получить список всех читателей
- `GET /readers/{reader_id}` - Получить читателя по ID
- `GET /readers/card/{card_number}` - Получить читателя по номеру билета
- `POST /readers` - Создать нового читателя
- `GET /readers/{reader_id}/loans` - Получить все выдачи читателя
- `GET /readers/{reader_id}/active-loans` - Получить активные выдачи

### Выдачи

- `POST /loans` - Создать новую выдачу
- `POST /loans/{loan_id}/return` - Вернуть книгу
- `GET /loans/overdue` - Получить просроченные выдачи

### Резервации

- `POST /reservations` - Создать резервацию
- `GET /reservations/book/{book_id}` - Получить резервации для книги

### Статистика

- `GET /statistics` - Общая статистика библиотеки
- `GET /statistics/popular-books` - Популярные книги
- `GET /statistics/active-readers` - Активные читатели

---

## Примеры использования

### Создание читателя

```bash
curl -X POST "http://localhost:8000/readers" \
  -H "Content-Type: application/json" \
  -d '{
    "library_card_number": "CARD-003",
    "first_name": "Алексей",
    "last_name": "Сидоров",
    "email": "sidorov@example.com",
    "phone": "+7-999-333-44-55",
    "max_books": 5
  }'
```

### Поиск книг

```bash
curl "http://localhost:8000/books/search/война"
```

### Создание выдачи

```bash
curl -X POST "http://localhost:8000/loans" \
  -H "Content-Type: application/json" \
  -d '{
    "copy_id": 1,
    "reader_id": 1,
    "librarian_id": 1,
    "loan_days": 14
  }'
```

### Получение статистики

```bash
curl "http://localhost:8000/statistics"
```

---

## Особенности реализации

- Все endpoints используют Pydantic схемы для валидации
- Реализована обработка ошибок с понятными сообщениями
- Проверка бизнес-логики (лимиты, доступность, статусы)
- Поддержка пагинации для списков
- Автоматическая генерация документации OpenAPI

---

## Примечания

- Для работы приложения требуется запущенная база данных PostgreSQL
- Перед первым запуском необходимо заполнить базу данных тестовыми данными
- Все даты обрабатываются в формате ISO 8601 (YYYY-MM-DD)
- Денежные суммы передаются как строки или числа с двумя знаками после запятой


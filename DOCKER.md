# Запуск проекта с помощью Docker

**Автор:** Софья Шипенкова

---

## Требования

- Docker (версия 20.10+)
- Docker Compose (версия 2.0+)

---

## Быстрый старт

### 1. Запуск всех сервисов

```bash
# Запуск PostgreSQL и FastAPI
docker compose up -d

# Инициализация базы данных тестовыми данными (выполнить один раз)
docker compose --profile init run --rm init_db
```

### 2. Доступ к приложению

После запуска приложение будет доступно по адресам:

- **API:** http://localhost:8000
- **Документация Swagger:** http://localhost:8000/docs
- **Документация ReDoc:** http://localhost:8000/redoc
- **PostgreSQL:** localhost:5432

### 3. Остановка сервисов

```bash
docker compose down
```

Для полной очистки (включая данные БД):

```bash
docker compose down -v
```

---

## Структура Docker Compose

Проект включает следующие сервисы:

### postgres
- **Образ:** postgres:15-alpine
- **Порт:** 5432
- **База данных:** library_db
- **Пользователь:** postgres
- **Пароль:** postgres
- **Том данных:** postgres_data (сохраняется между перезапусками)

### api
- **Приложение:** FastAPI (Лабораторная работа №4)
- **Порт:** 8000
- **Автоперезагрузка:** включена (для разработки)
- **Зависит от:** postgres

### init_db
- **Профиль:** init (запускается отдельной командой)
- **Назначение:** заполнение базы данных тестовыми данными
- **Зависит от:** postgres

---

## Команды для работы

### Просмотр логов

```bash
# Все сервисы
docker compose logs -f

# Конкретный сервис
docker compose logs -f api
docker compose logs -f postgres
```

### Перезапуск сервиса

```bash
docker compose restart api
```

### Выполнение команд в контейнере

```bash
# В контейнере API
docker compose exec api bash

# В контейнере PostgreSQL
docker compose exec postgres psql -U postgres -d library_db
```

### Пересборка образов

```bash
# Пересборка всех образов
docker compose build

# Пересборка конкретного сервиса
docker compose build api
```

---

## Инициализация базы данных

База данных автоматически создаётся при первом запуске PostgreSQL. Для заполнения тестовыми данными:

```bash
# Запуск инициализации (профиль init)
docker compose --profile init run --rm init_db
```

Или можно выполнить вручную:

```bash
# Подключение к контейнеру lab3
docker compose run --rm -e DATABASE_URL=postgresql://postgres:postgres@postgres:5432/library_db init_db python seed_data.py
```

---

## Переменные окружения

Все переменные окружения можно переопределить через файл `.env` в корне проекта:

```env
# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=library_db

# API
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/library_db
```

---

## Разработка

Для разработки с автоперезагрузкой:

1. Запустите сервисы:
   ```bash
   docker compose up -d postgres
   docker compose up api
   ```

2. Изменения в коде будут автоматически применяться благодаря volume mount

3. Для применения изменений в зависимостях пересоберите образ:
   ```bash
   docker compose build api
   docker compose up api
   ```

---

## Устранение проблем

### Порт уже занят

Если порт 5432 или 8000 занят, измените маппинг портов в `docker compose.yml`:

```yaml
ports:
  - "5433:5432"  # Для PostgreSQL
  - "8001:8000"  # Для API
```

### Ошибка подключения к БД

Убедитесь, что PostgreSQL контейнер запущен и здоров:

```bash
docker compose ps
docker compose logs postgres
```

### Очистка и перезапуск

```bash
# Остановка и удаление контейнеров
docker compose down

# Удаление томов (удалит данные БД)
docker compose down -v

# Пересборка и запуск
docker compose build
docker compose up -d
```

---

## Production

Для production использования рекомендуется:

1. Изменить пароли в `docker compose.yml`
2. Отключить автоперезагрузку (убрать `--reload` из команды)
3. Использовать переменные окружения из файла `.env`
4. Настроить reverse proxy (nginx) для API
5. Настроить резервное копирование базы данных

---

## Примечания

- Данные PostgreSQL сохраняются в томе `postgres_data`
- При удалении тома все данные будут потеряны
- Для production используйте отдельные файлы docker compose для dev и prod окружений


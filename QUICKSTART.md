# Быстрый старт

**Автор:** Софья Шипенкова

---

## Запуск проекта за 3 шага

### 1. Запуск сервисов

```bash
docker compose up -d
```

Эта команда запустит:
- PostgreSQL базу данных на порту 5432
- FastAPI приложение на порту 8000

### 2. Инициализация базы данных

```bash
docker compose --profile init run --rm init_db
```

Эта команда заполнит базу данных тестовыми данными (книги, читатели, выдачи).

### 3. Открыть в браузере

- **API:** http://localhost:8000
- **Документация:** http://localhost:8000/docs

---

## Проверка работы

### Проверить статус сервисов

```bash
docker compose ps
```

### Просмотр логов

```bash
docker compose logs -f api
```

### Тестовый запрос

```bash
curl http://localhost:8000/statistics
```

---

## Остановка

```bash
docker compose down
```

Для полной очистки (включая данные БД):

```bash
docker compose down -v
```

---

## Что дальше?

- Подробная документация по Docker: [DOCKER.md](DOCKER.md)
- Описание API: http://localhost:8000/docs
- Общая документация: [README.md](README.md)


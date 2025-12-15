"""
Настройка подключения к базе данных

Автор: Софья Шипенкова
"""

from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
import os
from dotenv import load_dotenv

load_dotenv()

# Параметры подключения к PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/library_db"
)

# Создание движка базы данных
engine = create_engine(DATABASE_URL, echo=True)


def init_db():
    """Создание всех таблиц в базе данных"""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Генератор сессий для работы с базой данных"""
    with Session(engine) as session:
        yield session


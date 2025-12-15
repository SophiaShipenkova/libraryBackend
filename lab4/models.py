"""
Модели SQLModel для системы управления библиотекой

Автор: Софья Шипенкова
"""

from datetime import date, datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from decimal import Decimal


# Базовые модели для связей многие-ко-многим
class BookAuthorLink(SQLModel, table=True):
    """Связь между книгами и авторами (многие-ко-многим)"""
    __tablename__ = "book_authors"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    book_id: int = Field(foreign_key="books.id")
    author_id: int = Field(foreign_key="authors.id")
    created_at: datetime = Field(default_factory=datetime.now)


class Author(SQLModel, table=True):
    """Модель автора книги"""
    __tablename__ = "authors"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    middle_name: Optional[str] = Field(default=None, max_length=100)
    birth_date: Optional[date] = None
    biography: Optional[str] = None
    nationality: Optional[str] = Field(default=None, max_length=50)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Связи
    books: List["Book"] = Relationship(back_populates="authors", link_model=BookAuthorLink)


class Publisher(SQLModel, table=True):
    """Модель издательства"""
    __tablename__ = "publishers"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200, unique=True)
    country: Optional[str] = Field(default=None, max_length=100)
    city: Optional[str] = Field(default=None, max_length=100)
    website: Optional[str] = Field(default=None, max_length=255)
    contact_email: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Связи
    books: List["Book"] = Relationship(back_populates="publisher")


class Book(SQLModel, table=True):
    """Модель книги"""
    __tablename__ = "books"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    isbn: Optional[str] = Field(default=None, max_length=20, unique=True)
    title: str = Field(max_length=500)
    publisher_id: Optional[int] = Field(default=None, foreign_key="publishers.id")
    year: Optional[int] = None
    genre: Optional[str] = Field(default=None, max_length=100)
    pages: Optional[int] = None
    language: str = Field(default="ru", max_length=50)
    description: Optional[str] = None
    date_added: date = Field(default_factory=date.today)
    location: Optional[str] = Field(default=None, max_length=100)
    status: str = Field(default="available", max_length=20)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Связи
    publisher: Optional[Publisher] = Relationship(back_populates="books")
    authors: List[Author] = Relationship(back_populates="books", link_model=BookAuthorLink)
    copies: List["BookCopy"] = Relationship(back_populates="book")
    reservations: List["Reservation"] = Relationship(back_populates="book")


class BookCopy(SQLModel, table=True):
    """Модель экземпляра книги"""
    __tablename__ = "book_copies"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    book_id: int = Field(foreign_key="books.id")
    inventory_number: str = Field(max_length=50, unique=True)
    condition: str = Field(default="good", max_length=20)
    status: str = Field(default="in_library", max_length=20)
    acquisition_date: date
    price: Optional[Decimal] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Связи
    book: Book = Relationship(back_populates="copies")
    loans: List["Loan"] = Relationship(back_populates="copy")


class Reader(SQLModel, table=True):
    """Модель читателя"""
    __tablename__ = "readers"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    library_card_number: str = Field(max_length=50, unique=True)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    middle_name: Optional[str] = Field(default=None, max_length=100)
    email: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)
    address: Optional[str] = None
    registration_date: date = Field(default_factory=date.today)
    status: str = Field(default="active", max_length=20)
    max_books: int = Field(default=5)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Связи
    loans: List["Loan"] = Relationship(back_populates="reader")
    reservations: List["Reservation"] = Relationship(back_populates="reader")


class Librarian(SQLModel, table=True):
    """Модель библиотекаря"""
    __tablename__ = "librarians"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    employee_number: str = Field(max_length=50, unique=True)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    middle_name: Optional[str] = Field(default=None, max_length=100)
    position: str = Field(max_length=100)
    email: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)
    hire_date: date
    status: str = Field(default="working", max_length=20)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Связи
    loans: List["Loan"] = Relationship(back_populates="librarian")


class Loan(SQLModel, table=True):
    """Модель выдачи книги"""
    __tablename__ = "loans"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    copy_id: int = Field(foreign_key="book_copies.id")
    reader_id: int = Field(foreign_key="readers.id")
    librarian_id: int = Field(foreign_key="librarians.id")
    loan_date: date = Field(default_factory=date.today)
    due_date: date
    return_date: Optional[date] = None
    status: str = Field(default="active", max_length=20)
    fine_amount: Decimal = Field(default=Decimal("0.00"))
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Связи
    copy: BookCopy = Relationship(back_populates="loans")
    reader: Reader = Relationship(back_populates="loans")
    librarian: Librarian = Relationship(back_populates="loans")


class Reservation(SQLModel, table=True):
    """Модель резервации книги"""
    __tablename__ = "reservations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    book_id: int = Field(foreign_key="books.id")
    reader_id: int = Field(foreign_key="readers.id")
    reservation_date: date = Field(default_factory=date.today)
    expiry_date: date
    status: str = Field(default="active", max_length=20)
    notification_sent: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Связи
    book: Book = Relationship(back_populates="reservations")
    reader: Reader = Relationship(back_populates="reservations")


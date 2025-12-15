"""
Pydantic схемы для API запросов и ответов

Автор: Софья Шипенкова
"""

from datetime import date
from typing import Optional, List
from pydantic import BaseModel, EmailStr
from decimal import Decimal


# ==================== СХЕМЫ ДЛЯ КНИГ ====================

class BookBase(BaseModel):
    isbn: Optional[str] = None
    title: str
    publisher_id: Optional[int] = None
    year: Optional[int] = None
    genre: Optional[str] = None
    pages: Optional[int] = None
    language: str = "ru"
    description: Optional[str] = None
    location: Optional[str] = None


class BookCreate(BookBase):
    pass


class BookResponse(BookBase):
    id: int
    date_added: date
    status: str
    
    class Config:
        from_attributes = True


# ==================== СХЕМЫ ДЛЯ ЧИТАТЕЛЕЙ ====================

class ReaderBase(BaseModel):
    library_card_number: str
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    max_books: int = 5


class ReaderCreate(ReaderBase):
    pass


class ReaderResponse(ReaderBase):
    id: int
    registration_date: date
    status: str
    
    class Config:
        from_attributes = True


# ==================== СХЕМЫ ДЛЯ ВЫДАЧ ====================

class LoanCreate(BaseModel):
    copy_id: int
    reader_id: int
    librarian_id: int
    loan_days: int = 14


class LoanResponse(BaseModel):
    id: int
    copy_id: int
    reader_id: int
    librarian_id: int
    loan_date: date
    due_date: date
    return_date: Optional[date] = None
    status: str
    fine_amount: Decimal
    
    class Config:
        from_attributes = True


class LoanReturn(BaseModel):
    fine_amount: Decimal = Decimal("0.00")


# ==================== СХЕМЫ ДЛЯ РЕЗЕРВАЦИЙ ====================

class ReservationCreate(BaseModel):
    book_id: int
    reader_id: int
    expiry_days: int = 7


class UpdateReservation(BaseModel):
    book_id: Optional[int] = None
    reader_id: Optional[int] = None
    reservation_date: Optional[date] = None
    expiry_date: Optional[date] = None

class ReservationResponse(BaseModel):
    id: int
    book_id: int
    reader_id: int
    reservation_date: date
    expiry_date: date
    status: str
    
    class Config:
        from_attributes = True


# ==================== СХЕМЫ ДЛЯ СТАТИСТИКИ ====================

class LibraryStatistics(BaseModel):
    total_books: int
    total_copies: int
    available_copies: int
    on_loan_copies: int
    total_readers: int
    active_readers: int
    active_loans: int
    overdue_loans: int


class PopularBook(BaseModel):
    book_id: int
    title: str
    loan_count: int


class ActiveReader(BaseModel):
    reader_id: int
    name: str
    card_number: str
    loan_count: int


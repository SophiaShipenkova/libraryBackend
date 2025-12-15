"""
Запросы к базе данных для основных процессов библиотеки

Автор: Софья Шипенкова
"""

from datetime import date, datetime, timedelta
from typing import List, Optional
from sqlmodel import Session, select, and_, or_, func
from decimal import Decimal

from models import (
    Author, Book, BookCopy, BookAuthorLink, Publisher,
    Reader, Librarian, Loan, Reservation
)


# ==================== ЗАПРОСЫ ДЛЯ КНИГ ====================

def get_all_books(session: Session, skip: int = 0, limit: int = 100) -> List[Book]:
    """Получить все книги с пагинацией"""
    statement = select(Book).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def get_book_by_id(session: Session, book_id: int) -> Optional[Book]:
    """Получить книгу по ID"""
    return session.get(Book, book_id)


def get_book_by_isbn(session: Session, isbn: str) -> Optional[Book]:
    """Получить книгу по ISBN"""
    statement = select(Book).where(Book.isbn == isbn)
    return session.exec(statement).first()


def search_books_by_title(session: Session, title_query: str) -> List[Book]:
    """Поиск книг по названию (частичное совпадение)"""
    statement = select(Book).where(Book.title.ilike(f"%{title_query}%"))
    return list(session.exec(statement).all())


def get_books_by_author(session: Session, author_id: int) -> List[Book]:
    """Получить все книги определённого автора"""
    statement = (
        select(Book)
        .join(BookAuthorLink)
        .where(BookAuthorLink.author_id == author_id)
    )
    return list(session.exec(statement).all())


def get_available_books(session: Session) -> List[Book]:
    """Получить все доступные книги (есть хотя бы один доступный экземпляр)"""
    statement = (
        select(Book)
        .join(BookCopy)
        .where(
            and_(
                Book.status == "available",
                BookCopy.status == "in_library"
            )
        )
        .distinct()
    )
    return list(session.exec(statement).all())


# ==================== ЗАПРОСЫ ДЛЯ ЭКЗЕМПЛЯРОВ ====================

def get_available_copies_for_book(session: Session, book_id: int) -> List[BookCopy]:
    """Получить все доступные экземпляры определённой книги"""
    statement = (
        select(BookCopy)
        .where(
            and_(
                BookCopy.book_id == book_id,
                BookCopy.status == "in_library"
            )
        )
    )
    return list(session.exec(statement).all())


def get_copy_by_inventory_number(session: Session, inventory_number: str) -> Optional[BookCopy]:
    """Получить экземпляр по инвентарному номеру"""
    statement = select(BookCopy).where(BookCopy.inventory_number == inventory_number)
    return session.exec(statement).first()


# ==================== ЗАПРОСЫ ДЛЯ ЧИТАТЕЛЕЙ ====================

def get_reader_by_card_number(session: Session, card_number: str) -> Optional[Reader]:
    """Получить читателя по номеру читательского билета"""
    statement = select(Reader).where(Reader.library_card_number == card_number)
    return session.exec(statement).first()


def get_active_loans_for_reader(session: Session, reader_id: int) -> List[Loan]:
    """Получить все активные выдачи читателя"""
    statement = (
        select(Loan)
        .where(
            and_(
                Loan.reader_id == reader_id,
                Loan.status == "active"
            )
        )
    )
    return list(session.exec(statement).all())


def count_active_loans_for_reader(session: Session, reader_id: int) -> int:
    """Подсчитать количество активных выдач читателя"""
    statement = (
        select(func.count(Loan.id))
        .where(
            and_(
                Loan.reader_id == reader_id,
                Loan.status == "active"
            )
        )
    )
    return session.exec(statement).one()


def can_reader_borrow_more(session: Session, reader_id: int) -> bool:
    """Проверить, может ли читатель взять ещё книги (не превышен лимит)"""
    reader = session.get(Reader, reader_id)
    if not reader:
        return False
    
    active_count = count_active_loans_for_reader(session, reader_id)
    return active_count < reader.max_books


# ==================== ЗАПРОСЫ ДЛЯ ВЫДАЧ ====================

def create_loan(
    session: Session,
    copy_id: int,
    reader_id: int,
    librarian_id: int,
    loan_days: int = 14
) -> Optional[Loan]:
    """Создать новую выдачу книги"""
    # Проверка доступности экземпляра
    copy = session.get(BookCopy, copy_id)
    if not copy or copy.status != "in_library":
        return None
    
    # Проверка лимита читателя
    if not can_reader_borrow_more(session, reader_id):
        return None
    
    # Создание выдачи
    loan = Loan(
        copy_id=copy_id,
        reader_id=reader_id,
        librarian_id=librarian_id,
        loan_date=date.today(),
        due_date=date.today() + timedelta(days=loan_days),
        status="active"
    )
    
    # Обновление статуса экземпляра
    copy.status = "on_loan"
    
    session.add(loan)
    session.commit()
    session.refresh(loan)
    
    return loan


def return_loan(session: Session, loan_id: int, fine_amount: Decimal = Decimal("0.00")) -> bool:
    """Вернуть книгу (завершить выдачу)"""
    loan = session.get(Loan, loan_id)
    if not loan or loan.status != "active":
        return False
    
    # Обновление выдачи
    loan.return_date = date.today()
    loan.status = "returned"
    loan.fine_amount = fine_amount
    loan.updated_at = datetime.now()
    
    # Обновление статуса экземпляра
    copy = session.get(BookCopy, loan.copy_id)
    if copy:
        copy.status = "in_library"
        copy.updated_at = datetime.now()
    
    session.commit()
    return True


def get_overdue_loans(session: Session) -> List[Loan]:
    """Получить все просроченные выдачи"""
    today = date.today()
    statement = (
        select(Loan)
        .where(
            and_(
                Loan.status == "active",
                Loan.due_date < today
            )
        )
    )
    return list(session.exec(statement).all())


def get_loans_by_reader(session: Session, reader_id: int) -> List[Loan]:
    """Получить все выдачи читателя (включая возвращённые)"""
    statement = select(Loan).where(Loan.reader_id == reader_id)
    return list(session.exec(statement).all())


# ==================== ЗАПРОСЫ ДЛЯ РЕЗЕРВАЦИЙ ====================

def create_reservation(
    session: Session,
    book_id: int,
    reader_id: int,
    expiry_days: int = 7
) -> Optional[Reservation]:
    """Создать резервацию книги"""
    # Проверка наличия доступных экземпляров
    available_copies = get_available_copies_for_book(session, book_id)
    if available_copies:
        return None  # Книга доступна, резервация не нужна
    
    # Проверка существующей активной резервации
    statement = (
        select(Reservation)
        .where(
            and_(
                Reservation.book_id == book_id,
                Reservation.reader_id == reader_id,
                Reservation.status == "active"
            )
        )
    )
    existing = session.exec(statement).first()
    if existing:
        return existing  # Резервация уже существует
    
    # Создание резервации
    reservation = Reservation(
        book_id=book_id,
        reader_id=reader_id,
        reservation_date=date.today(),
        expiry_date=date.today() + timedelta(days=expiry_days),
        status="active"
    )
    
    session.add(reservation)
    session.commit()
    session.refresh(reservation)
    
    return reservation


def get_active_reservations_for_book(session: Session, book_id: int) -> List[Reservation]:
    """Получить все активные резервации для книги (очередь)"""
    statement = (
        select(Reservation)
        .where(
            and_(
                Reservation.book_id == book_id,
                Reservation.status == "active"
            )
        )
        .order_by(Reservation.reservation_date)
    )
    return list(session.exec(statement).all())


def fulfill_reservation(session: Session, reservation_id: int) -> bool:
    """Выполнить резервацию (книга стала доступна)"""
    reservation = session.get(Reservation, reservation_id)
    if not reservation or reservation.status != "active":
        return False
    
    reservation.status = "fulfilled"
    reservation.updated_at = datetime.now()
    
    session.commit()
    return True


def get_expired_reservations(session: Session) -> List[Reservation]:
    """Получить все истёкшие резервации"""
    today = date.today()
    statement = (
        select(Reservation)
        .where(
            and_(
                Reservation.status == "active",
                Reservation.expiry_date < today
            )
        )
    )
    return list(session.exec(statement).all())


# ==================== СТАТИСТИЧЕСКИЕ ЗАПРОСЫ ====================

def get_most_popular_books(session: Session, limit: int = 10) -> List[dict]:
    """Получить самые популярные книги (по количеству выдач)"""
    statement = (
        select(
            Book.id,
            Book.title,
            func.count(Loan.id).label("loan_count")
        )
        .join(BookCopy)
        .join(Loan)
        .group_by(Book.id, Book.title)
        .order_by(func.count(Loan.id).desc())
        .limit(limit)
    )
    results = session.exec(statement).all()
    return [
        {"book_id": r[0], "title": r[1], "loan_count": r[2]}
        for r in results
    ]


def get_most_active_readers(session: Session, limit: int = 10) -> List[dict]:
    """Получить самых активных читателей (по количеству выдач)"""
    statement = (
        select(
            Reader.id,
            Reader.first_name,
            Reader.last_name,
            Reader.library_card_number,
            func.count(Loan.id).label("loan_count")
        )
        .join(Loan)
        .group_by(Reader.id, Reader.first_name, Reader.last_name, Reader.library_card_number)
        .order_by(func.count(Loan.id).desc())
        .limit(limit)
    )
    results = session.exec(statement).all()
    return [
        {
            "reader_id": r[0],
            "name": f"{r[1]} {r[2]}",
            "card_number": r[3],
            "loan_count": r[4]
        }
        for r in results
    ]


def get_library_statistics(session: Session) -> dict:
    """Получить общую статистику библиотеки"""
    total_books = session.exec(select(func.count(Book.id))).one()
    total_copies = session.exec(select(func.count(BookCopy.id))).one()
    available_copies = session.exec(
        select(func.count(BookCopy.id)).where(BookCopy.status == "in_library")
    ).one()
    total_readers = session.exec(select(func.count(Reader.id))).one()
    active_readers = session.exec(
        select(func.count(Reader.id)).where(Reader.status == "active")
    ).one()
    active_loans = session.exec(
        select(func.count(Loan.id)).where(Loan.status == "active")
    ).one()
    overdue_loans = len(get_overdue_loans(session))
    
    return {
        "total_books": total_books,
        "total_copies": total_copies,
        "available_copies": available_copies,
        "on_loan_copies": total_copies - available_copies,
        "total_readers": total_readers,
        "active_readers": active_readers,
        "active_loans": active_loans,
        "overdue_loans": overdue_loans
    }



def delete_reservation(session: Session, pk: int):
    session.delete(session.exec(select(Reservation).where(Reservation.id == pk)))
    session.commit()

def update_reservation(session: Session, pk: int, payload: dict) -> Reservation:
    reservation = session.execute(select(Reservation).where(Reservation.id == pk))
    if not reservation:
        raise Exception('reservation not found')
    for key, val in payload.items():
        setattr(reservation, key, val)
    session.commit()
    session.refresh(reservation)
    return reservation
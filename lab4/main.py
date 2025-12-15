"""
FastAPI приложение для системы управления библиотекой

Автор: Софья Шипенкова
"""

from datetime import date, timedelta
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Session, select, and_, func
from decimal import Decimal

from database import get_session, init_db
from models import (
    Book, BookCopy, Reader, Librarian, Loan, Reservation,
    BookAuthorLink, Author
)
from schemas import (
    BookCreate, BookResponse, ReaderCreate, ReaderResponse,
    LoanCreate, LoanResponse, LoanReturn, ReservationCreate,
    ReservationResponse, LibraryStatistics, PopularBook, ActiveReader, UpdateReservation
)

app = FastAPI(
    title="Библиотечная система API",
    description="API для управления библиотекой",
    version="1.0.0"
)


@app.on_event("startup")
def on_startup():
    """Инициализация базы данных при запуске"""
    init_db()


# ==================== ENDPOINTS ДЛЯ КНИГ ====================

@app.get("/books", response_model=List[BookResponse])
def get_books(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """Получить список всех книг"""
    statement = select(Book).offset(skip).limit(limit)
    books = session.exec(statement).all()
    return list(books)


@app.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int, session: Session = Depends(get_session)):
    """Получить книгу по ID"""
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    return book


@app.get("/books/search/{title_query}", response_model=List[BookResponse])
def search_books(title_query: str, session: Session = Depends(get_session)):
    """Поиск книг по названию"""
    statement = select(Book).where(Book.title.ilike(f"%{title_query}%"))
    books = session.exec(statement).all()
    return list(books)


@app.post("/books", response_model=BookResponse, status_code=201)
def create_book(book: BookCreate, session: Session = Depends(get_session)):
    """Создать новую книгу"""
    db_book = Book(**book.dict())
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book


@app.get("/books/{book_id}/copies", response_model=List[dict])
def get_book_copies(book_id: int, session: Session = Depends(get_session)):
    """Получить все экземпляры книги"""
    statement = select(BookCopy).where(BookCopy.book_id == book_id)
    copies = session.exec(statement).all()
    return [
        {
            "id": copy.id,
            "inventory_number": copy.inventory_number,
            "condition": copy.condition,
            "status": copy.status
        }
        for copy in copies
    ]


@app.get("/books/{book_id}/available", response_model=List[dict])
def get_available_copies(book_id: int, session: Session = Depends(get_session)):
    """Получить доступные экземпляры книги"""
    statement = select(BookCopy).where(
        and_(
            BookCopy.book_id == book_id,
            BookCopy.status == "in_library"
        )
    )
    copies = session.exec(statement).all()
    return [
        {
            "id": copy.id,
            "inventory_number": copy.inventory_number,
            "condition": copy.condition
        }
        for copy in copies
    ]


# ==================== ENDPOINTS ДЛЯ ЧИТАТЕЛЕЙ ====================

@app.get("/readers", response_model=List[ReaderResponse])
def get_readers(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """Получить список всех читателей"""
    statement = select(Reader).offset(skip).limit(limit)
    readers = session.exec(statement).all()
    return list(readers)


@app.get("/readers/{reader_id}", response_model=ReaderResponse)
def get_reader(reader_id: int, session: Session = Depends(get_session)):
    """Получить читателя по ID"""
    reader = session.get(Reader, reader_id)
    if not reader:
        raise HTTPException(status_code=404, detail="Читатель не найден")
    return reader


@app.get("/readers/card/{card_number}", response_model=ReaderResponse)
def get_reader_by_card(card_number: str, session: Session = Depends(get_session)):
    """Получить читателя по номеру читательского билета"""
    statement = select(Reader).where(Reader.library_card_number == card_number)
    reader = session.exec(statement).first()
    if not reader:
        raise HTTPException(status_code=404, detail="Читатель не найден")
    return reader


@app.post("/readers", response_model=ReaderResponse, status_code=201)
def create_reader(reader: ReaderCreate, session: Session = Depends(get_session)):
    """Создать нового читателя"""
    # Проверка уникальности номера билета
    statement = select(Reader).where(Reader.library_card_number == reader.library_card_number)
    existing = session.exec(statement).first()
    if existing:
        raise HTTPException(status_code=400, detail="Читатель с таким номером билета уже существует")
    
    db_reader = Reader(**reader.dict())
    session.add(db_reader)
    session.commit()
    session.refresh(db_reader)
    return db_reader


@app.get("/readers/{reader_id}/loans", response_model=List[LoanResponse])
def get_reader_loans(reader_id: int, session: Session = Depends(get_session)):
    """Получить все выдачи читателя"""
    statement = select(Loan).where(Loan.reader_id == reader_id)
    loans = session.exec(statement).all()
    return list(loans)


@app.get("/readers/{reader_id}/active-loans", response_model=List[LoanResponse])
def get_reader_active_loans(reader_id: int, session: Session = Depends(get_session)):
    """Получить активные выдачи читателя"""
    statement = select(Loan).where(
        and_(
            Loan.reader_id == reader_id,
            Loan.status == "active"
        )
    )
    loans = session.exec(statement).all()
    return list(loans)


# ==================== ENDPOINTS ДЛЯ ВЫДАЧ ====================

@app.post("/loans", response_model=LoanResponse, status_code=201)
def create_loan(loan_data: LoanCreate, session: Session = Depends(get_session)):
    """Создать новую выдачу книги"""
    # Проверка доступности экземпляра
    copy = session.get(BookCopy, loan_data.copy_id)
    if not copy:
        raise HTTPException(status_code=404, detail="Экземпляр не найден")
    if copy.status != "in_library":
        raise HTTPException(status_code=400, detail="Экземпляр недоступен для выдачи")
    
    # Проверка читателя
    reader = session.get(Reader, loan_data.reader_id)
    if not reader:
        raise HTTPException(status_code=404, detail="Читатель не найден")
    if reader.status != "active":
        raise HTTPException(status_code=400, detail="Читатель не активен")
    
    # Проверка лимита
    active_loans_count = session.exec(
        select(func.count(Loan.id)).where(
            and_(
                Loan.reader_id == loan_data.reader_id,
                Loan.status == "active"
            )
        )
    ).one()
    
    if active_loans_count >= reader.max_books:
        raise HTTPException(
            status_code=400,
            detail=f"Превышен лимит выдач. Максимум: {reader.max_books}"
        )
    
    # Проверка библиотекаря
    librarian = session.get(Librarian, loan_data.librarian_id)
    if not librarian:
        raise HTTPException(status_code=404, detail="Библиотекарь не найден")
    
    # Создание выдачи
    loan = Loan(
        copy_id=loan_data.copy_id,
        reader_id=loan_data.reader_id,
        librarian_id=loan_data.librarian_id,
        loan_date=date.today(),
        due_date=date.today() + timedelta(days=loan_data.loan_days),
        status="active"
    )
    
    # Обновление статуса экземпляра
    copy.status = "on_loan"
    
    session.add(loan)
    session.commit()
    session.refresh(loan)
    
    return loan


@app.post("/loans/{loan_id}/return", response_model=LoanResponse)
def return_loan(
    loan_id: int,
    loan_return: LoanReturn,
    session: Session = Depends(get_session)
):
    """Вернуть книгу"""
    loan = session.get(Loan, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Выдача не найдена")
    if loan.status != "active":
        raise HTTPException(status_code=400, detail="Выдача уже закрыта")
    
    # Обновление выдачи
    loan.return_date = date.today()
    loan.status = "returned"
    loan.fine_amount = loan_return.fine_amount
    
    # Обновление статуса экземпляра
    copy = session.get(BookCopy, loan.copy_id)
    if copy:
        copy.status = "in_library"
    
    session.commit()
    session.refresh(loan)
    
    return loan


@app.get("/loans/overdue", response_model=List[LoanResponse])
def get_overdue_loans(session: Session = Depends(get_session)):
    """Получить все просроченные выдачи"""
    today = date.today()
    statement = select(Loan).where(
        and_(
            Loan.status == "active",
            Loan.due_date < today
        )
    )
    loans = session.exec(statement).all()
    return list(loans)


# ==================== ENDPOINTS ДЛЯ РЕЗЕРВАЦИЙ ====================

@app.post("/reservations", response_model=ReservationResponse, status_code=201)
def create_reservation(
    reservation_data: ReservationCreate,
    session: Session = Depends(get_session)
):
    """Создать резервацию книги"""
    # Проверка наличия доступных экземпляров
    available_copies = session.exec(
        select(BookCopy).where(
            and_(
                BookCopy.book_id == reservation_data.book_id,
                BookCopy.status == "in_library"
            )
        )
    ).all()
    
    if available_copies:
        raise HTTPException(
            status_code=400,
            detail="Книга доступна, резервация не требуется"
        )
    
    # Проверка существующей резервации
    existing = session.exec(
        select(Reservation).where(
            and_(
                Reservation.book_id == reservation_data.book_id,
                Reservation.reader_id == reservation_data.reader_id,
                Reservation.status == "active"
            )
        )
    ).first()
    
    if existing:
        return existing
    
    # Проверка читателя
    reader = session.get(Reader, reservation_data.reader_id)
    if not reader:
        raise HTTPException(status_code=404, detail="Читатель не найден")
    
    # Проверка книги
    book = session.get(Book, reservation_data.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    
    # Создание резервации
    reservation = Reservation(
        book_id=reservation_data.book_id,
        reader_id=reservation_data.reader_id,
        reservation_date=date.today(),
        expiry_date=date.today() + timedelta(days=reservation_data.expiry_days),
        status="active"
    )
    
    session.add(reservation)
    session.commit()
    session.refresh(reservation)
    
    return reservation


@app.get("/reservations/book/{book_id}", response_model=List[ReservationResponse])
def get_book_reservations(book_id: int, session: Session = Depends(get_session)):
    """Получить все активные резервации для книги"""
    statement = select(Reservation).where(
        and_(
            Reservation.book_id == book_id,
            Reservation.status == "active"
        )
    ).order_by(Reservation.reservation_date)
    reservations = session.exec(statement).all()
    return list(reservations)


@app.delete("/reservations/{pk}")
def delete_reservation(pk: int, session: Session = Depends(get_session)) -> None:
    session.delete(session.exec(select(Reservation).where(Reservation.id == pk)))
    session.commit()

@app.patch("/reservations")
def update_reservation(pk: int, payload: UpdateReservation, session: Session = Depends(get_session)) -> ReservationResponse:
    payload_data = payload.model_validate()
    reservation = session.execute(select(Reservation).where(Reservation.id == pk))
    if not reservation:
        raise Exception('reservation not found')
    for key, val in payload_data.items():
        setattr(reservation, key, val)
    session.commit()
    session.refresh(reservation)
    response = ReservationResponse(**vars(reservation))
    return response

# ==================== ENDPOINTS ДЛЯ СТАТИСТИКИ ====================

@app.get("/statistics", response_model=LibraryStatistics)
def get_statistics(session: Session = Depends(get_session)):
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
    
    today = date.today()
    overdue_loans = session.exec(
        select(func.count(Loan.id)).where(
            and_(
                Loan.status == "active",
                Loan.due_date < today
            )
        )
    ).one()
    
    return LibraryStatistics(
        total_books=total_books,
        total_copies=total_copies,
        available_copies=available_copies,
        on_loan_copies=total_copies - available_copies,
        total_readers=total_readers,
        active_readers=active_readers,
        active_loans=active_loans,
        overdue_loans=overdue_loans
    )


@app.get("/statistics/popular-books", response_model=List[PopularBook])
def get_popular_books(limit: int = 10, session: Session = Depends(get_session)):
    """Получить самые популярные книги"""
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
        PopularBook(book_id=r[0], title=r[1], loan_count=r[2])
        for r in results
    ]


@app.get("/statistics/active-readers", response_model=List[ActiveReader])
def get_active_readers(limit: int = 10, session: Session = Depends(get_session)):
    """Получить самых активных читателей"""
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
        ActiveReader(
            reader_id=r[0],
            name=f"{r[1]} {r[2]}",
            card_number=r[3],
            loan_count=r[4]
        )
        for r in results
    ]


@app.get("/")
def root():
    """Корневой endpoint"""
    return {
        "message": "Библиотечная система API",
        "author": "Софья Шипенкова",
        "version": "1.0.0",
        "docs": "/docs"
    }


"""
Скрипт для заполнения базы данных тестовыми данными

Автор: Софья Шипенкова
"""

from datetime import date, timedelta
from decimal import Decimal
from sqlmodel import Session
from database import engine, init_db
from models import (
    Author, Book, BookCopy, BookAuthorLink, Publisher,
    Reader, Librarian, Loan, Reservation
)


def seed_database():
    """Заполнение базы данных тестовыми данными"""
    init_db()
    
    with Session(engine) as session:
        # Создание издательств
        publisher1 = Publisher(
            name="Эксмо",
            country="Россия",
            city="Москва",
            website="https://eksmo.ru",
            contact_email="info@eksmo.ru"
        )
        publisher2 = Publisher(
            name="АСТ",
            country="Россия",
            city="Москва",
            website="https://ast.ru",
            contact_email="info@ast.ru"
        )
        session.add(publisher1)
        session.add(publisher2)
        session.commit()
        session.refresh(publisher1)
        session.refresh(publisher2)
        
        # Создание авторов
        author1 = Author(
            first_name="Лев",
            last_name="Толстой",
            middle_name="Николаевич",
            birth_date=date(1828, 9, 9),
            nationality="Русский",
            biography="Великий русский писатель, классик мировой литературы"
        )
        author2 = Author(
            first_name="Фёдор",
            last_name="Достоевский",
            middle_name="Михайлович",
            birth_date=date(1821, 11, 11),
            nationality="Русский",
            biography="Русский писатель, мыслитель, философ и публицист"
        )
        author3 = Author(
            first_name="Александр",
            last_name="Пушкин",
            middle_name="Сергеевич",
            birth_date=date(1799, 6, 6),
            nationality="Русский",
            biography="Русский поэт, драматург и прозаик"
        )
        session.add(author1)
        session.add(author2)
        session.add(author3)
        session.commit()
        session.refresh(author1)
        session.refresh(author2)
        session.refresh(author3)
        
        # Создание книг
        book1 = Book(
            isbn="978-5-699-12345-6",
            title="Война и мир",
            publisher_id=publisher1.id,
            year=1869,
            genre="Роман",
            pages=1274,
            language="ru",
            description="Эпический роман о войне 1812 года",
            location="Стеллаж 1, Полка 3"
        )
        book2 = Book(
            isbn="978-5-17-23456-7",
            title="Преступление и наказание",
            publisher_id=publisher2.id,
            year=1866,
            genre="Роман",
            pages=671,
            language="ru",
            description="Психологический роман о преступлении и его последствиях",
            location="Стеллаж 2, Полка 1"
        )
        book3 = Book(
            isbn="978-5-699-34567-8",
            title="Евгений Онегин",
            publisher_id=publisher1.id,
            year=1833,
            genre="Роман в стихах",
            pages=240,
            language="ru",
            description="Роман в стихах о жизни русского дворянства",
            location="Стеллаж 1, Полка 5"
        )
        session.add(book1)
        session.add(book2)
        session.add(book3)
        session.commit()
        session.refresh(book1)
        session.refresh(book2)
        session.refresh(book3)
        
        # Связь книг и авторов
        link1 = BookAuthorLink(book_id=book1.id, author_id=author1.id)
        link2 = BookAuthorLink(book_id=book2.id, author_id=author2.id)
        link3 = BookAuthorLink(book_id=book3.id, author_id=author3.id)
        session.add(link1)
        session.add(link2)
        session.add(link3)
        session.commit()
        
        # Создание экземпляров
        copy1 = BookCopy(
            book_id=book1.id,
            inventory_number="INV-001",
            condition="excellent",
            status="in_library",
            acquisition_date=date(2020, 1, 15),
            price=Decimal("1200.00")
        )
        copy2 = BookCopy(
            book_id=book1.id,
            inventory_number="INV-002",
            condition="good",
            status="in_library",
            acquisition_date=date(2021, 3, 20),
            price=Decimal("1200.00")
        )
        copy3 = BookCopy(
            book_id=book2.id,
            inventory_number="INV-003",
            condition="excellent",
            status="in_library",
            acquisition_date=date(2020, 5, 10),
            price=Decimal("850.00")
        )
        copy4 = BookCopy(
            book_id=book3.id,
            inventory_number="INV-004",
            condition="good",
            status="in_library",
            acquisition_date=date(2019, 12, 5),
            price=Decimal("450.00")
        )
        session.add(copy1)
        session.add(copy2)
        session.add(copy3)
        session.add(copy4)
        session.commit()
        session.refresh(copy1)
        session.refresh(copy2)
        session.refresh(copy3)
        session.refresh(copy4)
        
        # Создание библиотекарей
        librarian1 = Librarian(
            employee_number="EMP-001",
            first_name="Мария",
            last_name="Иванова",
            middle_name="Петровна",
            position="Главный библиотекарь",
            email="ivanova@library.ru",
            phone="+7-495-123-45-67",
            hire_date=date(2015, 1, 10)
        )
        librarian2 = Librarian(
            employee_number="EMP-002",
            first_name="Анна",
            last_name="Смирнова",
            middle_name="Владимировна",
            position="Библиотекарь",
            email="smirnova@library.ru",
            phone="+7-495-123-45-68",
            hire_date=date(2018, 6, 1)
        )
        session.add(librarian1)
        session.add(librarian2)
        session.commit()
        session.refresh(librarian1)
        session.refresh(librarian2)
        
        # Создание читателей
        reader1 = Reader(
            library_card_number="CARD-001",
            first_name="Иван",
            last_name="Петров",
            middle_name="Сергеевич",
            email="petrov@example.com",
            phone="+7-999-111-22-33",
            address="г. Москва, ул. Ленина, д. 1, кв. 10",
            max_books=5
        )
        reader2 = Reader(
            library_card_number="CARD-002",
            first_name="Елена",
            last_name="Козлова",
            middle_name="Александровна",
            email="kozlova@example.com",
            phone="+7-999-222-33-44",
            address="г. Москва, ул. Пушкина, д. 5, кв. 20",
            max_books=3
        )
        session.add(reader1)
        session.add(reader2)
        session.commit()
        session.refresh(reader1)
        session.refresh(reader2)
        
        # Создание выдач
        loan1 = Loan(
            copy_id=copy1.id,
            reader_id=reader1.id,
            librarian_id=librarian1.id,
            loan_date=date.today() - timedelta(days=5),
            due_date=date.today() + timedelta(days=9),
            status="active"
        )
        loan2 = Loan(
            copy_id=copy3.id,
            reader_id=reader2.id,
            librarian_id=librarian2.id,
            loan_date=date.today() - timedelta(days=10),
            due_date=date.today() - timedelta(days=3),  # Просрочена
            status="active"
        )
        # Возвращённая выдача
        loan3 = Loan(
            copy_id=copy4.id,
            reader_id=reader1.id,
            librarian_id=librarian1.id,
            loan_date=date.today() - timedelta(days=20),
            due_date=date.today() - timedelta(days=6),
            return_date=date.today() - timedelta(days=5),
            status="returned"
        )
        session.add(loan1)
        session.add(loan2)
        session.add(loan3)
        session.commit()
        
        # Обновление статусов экземпляров
        copy1.status = "on_loan"
        copy3.status = "on_loan"
        session.commit()
        
        # Создание резервации
        reservation1 = Reservation(
            book_id=book1.id,
            reader_id=reader2.id,
            reservation_date=date.today() - timedelta(days=2),
            expiry_date=date.today() + timedelta(days=5),
            status="active"
        )
        session.add(reservation1)
        session.commit()
        
        print("База данных успешно заполнена тестовыми данными!")


if __name__ == "__main__":
    seed_database()


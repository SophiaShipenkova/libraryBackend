"""
Примеры использования запросов к базе данных

Автор: Софья Шипенкова
"""

from database import get_session
from requests import (
    get_all_books, get_book_by_isbn, search_books_by_title,
    get_available_books, get_reader_by_card_number,
    get_active_loans_for_reader, create_loan, return_loan,
    get_overdue_loans, create_reservation, get_library_statistics,
    get_most_popular_books, get_most_active_readers
)


def example_search_books():
    """Пример поиска книг"""
    print("=== Поиск книг ===")
    with next(get_session()) as session:
        # Поиск по названию
        books = search_books_by_title(session, "война")
        print(f"Найдено книг по запросу 'война': {len(books)}")
        for book in books:
            print(f"  - {book.title} ({book.year})")
        
        # Поиск по ISBN
        book = get_book_by_isbn(session, "978-5-699-12345-6")
        if book:
            print(f"\nКнига по ISBN: {book.title}")
        
        # Получение доступных книг
        available = get_available_books(session)
        print(f"\nДоступных книг: {len(available)}")


def example_reader_operations():
    """Пример работы с читателями"""
    print("\n=== Работа с читателями ===")
    with next(get_session()) as session:
        # Получение читателя
        reader = get_reader_by_card_number(session, "CARD-001")
        if reader:
            print(f"Читатель: {reader.first_name} {reader.last_name}")
            print(f"Номер билета: {reader.library_card_number}")
            
            # Активные выдачи
            loans = get_active_loans_for_reader(session, reader.id)
            print(f"Активных выдач: {len(loans)}")
            for loan in loans:
                print(f"  - Выдача #{loan.id}, срок возврата: {loan.due_date}")


def example_loan_operations():
    """Пример работы с выдачами"""
    print("\n=== Работа с выдачами ===")
    with next(get_session()) as session:
        # Просроченные выдачи
        overdue = get_overdue_loans(session)
        print(f"Просроченных выдач: {len(overdue)}")
        for loan in overdue:
            print(f"  - Выдача #{loan.id}, просрочено на {loan.due_date}")


def example_reservation_operations():
    """Пример работы с резервациями"""
    print("\n=== Работа с резервациями ===")
    with next(get_session()) as session:
        from models import Book, Reader
        book = session.exec(
            "SELECT * FROM books WHERE title LIKE '%Война%'"
        ).first()
        if book:
            from requests import get_active_reservations_for_book
            reservations = get_active_reservations_for_book(session, book.id)
            print(f"Активных резерваций для книги '{book.title}': {len(reservations)}")


def example_statistics():
    """Пример получения статистики"""
    print("\n=== Статистика библиотеки ===")
    with next(get_session()) as session:
        stats = get_library_statistics(session)
        print(f"Всего книг: {stats['total_books']}")
        print(f"Всего экземпляров: {stats['total_copies']}")
        print(f"Доступно экземпляров: {stats['available_copies']}")
        print(f"На руках: {stats['on_loan_copies']}")
        print(f"Всего читателей: {stats['total_readers']}")
        print(f"Активных читателей: {stats['active_readers']}")
        print(f"Активных выдач: {stats['active_loans']}")
        print(f"Просроченных выдач: {stats['overdue_loans']}")
        
        # Популярные книги
        print("\n=== Самые популярные книги ===")
        popular = get_most_popular_books(session, limit=5)
        for item in popular:
            print(f"  - {item['title']}: {item['loan_count']} выдач")
        
        # Активные читатели
        print("\n=== Самые активные читатели ===")
        active = get_most_active_readers(session, limit=5)
        for item in active:
            print(f"  - {item['name']} ({item['card_number']}): {item['loan_count']} выдач")


if __name__ == "__main__":
    print("Примеры использования запросов к базе данных библиотеки\n")
    example_search_books()
    example_reader_operations()
    example_loan_operations()
    example_reservation_operations()
    example_statistics()


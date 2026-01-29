import datetime

class Book:
    """도서 정보를 저장하는 클래스"""
    def __init__(self, title, author, isbn):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.is_borrowed = False
        self.added_date = datetime.date.today()

    def __repr__(self):
        return f"Book({self.title}, {self.author})"

class Library:
    """도서관 운영 로직을 담은 클래스"""
    def __init__(self):
        self.books = []

    def add_book(self, title, author, isbn):
        new_book = Book(title, author, isbn)
        self.books.append(new_book)
        return f"도서 추가 완료: {title}"

    def borrow_book(self, isbn):
        for book in self.books:
            if book.isbn == isbn:
                if not book.is_borrowed:
                    book.is_borrowed = True
                    return f"'{book.title}' 대출되었습니다."
                return "이미 대출 중인 도서입니다."
        return "해당 ISBN의 도서를 찾을 수 없습니다."

    def return_book(self, isbn):
        for book in self.books:
            if book.isbn == isbn:
                book.is_borrowed = False
                return f"'{book.title}' 반납되었습니다."
        return "반납할 도서 정보를 확인해주세요."

    def search_by_author(self, author_name):
        """특정 작가의 도서 목록 필터링"""
        return [book for book in self.books if author_name.lower() in book.author.lower()]

# 실행 예시
if __name__ == "__main__":
    my_library = Library()
    my_library.add_book("Clean Code", "Robert C. Martin", "978-0132350884")
    my_library.add_book("The Pragmatic Programmer", "Andrew Hunt", "978-0201616224")

    print(my_library.borrow_book("978-0132350884"))
    print(f"검색 결과: {my_library.search_by_author('Robert')}")
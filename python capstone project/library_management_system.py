from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


# ---------------------------------------------------------------------------
# Custom Exception (Exception Handling)
# ---------------------------------------------------------------------------
class LibraryError(Exception):
    """Custom exception raised for invalid library operations."""


# ---------------------------------------------------------------------------
# Book Class (Class, Encapsulation, Dunder Methods)
# ---------------------------------------------------------------------------
class Book:
    """Represents a book in the campus library."""

    VALID_CATEGORIES: Set[str] = {
        "Computer Science",
        "Mathematics",
        "Physics",
        "Electronics",
        "Literature",
        "General",
    }

    def __init__(
        self,
        book_id: str,
        title: str,
        author: str,
        category: str = "General",
        total_copies: int = 1,
        available_copies: Optional[int] = None,
    ) -> None:
        if total_copies < 1:
            raise LibraryError("Total copies must be at least 1.")

        self.book_id: str = book_id.strip().upper()
        self.title: str = title.strip()
        self.author: str = author.strip()
        self.category: str = (
            category if category in self.VALID_CATEGORIES else "General"
        )
        self.__total_copies: int = total_copies
        self.__available_copies: int = (
            total_copies if available_copies is None else available_copies
        )

    @property
    def total_copies(self) -> int:
        return self.__total_copies

    @property
    def available_copies(self) -> int:
        return self.__available_copies

    def is_available(self) -> bool:
        return self.__available_copies > 0

    def borrow_copy(self) -> None:
        if not self.is_available():
            raise LibraryError(f"'{self.title}' has no available copies.")
        self.__available_copies -= 1

    def return_copy(self) -> None:
        if self.__available_copies >= self.__total_copies:
            raise LibraryError(
                f"All copies of '{self.title}' are already in the library."
            )
        self.__available_copies += 1

    def to_dict(self) -> Dict[str, object]:
        return {
            "book_id": self.book_id,
            "title": self.title,
            "author": self.author,
            "category": self.category,
            "total_copies": self.__total_copies,
            "available_copies": self.__available_copies,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> Book:
        return cls(
            book_id=str(data["book_id"]),
            title=str(data["title"]),
            author=str(data["author"]),
            category=str(data.get("category", "General")),
            total_copies=int(data["total_copies"]),
            available_copies=int(data["available_copies"]),
        )

    def __str__(self) -> str:
        return (
            f"[{self.book_id}] {self.title} by {self.author} "
            f"({self.category}) | Available: {self.__available_copies}/{self.__total_copies}"
        )


# ---------------------------------------------------------------------------
# Member Hierarchy (Inheritance, Encapsulation, Polymorphism)
# ---------------------------------------------------------------------------
class LibraryMember:
    """Base class for all library members."""

    BORROW_LIMIT: int = 2
    LOAN_DAYS: int = 7
    DAILY_FINE: float = 10.0

    def __init__(
        self,
        member_id: str,
        name: str,
        department: str,
        borrowed_records: Optional[Dict[str, str]] = None,
        fine_balance: float = 0.0,
    ) -> None:
        self.member_id: str = member_id.strip().upper()
        self.name: str = name.strip()
        self.department: str = department.strip()
        # Maps book_id -> ISO due date string (YYYY-MM-DD)
        self.__borrowed_records: Dict[str, str] = (
            dict(borrowed_records) if borrowed_records else {}
        )
        self.__fine_balance: float = float(fine_balance)

    @property
    def borrowed_records(self) -> Dict[str, str]:
        """Returns a safe copy of borrowed book records."""
        return dict(self.__borrowed_records)

    @property
    def fine_balance(self) -> float:
        return self.__fine_balance

    def get_role(self) -> str:
        return "General Member"

    def get_borrow_limit(self) -> int:
        return self.BORROW_LIMIT

    def get_loan_days(self) -> int:
        return self.LOAN_DAYS

    def calculate_fine(self, overdue_days: int) -> float:
        if overdue_days <= 0:
            return 0.0
        return overdue_days * self.DAILY_FINE

    def can_borrow(self) -> bool:
        return len(self.__borrowed_records) < self.get_borrow_limit()

    def record_borrow(self, book_id: str, borrow_date: Optional[date] = None) -> date:
        if not self.can_borrow():
            raise LibraryError(
                f"{self.name} has reached the borrow limit ({self.get_borrow_limit()} books)."
            )
        if book_id in self.__borrowed_records:
            raise LibraryError(f"{self.name} has already borrowed book {book_id}.")

        start = borrow_date or date.today()
        due_date = start + timedelta(days=self.get_loan_days())
        self.__borrowed_records[book_id] = due_date.isoformat()
        return due_date

    def record_return(
        self, book_id: str, return_date: Optional[date] = None
    ) -> Tuple[int, float]:
        if book_id not in self.__borrowed_records:
            raise LibraryError(f"{self.name} has not borrowed book {book_id}.")

        due_date = date.fromisoformat(self.__borrowed_records.pop(book_id))
        actual_return = return_date or date.today()
        overdue_days = max(0, (actual_return - due_date).days)
        fine = self.calculate_fine(overdue_days)
        self.__fine_balance += fine
        return overdue_days, fine

    def pay_fine(self, amount: float) -> float:
        if amount <= 0:
            raise LibraryError("Payment amount must be positive.")
        if amount > self.__fine_balance:
            raise LibraryError(
                f"Payment (Rs. {amount:.2f}) exceeds pending fine (Rs. {self.__fine_balance:.2f})."
            )
        self.__fine_balance -= amount
        return self.__fine_balance

    def to_dict(self) -> Dict[str, object]:
        return {
            "role": self.__class__.__name__,
            "member_id": self.member_id,
            "name": self.name,
            "department": self.department,
            "borrowed_records": self.__borrowed_records,
            "fine_balance": self.__fine_balance,
        }

    def __len__(self) -> int:
        return len(self.__borrowed_records)

    def __str__(self) -> str:
        return (
            f"[{self.member_id}] {self.name} ({self.get_role()}, {self.department}) | "
            f"Borrowed: {len(self)}/{self.get_borrow_limit()} | "
            f"Fine: Rs. {self.__fine_balance:.2f}"
        )


class StudentMember(LibraryMember):
    """Subclass representing a B.Tech / university student."""

    BORROW_LIMIT = 3
    LOAN_DAYS = 14
    DAILY_FINE = 5.0

    def get_role(self) -> str:
        return "Student"


class FacultyMember(LibraryMember):
    """Subclass representing faculty with extended limits and lower fine rate."""

    BORROW_LIMIT = 6
    LOAN_DAYS = 30
    DAILY_FINE = 2.0

    def get_role(self) -> str:
        return "Faculty"


# ---------------------------------------------------------------------------
# Library Controller Class (Composition, File I/O, Search & Reporting)
# ---------------------------------------------------------------------------
class Library:
    """Manages books, members, transactions, and JSON persistence."""

    def __init__(self, data_file: str = "library_data.json") -> None:
        self.data_path: Path = Path(data_file)
        self.books: Dict[str, Book] = {}
        self.members: Dict[str, LibraryMember] = {}
        self.load_data()

    # -- Book Management ----------------------------------------------------
    def add_book(self, book: Book) -> None:
        if book.book_id in self.books:
            raise LibraryError(f"Book ID '{book.book_id}' already exists.")
        self.books[book.book_id] = book
        self.save_data()

    def search_books(self, keyword: str) -> List[Book]:
        query = keyword.strip().lower()
        return [
            book
            for book in self.books.values()
            if query in book.title.lower()
            or query in book.author.lower()
            or query in book.category.lower()
            or query == book.book_id.lower()
        ]

    # -- Member Management --------------------------------------------------
    def register_member(self, member: LibraryMember) -> None:
        if member.member_id in self.members:
            raise LibraryError(f"Member ID '{member.member_id}' already exists.")
        self.members[member.member_id] = member
        self.save_data()

    # -- Borrow / Return Workflows ------------------------------------------
    def issue_book(
        self, member_id: str, book_id: str, borrow_date: Optional[date] = None
    ) -> date:
        m_id = member_id.strip().upper()
        b_id = book_id.strip().upper()

        if m_id not in self.members:
            raise LibraryError(f"Member '{m_id}' not found.")
        if b_id not in self.books:
            raise LibraryError(f"Book '{b_id}' not found.")

        member = self.members[m_id]
        book = self.books[b_id]

        book.borrow_copy()
        try:
            due_date = member.record_borrow(b_id, borrow_date=borrow_date)
        except LibraryError:
            # Roll back book availability if member borrow fails
            book.return_copy()
            raise

        self.save_data()
        return due_date

    def return_book(
        self, member_id: str, book_id: str, return_date: Optional[date] = None
    ) -> Tuple[int, float]:
        m_id = member_id.strip().upper()
        b_id = book_id.strip().upper()

        if m_id not in self.members:
            raise LibraryError(f"Member '{m_id}' not found.") 
        if b_id not in self.books:
            raise LibraryError(f"Book '{b_id}' not found.")

        member = self.members[m_id]
        book = self.books[b_id]

        overdue_days, fine = member.record_return(b_id, return_date=return_date)
        book.return_copy()
        self.save_data()
        return overdue_days, fine

    # -- Summary Statistics -------------------------------------------------
    def get_summary(self) -> Dict[str, object]:
        total_titles = len(self.books)
        total_copies = sum(b.total_copies for b in self.books.values())
        available_copies = sum(b.available_copies for b in self.books.values())
        issued_copies = total_copies - available_copies
        total_fines = sum(m.fine_balance for m in self.members.values())
        return {
            "total_titles": total_titles,
            "total_copies": total_copies,
            "available_copies": available_copies,
            "issued_copies": issued_copies,
            "total_members": len(self.members),
            "pending_fines": total_fines,
        }

    # -- File Handling (JSON Persistence) -----------------------------------
    def save_data(self) -> None:
        payload = {
            "books": [book.to_dict() for book in self.books.values()],
            "members": [member.to_dict() for member in self.members.values()],
        }
        with self.data_path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    def load_data(self) -> None:
        if not self.data_path.exists():
            self._seed_sample_data()
            return

        try:
            with self.data_path.open("r", encoding="utf-8") as f:
                payload = json.load(f)
        except (json.JSONDecodeError, OSError):
            self._seed_sample_data()
            return

        self.books = {
            b["book_id"]: Book.from_dict(b) for b in payload.get("books", [])
        }
        role_map = {
            "StudentMember": StudentMember,
            "FacultyMember": FacultyMember,
            "LibraryMember": LibraryMember,
        }
        self.members = {}
        for m in payload.get("members", []):
            cls = role_map.get(m.get("role", "LibraryMember"), LibraryMember)
            member = cls(
                member_id=str(m["member_id"]),
                name=str(m["name"]),
                department=str(m["department"]),
                borrowed_records=m.get("borrowed_records", {}),
                fine_balance=float(m.get("fine_balance", 0.0)),
            )
            self.members[member.member_id] = member

    def _seed_sample_data(self) -> None:
        sample_books = [
            Book("B101", "Python Crash Course", "Eric Matthes", "Computer Science", 3),
            Book("B102", "Clean Code", "Robert C. Martin", "Computer Science", 2),
            Book("B103", "Higher Engineering Mathematics", "B.S. Grewal", "Mathematics", 4),
            Book("B104", "Concepts of Physics", "H.C. Verma", "Physics", 2),
        ]
        sample_members = [
            StudentMember("S101", "Aarav Sharma", "CSE"),
            StudentMember("S102", "Priya Nair", "ECE"),
            FacultyMember("F201", "Dr. Rajesh Verma", "CSE"),
        ]
        for book in sample_books:
            self.books[book.book_id] = book
        for member in sample_members:
            self.members[member.member_id] = member
        self.save_data()


# ---------------------------------------------------------------------------
# Interactive CLI & Self-Verification Demo
# ---------------------------------------------------------------------------
def print_menu() -> None:
    print("\n=== Smart Campus Library Management System ===")
    print("1. View All Books")
    print("2. Search Books")
    print("3. Add New Book")
    print("4. View All Members")
    print("5. Register Member (Student / Faculty)")
    print("6. Issue Book")
    print("7. Return Book")
    print("8. Pay Fine")
    print("9. Library Summary")
    print("0. Exit")


def run_cli(library: Library) -> None:
    while True:
        print_menu()
        choice = input("Enter choice (0-9): ").strip()

        try:
            if choice == "1":
                if not library.books:
                    print("No books in catalog.")
                for book in library.books.values():
                    print(" ", book)

            elif choice == "2":
                kw = input("Enter title, author, category, or ID: ")
                matches = library.search_books(kw)
                if not matches:
                    print("No matching books found.")
                for book in matches:
                    print(" ", book)

            elif choice == "3":
                b_id = input("Book ID (e.g., B105): ")
                title = input("Title: ")
                author = input("Author: ")
                category = input(f"Category {sorted(Book.VALID_CATEGORIES)}: ")
                copies = int(input("Total copies: "))
                library.add_book(Book(b_id, title, author, category, copies))
                print("Book added successfully.")

            elif choice == "4":
                for member in library.members.values():
                    print(" ", member)

            elif choice == "5":
                role = input("Role (student/faculty): ").strip().lower()
                m_id = input("Member ID (e.g., S103): ")
                name = input("Full Name: ")
                dept = input("Department (e.g., CSE): ")
                if role == "student":
                    library.register_member(StudentMember(m_id, name, dept))
                elif role == "faculty":
                    library.register_member(FacultyMember(m_id, name, dept))
                else:
                    raise LibraryError("Role must be 'student' or 'faculty'.")
                print("Member registered successfully.")

            elif choice == "6":
                m_id = input("Member ID: ")
                b_id = input("Book ID: ")
                due = library.issue_book(m_id, b_id)
                print(f"Book issued! Due date: {due.isoformat()}")

            elif choice == "7":
                m_id = input("Member ID: ")
                b_id = input("Book ID: ")
                overdue, fine = library.return_book(m_id, b_id)
                print(
                    f"Book returned. Overdue days: {overdue} | Fine charged: Rs. {fine:.2f}"
                )

            elif choice == "8":
                m_id = input("Member ID: ").strip().upper()
                if m_id not in library.members:
                    raise LibraryError(f"Member '{m_id}' not found.")
                amount = float(input("Amount to pay (Rs.): "))
                remaining = library.members[m_id].pay_fine(amount)
                library.save_data()
                print(f"Payment recorded. Remaining fine: Rs. {remaining:.2f}")

            elif choice == "9":
                summary = library.get_summary()
                print("\n--- Library Summary ---")
                for key, value in summary.items():
                    label = key.replace("_", " ").title()
                    print(f"  {label}: {value}")

            elif choice == "0":
                print("Goodbye!")
                break

            else:
                print("Invalid choice. Please enter a number from 0 to 9.")

        except (LibraryError, ValueError) as exc:
            print(f"Error: {exc}")


def run_demo() -> None:
    """Runs an automated end-to-end demonstration of all OOP features."""
    demo_file = Path("demo_library_data.json")
    if demo_file.exists():
        demo_file.unlink()

    lib = Library(str(demo_file))
    print("--- Initial Catalog ---")
    for book in lib.books.values():
        print(" ", book)

    # Polymorphism in action: Student vs Faculty loan periods and fine rates
    issue_day = date(2026, 11, 1)
    student_due = lib.issue_book("S101", "B101", borrow_date=issue_day)
    faculty_due = lib.issue_book("F201", "B102", borrow_date=issue_day)
    print(f"\nStudent S101 due date (14 days): {student_due}")
    print(f"Faculty F201 due date (30 days): {faculty_due}")

    # Return Student book 4 days late -> 4 * Rs. 5 = Rs. 20 fine
    overdue_s, fine_s = lib.return_book(
        "S101", "B101", return_date=student_due + timedelta(days=4)
    )
    print(f"Student S101 returned late by {overdue_s} days -> Fine: Rs. {fine_s:.2f}")

    # Pay partial fine
    remaining = lib.members["S101"].pay_fine(10.0)
    lib.save_data()
    print(f"Student S101 paid Rs. 10.00 -> Remaining fine: Rs. {remaining:.2f}")

    # Verify JSON persistence by reloading
    reloaded = Library(str(demo_file))
    print("\n--- Summary After Reloading JSON ---")
    print(reloaded.get_summary())

    # Clean up temporary demo file
    if demo_file.exists():
        demo_file.unlink()


if __name__ == "__main__":
    import sys

    if "--demo" in sys.argv:
        run_demo()
    else:
        run_cli(Library())
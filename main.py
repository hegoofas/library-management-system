from abc import ABC, abstractmethod
import datetime
import os
import uuid
from enum import Enum
import csv
from datetime import datetime


class Book:

    def __init__(self, id, name_book, author_name, publication_date, price):
        self.id = id
        self.name_book = name_book
        self.author_name = author_name
        self.publication_date = datetime.strptime(
            publication_date, "%Y-%m-%d") if isinstance(
                publication_date, str) else publication_date
        self.price = float(price)
        self.borrowed_book = False

    def __str__(self):
        return f"Id: {self.id} \nName Book: {self.name_book}\nAuther Name: {self.author_name}\nPublication_date: {self.publication_date.strftime('%Y-%m-%d')}\nPrice: {self.price:.2f}"


class Library:

    def __init__(self):
        self.books = []
        self.borrowed_books = []

    def load_books(self, filename="100_books_data_clean.csv"):
        with open(filename, "r", encoding="latin1") as f:
            book_reader = csv.DictReader(f)
            for row in book_reader:
                id = row["id"]
                name_book = row["name_book"]
                author_name = row["author_name"]
                publication_date = row["publication_date"]
                price = row["price"]
                book = Book(id, name_book, author_name, publication_date,
                            price)
                self.books.append(book)

    def save_books(self, filename="100_books_data_clean.csv"):
        with open(filename, "w", newline='', encoding="latin1") as f:
            writer = csv.writer(f)
            writer.writerow([
                "id", "name_book", "author_name", "publication_date", "price"
            ])
            for book in self.books:
                writer.writerow([
                    book.id, book.name_book, book.author_name,
                    book.publication_date.strftime("%Y-%m-%d"),
                    f"{book.price:.2f}"
                ])

    def view_transactions(self, filename="Transactions.csv"):
        try:
            with open(filename, mode="r", encoding="latin1") as f:
                reader = csv.reader(f)
                transactions = list(reader)
        except FileNotFoundError:
            print("Transactions file not found.")
            return

        if len(transactions) <= 1:
            print("No transactions found.")
            return

        print("\n=== Transactions List ===\n")
        for row in transactions[1:]:  
            process_type = row[0]
            time = row[1]
            customer_name = row[2]
            customer_id = row[3]
            book_name = row[4]
            book_id = row[5]
            price = row[6] if row[6] else "0"

            print(f"Process Type : {process_type}")
            print(f"Time         : {time}")
            print(f"Customer Name: {customer_name}")
            print(f"Customer ID  : {customer_id}")
            print(f"Book Name    : {book_name}")
            print(f"Book ID      : {book_id}")
            print(f"Price        : {price}")
            
            print(" ")
            print("-" * 40)
            print(" ")



        
class SearchManager:

    def __init__(self, library):
        self.library = library

    def search(self, name):
        name = name.lower()
        for book in self.library.books:
            if name in book.name_book.lower():
                return True
        return False


class Screen:

    def show_message(self, message):
        print(message)

    def clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")


class Keypad:

    def get_input(self, message):
        return input(message)


class Customer:

    def __init__(self, name):
        self.name = name
        self.id = uuid.uuid4()


class ProcessType(Enum):
    ADD = "Add"
    REMOVE = "Remove"
    BORROW = "Borrow"
    BUY = "Buy"
    RETURN = "Return"


class Process(ABC):

    def __init__(self, process_type, library, customer = None):
        self.process_id = uuid.uuid4()
        self.timestamp = datetime.now()
        self.process_type = process_type
        self.library = library
        self.search_manager = SearchManager(library)
        self.customer = customer

    @abstractmethod
    def execute(self):
        pass


class AddProcess(Process):

    def __init__(self, library, manager):
        super().__init__(ProcessType.ADD, library)
        self.manager = manager
        self.keypad = Keypad()
        self.screen = Screen()

    def execute(self):
        book_name = self.keypad.get_input("Enter Book Name: ")
        if self.search_manager.search(book_name):
            self.screen.show_message(f"Book: {book_name} Already Exists.")
            return
        author = self.keypad.get_input("Enter Author Name: ")
        publication_date = self.keypad.get_input(
            "Enter Publication Date (YYYY-MM-DD): ")
        price = self.keypad.get_input("Enter Price: ")

        new_id = str(len(self.library.books) + 1)
        book = Book(new_id, book_name, author, publication_date, price)
        self.library.books.append(book)
        self.library.save_books()

        self.screen.show_message(
            f"Book: {book_name} Added Successfully with ID {new_id}.")


class RemoveProcess(Process):

    def __init__(self, library,manager):
        super().__init__(ProcessType.REMOVE, library)
        self.manager = manager
        self.keypad = Keypad()
        self.screen = Screen()

    def execute(self):
        book_name = self.keypad.get_input("Enter Book Name: ")
        if not self.search_manager.search(book_name):
            self.screen.show_message(f"Book: {book_name} Not Found.")
            return

        for book in self.library.books:
            if book_name.lower() in book.name_book.lower():
                if book.borrowed_book:
                    self.screen.show_message(
                        f"Cannot remove book '{book.name_book}' as it is currently borrowed."
                    )
                    return

        self.library.books = [
            book for book in self.library.books
            if book_name.lower() not in book.name_book.lower()
        ]

        for index, book in enumerate(self.library.books, start=1):
            book.id = str(index)

        self.library.save_books()
        self.screen.show_message(f"Book: {book_name} Removed Successfully.")


class BorrowProcess(Process):

    def __init__(self, library, customer):
        super().__init__(ProcessType.BORROW, library, customer)
        self.customer = customer
        self.keypad = Keypad()
        self.screen = Screen()

    def execute(self):
        book_name = self.keypad.get_input("Enter Book Name: ")
        if not self.search_manager.search(book_name):
            self.screen.show_message(f"Book: {book_name} Not Found.")
            return
        for book in self.library.books:
            if book_name.lower() in book.name_book.lower():
                if book.borrowed_book:
                    self.screen.show_message(
                        f"Book: {book.name_book} Already Borrowed.")
                    return
                book.borrowed_book = True
                self.library.borrowed_books.append(
                    f"{book.name_book} Borrowed By: {self.customer.name} has Id: {self.customer.id}"
                )

                with open("Transactions.csv",
                          mode="a",
                          newline='',
                          encoding="latin1") as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        self.process_type.value,
                        self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        self.customer.name,
                        str(self.customer.id), book.name_book, book.id, ""
                    ])

                with open("Borrowed Books.csv",
                          mode="a",
                          newline='',
                          encoding="latin1") as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        self.customer.id, self.customer.name, book.name_book,
                        book.id
                    ])

                self.screen.show_message(
                    f"Id Process: {self.process_id} \n"
                    f"Process Type: {self.process_type} \n"
                    f"Time: {self.timestamp} \n"
                    f"Customer: {self.customer.name} \n"
                    f"Book: {book.name_book} Borrowed Successfully.")
                return


class ReturnProcess(Process):

    def __init__(self, library, customer):
        super().__init__(ProcessType.RETURN, library, customer)
        self.customer = customer
        self.keypad = Keypad()
        self.screen = Screen()

    def execute(self):
        book_name = self.keypad.get_input("Enter Book Name to Return: ")
        for book in self.library.books:
            if book_name.lower() in book.name_book.lower():
                if not book.borrowed_book:
                    self.screen.show_message(
                        f"Book: {book.name_book} is not currently borrowed.")
                    return
                book.borrowed_book = False

                with open("Transactions.csv",
                          mode="a",
                          newline='',
                          encoding="latin1") as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        self.process_type.value,
                        self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        self.customer.name,
                        str(self.customer.id), book.name_book, book.id, ""
                    ])

                self.screen.show_message(
                    f"Process ID: {self.process_id} \n"
                    f"Transaction Type: {self.process_type.value} \n"
                    f"Time: {self.timestamp} \n"
                    f"Customer: {self.customer.name} \n"
                    f"Book: {book.name_book} Returned Successfully.")
                return
        self.screen.show_message(f"Book: {book_name} Not Found in Library.")


class BuyProcess(Process):

    def __init__(self, library, customer):
        super().__init__(ProcessType.BUY, library, customer)
        self.customer = customer
        self.keypad = Keypad()
        self.screen = Screen()

    def execute(self):
        book_name = self.keypad.get_input("Enter Book Name: ")
        if not self.search_manager.search(book_name):
            self.screen.show_message(f"Book: {book_name} Not Found.")
            return

        price = None
        book_id = None
        for book in self.library.books:
            if book_name.lower() in book.name_book.lower():
                if book.borrowed_book:
                    self.screen.show_message(
                        f"Book: {book.name_book} is currently borrowed and cannot be bought."
                    )
                    return
                price = book.price
                book_id = book.id
                self.library.books.remove(book)
                break

        if price is None:
            self.screen.show_message(
                f"Book: {book_name} Not Found in Library.")
            return

        for index, book in enumerate(self.library.books, start=1):
            book.id = str(index)

        self.library.save_books()

        with open("Transactions.csv", mode="a", newline='',
                  encoding="latin1") as f:
            writer = csv.writer(f)
            writer.writerow([
                self.process_type.value,
                self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                self.customer.name,
                str(self.customer.id), book_name, book_id, f"{price:.2f}"
            ])

        self.screen.show_message(
            f"Process ID: {self.process_id} \n"
            f"Transaction Type: {self.process_type.value} \n"
            f"Time: {self.timestamp} \n"
            f"Customer: {self.customer.name} \n"
            f"Book: {book_name} Bought Successfully with Price: {price:.2f}.")


class library_system:

    def __init__(self):
        self.library = Library()
        self.library.load_books()
        self.keypad = Keypad()
        self.screen = Screen()
        self.customer = None
        self.buy = None
        self.borrow = None
        self.return_book = None

    def run(self):
        self.screen.show_message("Welcome to the Library System!")

        self.name = self.keypad.get_input("Enter Your Name: ")
        self.customer = Customer(self.name)
        self.buy = BuyProcess(self.library, self.customer)
        self.borrow = BorrowProcess(self.library, self.customer)
        self.return_book = ReturnProcess(self.library, self.customer)
        self.keypad.get_input(
            f"Hello {self.customer.name}!\npress Enter to Continue..")
        self.screen.clear_screen()
        while True:
            self.screen.show_message("1. Borrow Book")
            self.screen.show_message("2. Return Book")
            self.screen.show_message("3. Buy Book")
            self.screen.show_message("4. Exit")
            choice = self.keypad.get_input("Enter Your Choice: ")
            self.screen.clear_screen()
            if choice == "1":
                self.borrow.execute()
            elif choice == "2":
                self.return_book.execute()
            elif choice == "3":
                self.buy.execute()
            elif choice == "4":
                self.screen.show_message(
                    "Thank You for Using the Library System")
                break
            else:
                self.screen.show_message("Invalid Choice. Please Try Again.")
            self.keypad.get_input("Press Enter to Continue..")
            self.screen.clear_screen()


class Manager:

    def __init__(self, name="Gofa", id="12356", password="123456789"):
        self.name = name
        self.__id = id
        self.__password = password
        self.library = Library()
        self.library.load_books()
        self.keypad = Keypad()
        self.screen = Screen()
        self.add = AddProcess(self.library,self)
        self.remove = RemoveProcess(self.library,self)

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, new_id):
        self.__id = new_id
        self.screen.show_message(
            f"The id has been changed successfully, it is: {new_id}")

    @staticmethod
    def is_valid_password(password):
        if password.isdigit() and len(password) >= 8:
            return True
        else:
            return False

    @property
    def password(self):
        return self.__password

    @password.setter
    def password(self, new_password):
        if Manager.is_valid_password(new_password):
            self.__password = new_password
        else:
            self.screen.show_message("Invalid password format.")

    def start(self):
        attempts = 0
        while attempts < 3:
            id = self.keypad.get_input("Enter Your ID: ")
            password = self.keypad.get_input("Enter Your Password: ")
            if id == self.id and password == self.password:
                self.screen.show_message(f"Welcome Mr: {self.name}")
                while True:
                    self.screen.show_message("1. Add Book")
                    self.screen.show_message("2. Remove Book")
                    self.screen.show_message("3. View All Books")
                    self.screen.show_message("4. View Borrowed Books")
                    self.screen.show_message("5. Change Password ")
                    self.screen.show_message("6. View Transactions")
                    self.screen.show_message("7. Exit")
                    choice = self.keypad.get_input("Enter Your Choice: ")
                    self.screen.clear_screen()
                    if choice == "1":
                        self.add.execute()
                    elif choice == "2":
                        self.remove.execute()
                    elif choice == "3":
                        for book in self.library.books:
                            self.screen.show_message(book)
                    elif choice == "4":
                        for book in self.library.borrowed_books:
                            self.screen.show_message(book)
                    elif choice == "5":
                        new_password = self.keypad.get_input(
                            "Enter Your New Password: ")
                        if Manager.is_valid_password(new_password):
                            self.password = new_password
                        else:
                            self.screen.show_message(
                                "Invalid password format.")
                    elif choice == "6":
                        self.library.view_transactions()
                    elif choice == "7":
                        self.screen.show_message(
                            "Thank You for Using the Library System")
                        break 

            else:
                self.screen.show_message(
                    "Invalid ID or Password. Please Try Again.")
                attempts += 1
                return


if __name__ == "__main__":
    manager = Manager()
    manager.start()
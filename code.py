from collections import UserDict
from datetime import datetime, timedelta


#Створення декоратора

def input_error(func):
    def inner(*args):
        try:
            return func(*args)
        except ValueError as e:
            return str(e)
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Not enough arguments."
    return inner


'''
Формування класів
'''

class Field:
    def __init__(self, value):
        self.value = value

#створення класу для імені контакту
class Name(Field):
    pass

#створення класу для телефону 

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must contain 10 digits.")
        super().__init__(value)

#створення класу для народження

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)


#створення класу для одного запису контакту

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None  # нове поле

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def change_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                p.value = Phone(new_phone).value
                return
        raise ValueError("Phone not found.")

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = "; ".join(p.value for p in self.phones)
        birthday = self.birthday.value if self.birthday else "Not set"
        return f"{self.name.value}: phones: {phones}, birthday: {birthday}"


#Створення класу адресної книги, яку використовуватиме бот

class AddressBook(UserDict):

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        result = []

        for record in self.data.values():
            if record.birthday:
                birthday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                birthday_this_year = birthday_date.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                delta = (birthday_this_year - today).days

                if 0 <= delta <= 7:
                    congratulation_date = birthday_this_year

                    if congratulation_date.weekday() == 5:
                        congratulation_date += timedelta(days=2)
                    elif congratulation_date.weekday() == 6:
                        congratulation_date += timedelta(days=1)

                    result.append({
                        "name": record.name.value,
                        "birthday": congratulation_date.strftime("%d.%m.%Y")
                    })

        return result


@input_error
def add_contact(args, book):
    name, phone = args
    record = book.find(name)

    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    else:
        message = "Contact updated."

    record.add_phone(phone)
    return message


@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)

    if record is None:
        raise KeyError

    record.change_phone(old_phone, new_phone)
    return "Phone changed."


@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)

    if record is None:
        raise KeyError

    return "; ".join(p.value for p in record.phones)


@input_error
def show_all(args, book):
    if not book.data:
        return "No contacts saved."

    result = ""
    for record in book.data.values():
        result += str(record) + "\n"

    return result.strip()


@input_error
def add_birthday_handler(args, book):
    name, birthday = args
    record = book.find(name)

    if record is None:
        raise KeyError

    record.add_birthday(birthday)
    return "Birthday added."


@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)

    if record is None:
        raise KeyError

    if record.birthday is None:
        return "Birthday not set."

    return record.birthday.value


@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()

    if not upcoming:
        return "No birthdays in the next 7 days."

    result = ""
    for item in upcoming:
        result += f"{item['name']} - {item['birthday']}\n"

    return result.strip()


#створення парсера

def parse_input(user_input):
    parts = user_input.strip().split()
    command = parts[0].lower()
    return command, parts[1:]


#формування список команд бота

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(args, book))

        elif command == "add-birthday":
            print(add_birthday_handler(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
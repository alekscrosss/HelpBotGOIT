from datetime import datetime
from abc import ABC, abstractmethod
from collections import UserDict
import pickle
from sort import clean_folder_interface
from note import notebook_interface, Note
import os
import re #16.10.23 Olha
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ADDRESS_BOOK_PATH = os.path.join(BASE_DIR, 'address_book.dat')
class UserInterface(ABC):
    @abstractmethod
    def display_contacts(self, contacts):
        pass
    @abstractmethod
    def display_notes(self, notes):
        pass
    @abstractmethod
    def display_commands(self, commands):
        pass
class ConsoleInterface(UserInterface):
    def display_contacts(self, contacts):
        for contact in contacts:
            print(contact)
    def display_notes(self, notes):
        for note in notes:
            print(note)
    def display_commands(self, commands):
        if isinstance(commands, str):  # Перевірка, чи commands є рядком
            print(commands)
        else:  # Якщо commands - це ітерований об'єкт
            print("Available commands:")
            for command in commands:
                print(command)
class Field:
    def __init__(self, value=None):
        self.value = value
    def set_value(self, value):
        self.value = value
    def get_value(self):
        return self.value
class Name(Field):
    def __init__(self, value):
        super().__init__(value)
class Phone(Field):
    def set_value(self, value):
        validated_phone = self.validate_phone(value) # 15.10.23 modify Yulia
        if validated_phone is None: # 15.10.23 modify Yulia
            print("Invalid phone number format")  # check phone
        else:
            self.value = validated_phone
    @staticmethod
    def validate_phone(phone):
        new_phone = (
            str(phone).strip()
            .removeprefix("+")
            .replace("(", "")
            .replace(")", "")
            .replace("-", "")
            .replace(" ", "")
        )
        if new_phone.startswith("38") and len(new_phone) == 12:  # 15.10.23 modify Yulia
            return "+" + new_phone
        elif len(new_phone) == 10:
            return '+38' + new_phone
        else:
            return None # 15.10.23 modify Yulia
class EmailAddress(Field):
    def __init__(self, value):  # =None убрала 16.10 Olha
        super().__init__(value)
    def set_value(self, value):
        validated_email = self.validate_email(value)
        if isinstance(value, str) and self.validate_email(value):
            self.value = validated_email #value
        else:
            print("Invalid email format")
    def get_value(self):
        return self.value
    @staticmethod
    def validate_email(email):   #16.10.23
        pattern = r'[A-Za-z][A-Za-z0-9._]+@[A-Za-z]+\.[A-Za-z]{2,}\b'
        temp_email = re.findall(pattern, email)
        if temp_email:
            return "".join(temp_email)  # True
        else:
            return False
class Birthday(Field):
    def __init__(self, value=None):
        super().__init__(value)
    def set_value(self, value):
        try:
            datetime.strptime(value, "%d.%m.%y")
        except ValueError:
            try:
                # пытаемся прочитать дату в формате 'dd-mm-yy'
                datetime.strptime(value, "%d-%m-%y")
            except ValueError:
                print("Invalid date format. Please use 'dd.mm.yy'")
                return
        self.value = value
    def days_to_birthday(self):
        if self.value is None:
            return None
        birth_date = datetime.strptime(self.value, "%d.%m.%y").date()
        current_date = datetime.now().date()  # Use only the date part
        # Calculate next birthday date
        next_birthday_year = current_date.year
        if (current_date.month, current_date.day) > (birth_date.month, birth_date.day):
            next_birthday_year += 1
        next_birthday_date = datetime(next_birthday_year, birth_date.month, birth_date.day).date()
        difference = next_birthday_date - current_date
        days_until_birthday = difference.days
        return days_until_birthday
class Record:
    def __init__(self, name, birthday=None, email=None):
        self.name = Name(name)
        self.phones = []
        self.emails = [] if email else [EmailAddress(email)]
        self.birthday = Birthday(birthday)
    def add_email(self, email):
        if isinstance(email, EmailAddress):
            self.emails.append(email)
        elif EmailAddress.validate_email(email):
            email_value = EmailAddress.validate_email(email)
            if email_value:
                self.emails.append(EmailAddress(email_value))
            else:
                print("Invalid email number format")
        else:
            self.emails.append(EmailAddress(None))  # new - пофиксила баг с корректной перезаписью Email
            print("Invalid email number format")
    def get_emails(self):
        if hasattr(self, 'emails'):
            return [email for email in self.emails if email and isinstance(email, EmailAddress)] if self.emails else []
        elif hasattr(self, 'email'):
            return [self.email] if self.email and isinstance(self.email, EmailAddress) else []
        else:
            return []
    def add_phone(self, phone):
        if isinstance(phone, Phone):  
            self.phones.append(phone)
        elif Phone.validate_phone(phone):
            phone_value = Phone.validate_phone(phone)
            if phone_value:
                self.phones.append(Phone(phone_value))
            else:
                raise ValueError("Invalid phone number format")
        else:
            raise ValueError("Invalid phone number format")
    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]
    def remove_email(self, email):
        self.emails = [p for p in self.emails if p.value != email]
    def edit_phone(self, phone, new_phone):
        for p in self.phones:
            if p.value == phone:
                p.set_value(new_phone)
                break
        else:
            raise ValueError("Phone number not found")
    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
    def get_email(self):
        return self.email.get_value() if self.email else None
    def edit_email(self, email, new_email):
        for p in self.emails:
            if p.value == email:
                p.set_value(new_email)
                break
        else:
            raise ValueError("Email not found")
class AddressBook(UserDict):
    def __init__(self, filename, ui):
        super().__init__()
        self.ui = ui
        self.page_size = 5
        self.filename = filename
    def add_record(self, record):
        self.data[record.name.get_value()] = record
    def find(self, name):
        return self.data.get(name)
    def delete(self, name):
        if name in self.data:
            del self.data[name]
    def iterator(self):
        records = list(self.data.values())
        for i in range(0, len(records), self.page_size):
            yield records[i:i + self.page_size]
    def save_to_file(self):
        try:
            with open(self.filename, 'wb') as file:
                pickle.dump(self.data, file)
            print(f'Address book saved to {self.filename}')
        except Exception as e:
            print(f'Error saving to {self.filename}: {str(e)}')
    def read_from_file(self):
        try:
            with open(self.filename, 'rb') as file:
                data = pickle.load(file)
                self.data = data
            print(f'Address book loaded from {self.filename}')
        except FileNotFoundError:
            print(f'File {self.filename} not found. Creating a new address book.')
        except Exception as e:
            print(f'Error reading from {self.filename}: {str(e)}')
    def search(self, query):
        query = query.lower()
        results = []
        for record in self.data.values():
            if query in record.name.get_value().lower():
                results.append(record)
            for phone in record.phones:
                if query in phone.get_value():
                    results.append(record)
        return results
    def delete_contact(self, name):
        if name in self.data:
            del self.data[name]
            self.save_to_file()  # Save data after each deletion
            print(f"Contact {name} deleted from address_bot - saved.")
        else:
            print(f"Contact {name} not found.")
    def iterator(self, page_number=None):
            records = list(self.data.values())
            if page_number:
                start_idx = (page_number - 1) * self.page_size
                end_idx = start_idx + self.page_size
                page_records = records[start_idx:end_idx]
            else:
                page_records = records
            return page_records
    def get_page(self, page_number):
        start_index = (page_number - 1) * self.page_size
        end_index = start_index + self.page_size
        records = list(self.data.values())[start_index:end_index]
        return records
    def get_total_pages(self):
        total_contacts = len(self.data)
        return (total_contacts + self.page_size - 1) // self.page_size
def handle_command(address_book, command):
    parts = command.lower().split()
    if not parts:
        print("Enter a command. Type 'helper' for a list of available commands.")
        return ""
    action, *args = parts
    if action == "add":
        if len(args) < 2:
            return "Invalid format for 'add' command. Please provide a name and at least one phone number."
        name = args[0]
        phones = []
        email = None
        birthday = None
        for arg in args[1:]:
            if "@" in arg or any(char.isalpha() for char in arg): #Добавила проверку, чтобы были еще буквы в Email
                email = arg
            elif len(arg.split('.')) == 3:
                birthday = arg
            else:
                phones.append(arg)
        record = Record(name, birthday, email)
        for phone in phones:
            phone_value = Phone.validate_phone(phone)
            if phone_value:
                phone_obj = Phone(phone_value)
                record.add_phone(phone_obj)
            else:
                return "Invalid phone number format"
        if email:
            record.add_email(email)
        address_book.add_record(record)
        address_book.save_to_file()
        phones_str = ', '.join([str(p.get_value()) for p in record.phones])
        email_str = ', '.join([str(email.get_value()) for email in record.get_emails()])
        birthday_str = record.birthday.get_value() or "None"  # Use "None" if birthday is None
        response = f"Contact {name} added with the following information:\n" \
                f"Name: {record.name.get_value()}\n" \
                f"Phone: {phones_str}\n" \
                f"Email: {email_str}\n" \
                f"Birthday: {birthday_str}"
        if birthday:
            days_left = record.birthday.days_to_birthday()
            if days_left is not None:
                response += f"\n{days_left} days left until the next birthday."
        response += "\nContact saved!"
        return response
    elif action == "delete":
        if len(args) < 1:
            return "Invalid format for 'delete' command. Please provide a name."
        name = args[0]
        address_book.delete_contact(name)
        return ""
    elif action == "notebook":
        notebook_interface()
        return "Work with notebook is completed."
    elif action == "birthday" and args[0]:
        if len(args) < 2:
            return "Invalid format for 'add birthday' command. Please provide a name and a birthday date."
        name = args[0]
        birthday = args[1]
        record = Record(name, birthday)
        address_book.add_record(record)
        response = f"Contact {name} added with birthday: {birthday}"
        days_left = record.birthday.days_to_birthday()
        if days_left is not None:
            response += f"\n{days_left} days left until the next birthday."
        return response
    elif action == "change":
        if len(args) < 2:
            return "Invalid format for 'change' command. Please provide a name and either a new phone number, email, or birthday."
        name = args[0]
        record = address_book.find(name)
        if record:
            change_type = args[1].lower()
            if change_type == "phone" and len(args) >= 3:
                new_phone = args[2]
                try:
                    record.edit_phone(record.phones[0].get_value(), new_phone)
                    address_book.save_to_file()
                    # Empty string to suppress success message
                    return "" if Phone.validate_phone(new_phone) else ""
                except ValueError:
                    return "Invalid phone number format"
            elif change_type == "email" and len(args) >= 3:
                new_email = args[2]
                try:
                    record.edit_email(record.emails[0].get_value(), new_email)
                    address_book.save_to_file()
                    return ""  # Empty string to suppress success message
                except ValueError:
                    return "Invalid email format"
            elif change_type == "birthday" and len(args) >= 3:
                new_birthday = args[2]
                try:
                    datetime.strptime(new_birthday, "%d.%m.%y")
                    record.birthday.set_value(new_birthday)
                    address_book.save_to_file()
                    return f"Contact {name} birthday changed to {new_birthday}"
                except ValueError:
                    print("Invalid date format. Please use 'dd.mm.yy'")
                    return f"Contact {name} birthday didn't change. Invalid date format. Please use 'dd.mm.yy'"
    elif action == "find":
        if len(args) < 1:
            return "Invalid format for 'find' command. Please provide a search query."
        search_query = ' '.join(args)
        results = address_book.search(search_query)
        if results:
            contacts_info = []
            for record in results:
                phones_str = ', '.join([p.get_value() for p in record.phones])
                info = f"{record.name.get_value()}: {phones_str} | {record.birthday.get_value()}"
                if record.birthday.get_value():
                    days_left = record.birthday.days_to_birthday()
                    birthday_info = f" | Birthday in {days_left} days" if days_left is not None else ""
                    info += birthday_info
                contacts_info.append(info)
            return "\n".join(contacts_info)
        else:
            return f"No contacts found for '{search_query}'"
    elif action == "phone":
        if len(args) < 1:
            return "Invalid format for 'phone' command. Please provide a name."
        name = args[0]
        record = address_book.find(name)
        if record:
            phones_str = ', '.join([p.get_value() for p in record.phones])
            birthday_info = ""
            if record.birthday.get_value():
                days_left = record.birthday.days_to_birthday()
                birthday_info = f" | Birthday in {days_left} days" if days_left is not None else ""
            return f"Phone number for {name}: {phones_str} | {record.birthday.get_value()} {birthday_info}"
        else:
            return f"Contact {name} not found"
    elif action == "email":
        if len(args) < 1:
            return "Invalid format for 'email' command. Please provide a name."
        name = args[0]
        record = address_book.find(name)

        if record:
            emails_list = []
            for i in record.emails:
                if i is not None:
                    emails_list.append(str(i.get_value()))
            if emails_list:
                emails_str = ', '.join(emails_list)
            else:
                emails_str = "No emails"
            return f"Email for {name}: {emails_str}"
        else:
            return f"Contact {name} not found"
    elif action == "show" and args and args[0] == "all":
        page_number = int(args[1]) if len(args) > 1 and args[1].isdigit() else 1
        total_pages = address_book.get_total_pages()
        if page_number < 1 or page_number > total_pages:
            return f"Invalid page number. Please provide a number between 1 and {total_pages}."
        page_records = address_book.iterator(page_number)
        if not page_records:
            return f"No contacts found on page {page_number}."
        contacts_info = []
        for record in page_records:
            phones_str = ', '.join([str(p.get_value()) for p in record.phones])
            email_str = ', '.join([str(email.get_value()) for email in record.get_emails()])
            birthday_str = record.birthday.get_value() or "None"  # Використовуйте "None", якщо день народження немає
            info = f"{record.name.get_value()} | Phone: {phones_str or '-'} | Email: {email_str or '-'} | Birthday: {birthday_str or '-'}"
            if record.birthday.get_value():
                days_left = record.birthday.days_to_birthday()
                if days_left is not None:
                    info += f" | {days_left} days left until the next birthday."
            contacts_info.append(info)
        prev_page = page_number - 1 if page_number > 1 else None
        next_page = page_number + 1 if page_number < total_pages else None
        pagination_info = f"\nPage {page_number} of {total_pages} |"
        if prev_page is not None:
            pagination_info += f" Previous: 'show all {prev_page}' |"
        if next_page is not None:
            pagination_info += f" Next: 'show all {next_page}' |"
        contacts_info.append(pagination_info)
        return "\n".join(contacts_info)
    elif action == "celebration" and args and args[0] == "in":
        if len(args) < 2 or not args[1].isdigit():
            return "Invalid format for 'celebration in' command. Please provide a valid number of days."
        days_until_celebration = int(args[1])
        upcoming_birthdays = []
        for record in address_book.data.values():
            if record.birthday.get_value():
                days_left = record.birthday.days_to_birthday()
                if days_left is not None and days_left <= days_until_celebration:
                    phones_str = ', '.join([p.get_value() for p in record.phones])
                    upcoming_birthdays.append(f"{record.name.get_value()}: {phones_str} | {record.birthday.get_value()}. Don't forget to greet!")
        if upcoming_birthdays:
            return f"Upcoming birthdays in the next {days_until_celebration} days:\n" + "\n".join(upcoming_birthdays)
        else:
            return f"No upcoming birthdays in the next {days_until_celebration} days."
    elif action == "helper":
        return (
            "Available commands:\n"
            "  - add [name] [phone][birthday] [emai]: Add a new contact with optional phones and birthday.\n"
            "  - show all: Display all contacts with phones and optional days until the next birthday.\n"
            "  - celebration in [days]: Show upcoming birthdays in the next [days] days with names and phones.\n"
            "  - helper: Display available commands and their descriptions.\n"
            "  - find [letter] or [number]: Display all contacts with letter or number, which you saied about.\n"
            "  - change [name] [phone] or [birthday]: Changes contact, which you want.\n"
            "  - phone [name]: phoning person you want.\n"
            "  - delete [name]: Delete a contact by name.\n"  #15.10.23 Yuliya
            "  - goodbye, close, exit: Save the address book to a file and exit the program.\n"
            "  - clean: Open sorter.\n"  #15.10.23 Alex
            "  - notebook: Open notes.\n" #15.10.23 Alex 
            "  - email [name]: Shows all emails for a contact "  # 16.10.23 Olha
        )
    elif action == "unknown":
        print("Unknown command. Type 'helper' for a list of available commands.")
        return "Unknown command"
    elif action == "hello":
        return "How can I help you?"
    elif action in ["goodbye", "close", "exit"]:
        return "Good bye!"
    elif action == "clean":
        clean_folder_interface()
        return "Cleaning process finished."
    else:
        return "Unknown command"
def main():
    filename = "address_book.dat"
    ui = ConsoleInterface()
    address_book = AddressBook(filename, ui)
    address_book.read_from_file()
    ui.display_commands("Welcome to ContactBot!")
    ui.display_commands(f"Address book loaded from {filename}. {len(address_book.data)} contacts found.") # 15.10.23 modify Yulia
    command_autocomplete = {
        'a': ['add'],
        'c': ['change', 'celebration', 'clean', 'close'],
        'd': ['delete'],
        'e': ['exit'],
        'f': ['find'],
        'h': ['helper'],
        'n': ['notebook'],
        's': ['show all'],
        'p': ['phone'],
    }
    command_prompt = "Enter a command: "
    while True:
        user_input = input(command_prompt).strip()
        if not user_input:
            if not user_input:
                print("Unknown command. Type 'helper' for a list of available commands.")
            continue
        command = user_input[0]
        autocomplete_options = command_autocomplete.get(command, [])
        if autocomplete_options and len(user_input) == 1:
            print("Available commands:", ', '.join(autocomplete_options))
            continue  # Wait for the user to input the complete command
        response = handle_command(address_book, user_input)
        print(response)
        if user_input.lower() in ["goodbye", "close", "exit"]:
            address_book.save_to_file()  # Save the data before exiting
            ui.display_commands("Good bye!")
            break  # Exit the loop and end the program
if __name__ == "__main__":
    main()
    ui = ConsoleInterface()
    address_book = AddressBook(ui=ui)

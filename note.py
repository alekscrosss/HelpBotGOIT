import datetime
import pickle


class Note:
    def __init__(self, title, text, tags=None):
        self.title = title
        self.text = text
        self.tags = [] if tags is None else tags
        self.created_at = datetime.datetime.now()

    def __repr__(self):
        date_str = self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        tags_str = f"[Tags: {', '.join(self.tags)}]" if self.tags else ""
        return f'[{date_str}] {self.title} - {self.text} {tags_str}'

class Notebook:
    def __init__(self):
        self.notes = []

    def add(self, title, text, tags=None):
        note = Note(title, text, tags)
        self.notes.append(note)

    def delete(self, index):
        if 0 <= index < len(self.notes):
            del self.notes[index]
        else:
            print("Invalid note index!")

    def list_notes(self):
        if not self.notes:
            print("The notes list is empty.")
            return
        for index, note in enumerate(self.notes):
            print(f"{index}. {note}")

    def clear_all(self):
        self.notes = []

    def edit(self, index, new_title=None, new_text=None, new_tags=None):
        try:
            note = self.notes[index]
            if new_title:
                note.title = new_title
            if new_text:
                note.text = new_text
            if new_tags is not None:
                note.tags = new_tags
            return True
        except IndexError:
            return False

    def save_to_file(self, filename="notes.pkl"):
        with open(filename, 'wb') as file:
            pickle.dump(self.notes, file)

    def load_from_file(self, filename="notes.pkl"):
        try:
            with open(filename, 'rb') as file:
                self.notes = pickle.load(file)
        except FileNotFoundError:
            pass

    def search(self, keyword):
        keyword_lower = keyword.lower()
        matching_notes = []
        for note in self.notes:
            if keyword_lower in note.title.lower() or keyword_lower in note.text.lower() or any(
                    keyword_lower in tag.lower() for tag in note.tags):
                matching_notes.append(note)
        return matching_notes

    def add_tag(self, index, tag):
        try:
            note = self.notes[index]
            if tag:
                note.tags.append(tag)
            return True
        except IndexError:
            return False

    def list_tags(self):
        all_tags = set()
        for note in self.notes:
            all_tags.update(note.tags)
        return list(all_tags)

def input_with_retry(prompt, validation_func=None, error_message="Invalid input!"):
    while True:
        data = input(prompt).strip()
        if validation_func is None or validation_func(data):
            return data
        print(error_message)

def add(notebook):
    title = input_with_retry("Enter note title: ", lambda x: x != "")
    text = input_with_retry("Enter note text: ", lambda x: x != "")
    tags = input("Enter tags (comma separated, leave blank for none): ").split(',')
    tags = [tag.strip() for tag in tags if tag.strip()]
    notebook.add(title, text, tags)
    notebook.save_to_file()

def edit(notebook):
    notebook.list_notes()
    index = input_with_retry(
        "Enter the index of the note you want to edit: ",
        lambda x: x.isdigit() and 0 <= int(x) < len(notebook.notes),
        "Please enter a valid index!"
    )
    index = int(index)

    new_title = input("Enter new title (leave blank to keep current): ")
    if not new_title:
        new_title = None

    new_text = input("Enter new text (leave blank to keep current): ")
    if not new_text:
        new_text = None

    new_tags = input("Enter new tags (comma separated, leave blank for none): ").split(',')
    new_tags = [tag.strip() for tag in new_tags if tag.strip()]

    if notebook.edit(index, new_title, new_text, new_tags):
        print("Note updated successfully!")
    else:
        print("Invalid index!")
    notebook.save_to_file()

def delete(notebook):
    notebook.list_notes()
    index = input_with_retry(
        "Enter note index to delete: ",
        lambda x: x.isdigit() and 0 <= int(x) < len(notebook.notes),
        "Please enter a valid index!"
    )
    index = int(index)
    notebook.delete(index)
    notebook.save_to_file()

def search(notebook):
    keyword = input_with_retry("Enter a keyword to search for: ", lambda x: x != "")
    matching_notes = notebook.search(keyword)
    if matching_notes:
        print("Matching notes:")
        for note in matching_notes:
            print(note)
    else:
        print("No matching notes found.")

def clear(notebook):
    notebook.clear_all()
    print("All notes have been cleared.")
    notebook.save_to_file()

def tags(notebook):
    tags = notebook.list_tags()
    if tags:
        print("Tags: ", ', '.join(tags))
    else:
        print("No tags found.")

def notebook_interface():
    notebook = Notebook()
    notebook.load_from_file()
    while True:
        command = input_with_retry(
            "\nChoose an option in notes ('add', 'search', 'delete', 'edit', 'list', 'clear', 'tags', 'exit'): ",
            lambda x: x in ['add', 'delete', 'edit', 'list', 'clear', 'exit', 'search', 'tags']
        ).strip().lower()

        if command == 'add':
            add(notebook)
        elif command == 'edit':
            edit(notebook)
        elif command == 'delete':
            delete(notebook)
        elif command == 'search':
            search(notebook)
        elif command == 'list':
            notebook.list_notes()
        elif command == 'clear':
            clear(notebook)
        elif command == 'tags':
            tags(notebook)
        elif command == 'exit':
            break

if __name__ == '__main__':
    notebook_interface()

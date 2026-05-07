import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class BookTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker / Трекер прочитанных книг")
        self.root.geometry("850x600")
        self.root.minsize(700, 500)
        
        self.books = []
        self.json_file = "books_data.json"

        self._create_ui()
        self._load_from_json()

    def _create_ui(self):
        # --- Фрейм ввода ---
        input_frame = ttk.LabelFrame(self.root, text="➕ Добавить новую книгу")
        input_frame.pack(padx=10, pady=5, fill="x")

        ttk.Label(input_frame, text="Название:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_title = ttk.Entry(input_frame, width=40)
        self.entry_title.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Автор:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_author = ttk.Entry(input_frame, width=40)
        self.entry_author.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Жанр:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.entry_genre = ttk.Entry(input_frame, width=40)
        self.entry_genre.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Страниц:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.entry_pages = ttk.Entry(input_frame, width=40)
        self.entry_pages.grid(row=3, column=1, padx=5, pady=5)

        self.btn_add = ttk.Button(input_frame, text="Добавить книгу", command=self._add_book)
        self.btn_add.grid(row=4, column=1, padx=5, pady=10, sticky="e")

        # --- Фрейм фильтрации ---
        filter_frame = ttk.LabelFrame(self.root, text="🔍 Фильтрация")
        filter_frame.pack(padx=10, pady=5, fill="x")

        ttk.Label(filter_frame, text="По жанру:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.filter_genre = ttk.Entry(filter_frame, width=20)
        self.filter_genre.grid(row=0, column=1, padx=5, pady=5)
        self.filter_genre.insert(0, "Все")

        ttk.Label(filter_frame, text="Больше стр.:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.filter_pages = ttk.Entry(filter_frame, width=10)
        self.filter_pages.grid(row=0, column=3, padx=5, pady=5)

        self.btn_filter = ttk.Button(filter_frame, text="Применить", command=self._apply_filter)
        self.btn_filter.grid(row=0, column=4, padx=5, pady=5)
        self.btn_clear = ttk.Button(filter_frame, text="Сбросить", command=self._clear_filter)
        self.btn_clear.grid(row=0, column=5, padx=5, pady=5)

        # --- Таблица ---
        table_frame = ttk.Frame(self.root)
        table_frame.pack(padx=10, pady=5, fill="both", expand=True)

        columns = ("title", "author", "genre", "pages")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.tree.heading("title", text="Название")
        self.tree.heading("author", text="Автор")
        self.tree.heading("genre", text="Жанр")
        self.tree.heading("pages", text="Страниц")
        self.tree.column("title", width=250)
        self.tree.column("author", width=180)
        self.tree.column("genre", width=120)
        self.tree.column("pages", width=80, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # --- Кнопки сохранения/загрузки ---
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(padx=10, pady=5, fill="x")
        ttk.Button(btn_frame, text="💾 Сохранить в JSON", command=self._save_to_json).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="📂 Загрузить из JSON", command=self._load_from_json).pack(side="left", padx=5)

    # --- Логика приложения ---
    def _validate_input(self):
        title = self.entry_title.get().strip()
        author = self.entry_author.get().strip()
        genre = self.entry_genre.get().strip()
        pages_str = self.entry_pages.get().strip()

        if not all([title, author, genre]):
            messagebox.showerror("Ошибка ввода", "Поля 'Название', 'Автор' и 'Жанр' не должны быть пустыми.")
            return None

        try:
            pages = int(pages_str)
            if pages <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Количество страниц должно быть целым положительным числом.")
            return None

        return {"title": title, "author": author, "genre": genre, "pages": pages}

    def _add_book(self):
        book = self._validate_input()
        if book:
            self.books.append(book)
            self._refresh_table(self.books)
            self._clear_input()
            messagebox.showinfo("Успех", f"Книга '{book['title']}' добавлена в трекер!")

    def _clear_input(self):
        for entry in (self.entry_title, self.entry_author, self.entry_genre, self.entry_pages):
            entry.delete(0, tk.END)

    def _refresh_table(self, book_list):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for b in book_list:
            self.tree.insert("", tk.END, values=(b["title"], b["author"], b["genre"], b["pages"]))

    def _apply_filter(self):
        genre_val = self.filter_genre.get().strip().lower()
        pages_val = self.filter_pages.get().strip()

        filtered = self.books.copy()

        if genre_val and genre_val != "все":
            filtered = [b for b in filtered if b["genre"].lower() == genre_val]

        if pages_val:
            try:
                min_pages = int(pages_val)
                filtered = [b for b in filtered if b["pages"] > min_pages]
            except ValueError:
                messagebox.showwarning("Фильтр", "Введите корректное число для фильтра по страницам.")
                return

        self._refresh_table(filtered)

    def _clear_filter(self):
        self.filter_genre.delete(0, tk.END)
        self.filter_genre.insert(0, "Все")
        self.filter_pages.delete(0, tk.END)
        self._refresh_table(self.books)

    def _save_to_json(self):
        try:
            with open(self.json_file, "w", encoding="utf-8") as f:
                json.dump(self.books, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Сохранение", f"Данные успешно сохранены в {self.json_file}")
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", str(e))

    def _load_from_json(self):
        if os.path.exists(self.json_file):
            try:
                with open(self.json_file, "r", encoding="utf-8") as f:
                    self.books = json.load(f)
                self._refresh_table(self.books)
                messagebox.showinfo("Загрузка", f"Загружено {len(self.books)} книг.")
            except json.JSONDecodeError:
                messagebox.showerror("Ошибка загрузки", "Файл JSON повреждён.")
            except Exception as e:
                messagebox.showerror("Ошибка загрузки", str(e))
        else:
            self.books = []
            self._refresh_table([])

if __name__ == "__main__":
    root = tk.Tk()
    app = BookTrackerApp(root)
    root.mainloop()
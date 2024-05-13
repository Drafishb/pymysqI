def display_code():
    code = """
import tkinter as tk
from tkinter import ttk, messagebox
import pymysql


class DatabaseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Database App")

        # Создание и размещение виджетов для авторизации
        self.login_frame = ttk.Frame(self.root)
        self.login_frame.pack(padx=20, pady=20)
        self.username_label = ttk.Label(self.login_frame, text="Логин:")
        self.username_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.username_entry = ttk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        self.password_label = ttk.Label(self.login_frame, text="Пароль:")
        self.password_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.password_entry = ttk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        self.login_button = ttk.Button(self.login_frame, text="Войти", command=self.login)
        self.login_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        # Инициализация соединения с базой данных
        self.db = None

    def login(self):
        # Подключение к базе данных
        try:
            self.db = pymysql.connect(host='localhost',
                                      user='root',
                                      password='pfrpCnd47Dz75VX7',
                                      database='TestBD',
                                      charset='utf8mb4',
                                      cursorclass=pymysql.cursors.DictCursor)

            # Проверка логина и пароля
            with self.db.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE Login=%s AND Password=%s",
                               (self.username_entry.get(), self.password_entry.get()))
                user = cursor.fetchone()
                if user:
                    # Успешная авторизация, показываем таблицу
                    self.show_table()
                else:
                    messagebox.showerror("Ошибка", "Неверный логин или пароль")
        except pymysql.Error as e:
            messagebox.showerror("Ошибка", "Неверный логин или пароль: {}".format(str(e)))

    def show_table(self):
        # Удаление виджетов авторизации
        self.login_frame.destroy()

        # Создание и размещение виджетов для работы с таблицей
        self.table_frame = ttk.Frame(self.root)
        self.table_frame.pack(padx=20, pady=20)

        # Создание таблицы для вывода данных
        self.data_tree = ttk.Treeview(self.table_frame, columns=("ID", "Name", "Age"))
        self.data_tree.heading("#0", text="ID")
        self.data_tree.heading("#1", text="Name")
        self.data_tree.heading("#2", text="Age")
        self.data_tree.pack(expand=True, fill="both")

        # Заполнение таблицы данными из базы данных
        self.refresh_table()

        # Кнопки для добавления, редактирования и удаления записей
        self.add_button = ttk.Button(self.table_frame, text="Добавить", command=self.add_record)
        self.add_button.pack(side="left", padx=5, pady=5)
        self.edit_button = ttk.Button(self.table_frame, text="Редактировать", command=self.edit_record)
        self.edit_button.pack(side="left", padx=5, pady=5)
        self.delete_button = ttk.Button(self.table_frame, text="Удалить", command=self.delete_record)
        self.delete_button.pack(side="left", padx=5, pady=5)

    def refresh_table(self):
        # Очистка таблицы
        for row in self.data_tree.get_children():
            self.data_tree.delete(row)

        # Запрос данных из базы данных
        with self.db.cursor() as cursor:
            cursor.execute("SELECT * FROM your_table")
            for row in cursor.fetchall():
                self.data_tree.insert("", "end", text=row['id'], values=(row['id'], row['name'], row['age']))

    def add_record(self):
        # Создание диалогового окна для ввода данных
        self.add_window = tk.Toplevel(self.root)
        self.add_window.title("Add Record")
        self.add_window.grab_set()

        self.name_label = ttk.Label(self.add_window, text="Name:")
        self.name_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.name_entry = ttk.Entry(self.add_window)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        self.age_label = ttk.Label(self.add_window, text="Age:")
        self.age_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.age_entry = ttk.Entry(self.add_window)
        self.age_entry.grid(row=1, column=1, padx=5, pady=5)

        self.save_button = ttk.Button(self.add_window, text="Сохранить", command=self.save_record)
        self.save_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

    def save_record(self):
        # Получение данных из полей ввода
        name = self.name_entry.get()
        age = self.age_entry.get()

        # Вставка записи в базу данных
        with self.db.cursor() as cursor:
            cursor.execute("INSERT INTO your_table (Name, Age) VALUES (%s, %s)", (name, age))
            self.db.commit()

        # Закрытие диалогового окна
        self.add_window.destroy()

        # Обновление таблицы
        self.refresh_table()

    def edit_record(self):
        # Получение выделенной записи из таблицы
        selected_item = self.data_tree.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Не выбрана запись")
            return

        # Получение данных выбранной записи
        item_values = self.data_tree.item(selected_item, "values")
        record_id = item_values[0]
        name = item_values[1]
        age = item_values[2]

        # Создание диалогового окна для редактирования данных
        self.edit_window = tk.Toplevel(self.root)
        self.edit_window.title("Edit Record")
        self.edit_window.grab_set()

        self.name_label = ttk.Label(self.edit_window, text="Name:")
        self.name_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.name_entry = ttk.Entry(self.edit_window)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        self.name_entry.insert(0, name)

        self.age_label = ttk.Label(self.edit_window, text="Age:")
        self.age_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.age_entry = ttk.Entry(self.edit_window)
        self.age_entry.grid(row=1, column=1, padx=5, pady=5)
        self.age_entry.insert(0, age)

        self.save_button = ttk.Button(self.edit_window, text="Сохранить", command=lambda: self.save_edited_record(record_id))
        self.save_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

    def save_edited_record(self, record_id):
        # Получение данных из полей ввода
        name = self.name_entry.get()
        age = self.age_entry.get()

        # Обновление записи в базе данных
        with self.db.cursor() as cursor:
            cursor.execute("UPDATE your_table SET Name=%s, Age=%s WHERE id=%s", (name, age, record_id))
            self.db.commit()

        # Закрытие диалогового окна
        self.edit_window.destroy()

        # Обновление таблицы
        self.refresh_table()

    def delete_record(self):
        # Получение выделенной записи из таблицы
        selected_item = self.data_tree.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Не выбрана запись")
            return

        # Получение ID выбранной записи
        record_id = self.data_tree.item(selected_item, "text")

        # Подтверждение удаления записи
        confirm = messagebox.askyesno("Подтвердить", "Вы уверены, что хотите удалить эту запись?")
        if confirm:
            # Удаление записи из базы данных
            with self.db.cursor() as cursor:
                cursor.execute("DELETE FROM your_table WHERE id=%s", (record_id,))
                self.db.commit()

            # Обновление таблицы
            self.refresh_table()


root = tk.Tk()
app = DatabaseApp(root)
root.mainloop()

"""
    print(code)

if __name__ == "__main__":
    display_code()

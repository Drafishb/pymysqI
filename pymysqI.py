def display_code():
    code = """
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pymysql

def fetch_data(table_name, connection):
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {table_name}")
            return cursor.fetchall()
    except pymysql.Error as e:
        print(f"Ошибка при выполнении запроса к базе данных: {e}")
        return []

def insert_data(table_name, values, connection):
    try:
        with connection.cursor() as cursor:
            placeholders = ', '.join(['%s'] * len(values))
            cursor.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", values)
            connection.commit()
            print("Данные успешно добавлены в таблицу.")
            return True
    except pymysql.Error as e:
        print(f"Ошибка при вставке данных в таблицу: {e}")
        return False

def delete_data(table_name, primary_key_value, connection):
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM {table_name} WHERE {table_name}_INT=%s", (primary_key_value,))
            connection.commit()
            print("Запись успешно удалена.")
            return True
    except pymysql.Error as e:
        print(f"Ошибка при удалении записи из таблицы: {e}")
        return False

def update_data(table_name, columns, primary_key_value, new_values, connection):
    try:
        with connection.cursor() as cursor:
            placeholders = ', '.join([f"{col}=%s" for col in columns])
            cursor.execute(f"UPDATE {table_name} SET {placeholders} WHERE {table_name}_INT=%s", (*new_values, primary_key_value))
            connection.commit()
            print("Запись успешно обновлена.")
            return True
    except pymysql.Error as e:
        print(f"Ошибка при обновлении записи в таблице: {e}")
        return False

def update_table(treeview, table_name, connection):
    treeview.delete(*treeview.get_children())
    new_data = fetch_data(table_name, connection)
    for row in new_data:
        treeview.insert("", "end", values=row)

def add_record_dialog(table_name, connection, treeview):
    dialog = tk.Toplevel()
    dialog.title("Добавление записи")

    entry_frame = ttk.Frame(dialog, padding="10")
    entry_frame.pack()

    with connection.cursor() as cursor:
        cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        columns = [col[0] for col in cursor.fetchall()]

    entry_fields = []
    for i, col in enumerate(columns):
        ttk.Label(entry_frame, text=col).grid(row=i, column=0, sticky="e")
        entry_field = ttk.Entry(entry_frame)
        entry_field.grid(row=i, column=1, padx=5, pady=5)
        entry_fields.append(entry_field)

    def insert_record():
        values = [entry.get() for entry in entry_fields]
        if insert_data(table_name, values, connection):
            messagebox.showinfo("Успех", "Запись успешно добавлена.")
            dialog.destroy()
            update_table(treeview, table_name, connection)

    ttk.Button(entry_frame, text="Добавить", command=insert_record).grid(row=len(columns), columnspan=2, pady=10)

def delete_record(treeview, table_name, connection):
    selected_item = treeview.selection()[0]
    values = treeview.item(selected_item)['values']
    primary_key_value = values[0]  # Предполагаем, что первый столбец - это ваш primary key
    if delete_data(table_name, primary_key_value, connection):
        messagebox.showinfo("Успех", "Запись успешно удалена.")
        update_table(treeview, table_name, connection)

def edit_record_dialog(table_name, connection, treeview):
    selected_item = treeview.selection()[0]
    values = treeview.item(selected_item)['values']
    primary_key_value = values[0]  # Предполагаем, что первый столбец - это ваш primary key

    dialog = tk.Toplevel()
    dialog.title("Редактирование записи")

    entry_frame = ttk.Frame(dialog, padding="10")
    entry_frame.pack()

    with connection.cursor() as cursor:
        cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        columns = [col[0] for col in cursor.fetchall()]

    entry_fields = []
    for i, col in enumerate(columns):
        ttk.Label(entry_frame, text=col).grid(row=i, column=0, sticky="e")
        entry_field = ttk.Entry(entry_frame)
        entry_field.grid(row=i, column=1, padx=5, pady=5)
        entry_field.insert(0, str(values[i]))  # Заполняем текущим значением
        entry_fields.append(entry_field)

    def update_record():
        new_values = [entry.get() for entry in entry_fields]
        if update_data(table_name, columns, primary_key_value, new_values, connection):
            messagebox.showinfo("Успех", "Запись успешно обновлена.")
            dialog.destroy()
            update_table(treeview, table_name, connection)

    ttk.Button(entry_frame, text="Сохранить", command=update_record).grid(row=len(columns), columnspan=2, pady=10)

def main():
    host = 'localhost'
    user = 'root'
    database = 'TestBD'

    connection = pymysql.connect(host=host, user=user, database=database)

    root = tk.Tk()
    root.title("Данные из базы данных")

    # Устанавливаем размер окна
    window_width = 800
    window_height = 600
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    root.resizable(False, False)

    canvas = tk.Canvas(root)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    table_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=table_frame, anchor="nw")

    data_test1 = fetch_data("Table1", connection)
    data_test2 = fetch_data("Table2", connection)
    data_test3 = fetch_data("Table3", connection)

    def display_data(frame, data, table_name):
        table_subframe = ttk.Frame(frame)
        table_subframe.pack(pady=5)

        ttk.Label(table_subframe, text=f"Таблица {table_name}").pack()

        tree = ttk.Treeview(table_subframe, columns=data[0], show="headings")
        for col in data[0]:
            tree.heading(col, text=col)
        for row in data:
            tree.insert("", "end", values=row)
        tree.pack(side="left", fill="both")

        scrollbar = ttk.Scrollbar(table_subframe, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.config(yscrollcommand=scrollbar.set)

        buttons_frame = ttk.Frame(frame)
        buttons_frame.pack()

        def open_dialog():
            add_record_dialog(table_name, connection, tree)

        ttk.Button(buttons_frame, text="Добавить запись", command=open_dialog).pack(side="left", padx=5)

        def edit_record():
            if not tree.selection():
                return
            edit_record_dialog(table_name, connection, tree)

        ttk.Button(buttons_frame, text="Редактировать запись", command=edit_record).pack(side="left", padx=5)

        def delete_record_wrapper():
            if not tree.selection():
                return
            delete_record(tree, table_name, connection)

        ttk.Button(buttons_frame, text="Удалить запись", command=delete_record_wrapper).pack(side="left", padx=5)

    if data_test1:
        display_data(table_frame, data_test1, "Table1")

    if data_test2:
        display_data(table_frame, data_test2, "Table2")

    if data_test3:
        display_data(table_frame, data_test3, "Table3")

    root.mainloop()

if __name__ == "__main__":
    main()

"""
    print(code)

if __name__ == "__main__":
    display_code()

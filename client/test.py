import customtkinter as ctk
from tkinter import messagebox


class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Вход")
        self.geometry("400x450")
        self.title_label = ctk.CTkLabel(self, text="Введите данные для входа", font=("Arial", 16))
        self.title_label.pack(pady=10)

        self.master_password_label = ctk.CTkLabel(self, text="Мастер-пароль:")
        self.master_password_label.pack(pady=5)
        self.master_password_entry = ctk.CTkEntry(self, show="*")
        self.master_password_entry.pack(pady=5)

        self.server_ip_label = ctk.CTkLabel(self, text="IP-адрес сервера:")
        self.server_ip_label.pack(pady=5)
        self.server_ip_entry = ctk.CTkEntry(self)
        self.server_ip_entry.pack(pady=5)

        self.server_login_label = ctk.CTkLabel(self, text="Логин:")
        self.server_login_label.pack(pady=5)
        self.server_login_entry = ctk.CTkEntry(self)
        self.server_login_entry.pack(pady=5)

        self.server_password_label = ctk.CTkLabel(self, text="Пароль:")
        self.server_password_label.pack(pady=5)
        self.server_password_entry = ctk.CTkEntry(self, show="*")
        self.server_password_entry.pack(pady=5)

        self.login_button = ctk.CTkButton(self, text="Войти", command=self.verify_login)
        self.login_button.pack(pady=20)

    def verify_login(self):
        master_password = self.master_password_entry.get()
        ip_address = self.server_ip_entry.get()
        server_login = self.server_login_entry.get()
        server_password = self.server_password_entry.get()

        if master_password == "1234" and ip_address and server_login and server_password:
            self.destroy()
            app = PasswordManagerApp(ip_address, server_login)
            app.mainloop()
        else:
            messagebox.showerror("Ошибка", "Некорректные данные или пустые поля")


# Главное приложение
class PasswordManagerApp(ctk.CTk):
    def __init__(self, ip_address, server_login):
        super().__init__()
        self.title("Менеджер паролей")
        self.geometry("600x400")

        # Верхний заголовок
        self.server_info_label = ctk.CTkLabel(self, text=f"Подключено к {ip_address} как {server_login}")
        self.server_info_label.pack(pady=10)

        # Основной фрейм
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Секция полей ввода (слева)
        self.input_frame = ctk.CTkFrame(self.main_frame)
        self.input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.site_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Сайт")
        self.site_entry.pack(pady=5, padx=5)

        self.login_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Логин")
        self.login_entry.pack(pady=5, padx=5)

        self.password_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Пароль")
        self.password_entry.pack(pady=5, padx=5)

        # Секция кнопок (справа)
        self.button_frame = ctk.CTkFrame(self.main_frame)
        self.button_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.add_button = ctk.CTkButton(self.button_frame, text="Добавить пароль", command=self.add_password)
        self.add_button.pack(pady=10, padx=5)

        self.delete_button = ctk.CTkButton(self.button_frame, text="Удалить пароль", command=self.delete_password)
        self.delete_button.pack(pady=10, padx=5)

        # Список паролей
        self.password_listbox = ctk.CTkTextbox(self, height=200, width=580)
        self.password_listbox.pack(pady=10)

        # Хранилище паролей
        self.passwords = []

    def update_password_list(self):
        self.password_listbox.delete("1.0", "end")
        for site, login, password in self.passwords:
            self.password_listbox.insert("end", f"{site} | {login} | {password}\n")

    def add_password(self):
        site = self.site_entry.get()
        login = self.login_entry.get()
        password = self.password_entry.get()

        if site and login and password:
            self.passwords.append((site, login, password))
            self.update_password_list()
            self.site_entry.delete(0, "end")
            self.login_entry.delete(0, "end")
            self.password_entry.delete(0, "end")
        else:
            messagebox.showwarning("Ошибка", "Заполните все поля")

    def delete_password(self):
        selected_text = self.password_listbox.get("1.0", "end").strip()
        if selected_text:
            lines = selected_text.split("\n")
            if lines:
                last_line = lines[-1]
                if last_line:
                    site, login, password = last_line.split(" | ")
                    self.passwords = [p for p in self.passwords if p != (site, login, password)]
                    self.update_password_list()
        else:
            messagebox.showwarning("Ошибка", "Список пуст")


if __name__ == "__main__":
    login_app = LoginWindow()
    login_app.mainloop()

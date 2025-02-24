import customtkinter as ctk
from tkinter import messagebox
import utils


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

        self.server_ip_label = ctk.CTkLabel(self, text="IP сервера:")
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

        self.login_button = ctk.CTkButton(self, text="Войти", command=self.login)
        self.login_button.pack(pady=20)

    def login(self):
        master_password = self.master_password_entry.get()
        ip = self.server_ip_entry.get()
        server_login = self.server_login_entry.get()
        server_password = self.server_password_entry.get()

        if master_password and ip and server_login and server_password and utils.ping_server(ip):
            token = utils.login_user(ip, server_login, server_password)
            if token in ["Register error", "Incorrect password"]:
                messagebox.showerror("Ошибка", "Проверьте данные и пароль!")
            self.destroy()
            app = PasswordManagerApp(ip, server_login, server_password, master_password, token)
            app.mainloop()
        else:
            messagebox.showerror("Ошибка", "Проверьте данные и статус сервера")


class PasswordManagerApp(ctk.CTk):
    def __init__(self, ip, login, password, masterKey, token):
        super().__init__()
        self.ip = ip
        self.login = login
        self.password = password
        self.token = token
        self.masterKey = masterKey



        self.title("Менеджер паролей")
        self.geometry("600x400")

        self.server_info_label = ctk.CTkLabel(self, text=f"Подключено к {ip} как {login}")
        self.server_info_label.pack(pady=10)

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.input_frame = ctk.CTkFrame(self.main_frame)
        self.input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.site_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Сервис")
        self.site_entry.pack(pady=5, padx=5)

        self.login_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Логин")
        self.login_entry.pack(pady=5, padx=5)

        self.password_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Пароль")
        self.password_entry.pack(pady=5, padx=5)

        self.button_frame = ctk.CTkFrame(self.main_frame)
        self.button_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.add_button = ctk.CTkButton(self.button_frame, text="Добавить пароль", command=self.add_password)
        self.add_button.pack(pady=10, padx=5)

        self.delete_button = ctk.CTkButton(self.button_frame, text="Удалить пароль", command=self.delete_password)
        self.delete_button.pack(pady=10, padx=5)

        self.password_listbox = ctk.CTkTextbox(self, height=200, width=580)
        self.password_listbox.pack(pady=10)

        self.passwords = []
        self.load_passwords()

    def update_password_list(self):
        self.password_listbox.delete("1.0", "end")
        for site, login, password in self.passwords:
            self.password_listbox.insert("end", f"{site} | {login} | {password}\n")

    def add_password(self):
        site = self.site_entry.get()
        login = self.login_entry.get()
        password = self.password_entry.get()

        if site and login and password:
            password = utils.encrypt_password(self.masterKey, password)
            if not utils.check_token(self.ip, self.token):
                self.token = utils.login_user(self.ip, self.login, self.password)
            utils.add_password(self.ip, self.token, site, login, password)
            self.site_entry.delete(0, "end")
            self.login_entry.delete(0, "end")
            self.password_entry.delete(0, "end")
            self.load_passwords()
        else:
            messagebox.showwarning("Ошибка", "Заполните все поля")

    def delete_password(self):
        if not utils.check_token(self.ip, self.token):
            self.token = utils.login_user(self.ip, self.login, self.password)
        site = self.site_entry.get()
        self.site_entry.delete(0, "end")
        if site in utils.get_passwords(self.ip, self.token).keys():
            utils.delete_password(self.ip, self.token ,site)
            self.load_passwords()
        else:
            messagebox.showwarning("Ошибка", "Список пуст")

    def load_passwords(self):
        self.passwords = []
        if not utils.check_token(self.ip, self.token):
            self.token = utils.login_user(self.ip, self.login, self.password)
        passw = utils.get_passwords(self.ip, self.token)
        key = passw.keys()
        for site in key:
            login = passw[site][0]
            password = passw[site][1]
            password = utils.decrypt_password(self.masterKey, password)
            self.passwords.append((site, login, password))
            self.update_password_list()
        self.update_password_list()


if __name__ == "__main__":
    login_app = LoginWindow()
    login_app.mainloop()

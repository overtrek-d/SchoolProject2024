import psycopg2
from psycopg2 import sql
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, db_name, user, password, host, port):
        self.db_name = db_name
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection = None

    def connect(self):
        try:
            self.connection = psycopg2.connect(
                dbname=self.db_name, user=self.user, password=self.password, host=self.host, port=self.port
            )
            self.connection.autocommit = True
            logging.info("Connected to the database '%s'.", self.db_name)

        except psycopg2.OperationalError:
            logging.warning("Database '%s' not found. Attempting to create it.", self.db_name)

            temp_conn = psycopg2.connect(
                dbname='postgres', user=self.user, password=self.password, host=self.host, port=self.port
            )
            temp_conn.autocommit = True
            cursor = temp_conn.cursor()
            cursor.execute(sql.SQL("CREATE DATABASE {};").format(sql.Identifier(self.db_name)))
            cursor.close()
            temp_conn.close()

            self.connection = psycopg2.connect(
                dbname=self.db_name, user=self.user, password=self.password, host=self.host, port=self.port
            )
            self.connection.autocommit = True

    def create_tables(self):
        users_table = """
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            login VARCHAR(255) NOT NULL,
            hash_password TEXT NOT NULL
        );
        """

        passwords_table = """
        CREATE TABLE IF NOT EXISTS passwords (
            password_id SERIAL PRIMARY KEY,
            owner_id INT NOT NULL REFERENCES users(user_id),
            service VARCHAR(255) NOT NULL,
            service_login VARCHAR(255) NOT NULL,
            service_password TEXT NOT NULL
        );
        """

        with self.connection.cursor() as cursor:
            cursor.execute(users_table)
            cursor.execute(passwords_table)

    def execute_query(self, query, params=None):
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)

    def fetch_query(self, query, params=None):
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    def register_user(self, login: str, password: str):
        query = """
        INSERT INTO users (login, hash_password) VALUES (%s, %s);
        """

        self.execute_query(query, (login, password))
        logging.info("User '%s' registered successfully with user_id %d.", login)
        return None

    def login_user(self, login, hash_password):
        query_user_exists = """
        SELECT hash_password FROM users WHERE login = %s;
        """
        result = self.fetch_query(query_user_exists, (login,))

        if not result:
            logging.warning("Login attempt failed: user '%s' not found.", login)
            return "User not found"

        stored_hash_password = result[0][0]
        if stored_hash_password != hash_password:
            logging.warning("Login attempt failed: incorrect password for user '%s'.", login)
            return "Incorrect password"

        query_get_user_id = """
        SELECT user_id FROM users WHERE login = %s AND hash_password = %s;
        """
        user_id = self.fetch_query(query_get_user_id, (login, hash_password))[0][0]
        logging.info("User '%s' logged in successfully with user_id %d.", login, user_id)
        return user_id

    def get_user_passwords(self, user_id: int): # {service: [login, password]}
        query = """
        SELECT service, service_login, service_password 
        FROM passwords WHERE owner_id = %s;
        """
        passwords = self.fetch_query(query, (user_id,))
        passwords_dict = {service: [service_login, service_password] for service, service_login, service_password in passwords}
        logging.info("Fetched %d passwords for user_id %d.", len(passwords), user_id)
        return passwords_dict

    def close_connection(self):
        if self.connection:
            self.connection.close()
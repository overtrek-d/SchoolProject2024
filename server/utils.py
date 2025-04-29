import logging
from Crypto.Hash import SHA256
import requests
import yaml
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64
import os

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")


def config_load():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

def hash(value: str):
    return SHA256.new(value.encode('utf-8')).hexdigest()


def ping_server(ip):
    try:
        url = "http://" + str(ip) + "/ping"
        headers = {"accept": "application/json"}
        response = requests.get(url, headers=headers)
        if response.text == '"Pong"' and response.status_code == 200:
            return True
        else:
            return False
    except:
        return False

def check_token(ip, token) -> bool:
    try:
        url = "http://" + str(ip) + "/token/check"
        headers = {"accept": "application/json"}
        params = {"token": token}
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200 and response.text == '"OK"':
            return True
        else:
            return False
    except:
        return False

def register_user(ip, login, password) -> bool:
    url = "http://" + str(ip) + "/user/register"
    headers = {"accept": "application/json"}
    params = {"username": login, "password": password}
    response = requests.post(url, headers=headers, params=params)
    if response.text == '"Success"' and response.status_code == 200:
        return True
    else:
        return False

def login_user(ip, login, password) -> str:
    url = "http://" + str(ip) + "/user/login"
    headers = {"accept": "application/json", "Content-Type": "application/x-www-form-urlencoded",}
    data = {"grant_type": "password", "username": login, "password": password}
    response = requests.post(url, headers=headers, data=data)
    if response.text == '"User not found"':
        if register_user(ip, login, password):
            login_user(ip, login, password)
        else:
            return "Register error"
    elif response.text == '"Incorrect password"':
        return "Incorrect password"
    else:
        if response.status_code == 200:
            try:
                return response.json().get("access_token")
            except ValueError:
                logging.error("Не удалось распарсить JSON: %s", response.text)
                return None
        else:
            logging.error("Ошибка при логине: %s - %s", response.status_code, response.text)
            return None

def get_passwords(ip, token):
    if check_token(ip, token):
        url = "http://" + str(ip) + "/password/get"
        headers = {"accept": "application/json"}
        params = {"token": token}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return False
    else:
        return False

def add_password(ip, token, service, service_loign, service_password):
    if check_token(ip, token):
        url = "http://" + str(ip) + "/password/add"
        headers = {"accept": "application/json"}
        params = {"token": token, "service": service, "login": service_loign, "password": service_password}
        responce = requests.post(url, headers=headers, params=params)
        if responce.text == '"Success"':
            return True
        else:
            return False

def delete_password(ip, token, service):
    if check_token(ip, token):
        url = "http://" + str(ip) + "/password/delete"
        headers = {"accept": "application/json"}
        params = {"token": token, "service": service}
        responce = requests.post(url, headers=headers, params=params)
        if responce.text == '"Success"':
            return True
        else:
            return False

def encrypt_password(master_key, password):
    key = master_key.encode()[:32].ljust(32, b'\0')
    iv = get_random_bytes(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(password.encode(), AES.block_size))
    return base64.b64encode(iv + encrypted).decode()

def decrypt_password(master_key, password):
    try:
        key = master_key.encode()[:32].ljust(32, b'\0')
        encrypted_data = base64.b64decode(password)
        iv = encrypted_data[:AES.block_size]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(encrypted_data[AES.block_size:]), AES.block_size)
        return decrypted.decode()
    except:
        return "FALED MASTERKEY"
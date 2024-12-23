import requests
import yaml
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
import base64

def load_config():
    with open("config.yaml") as f:
        return yaml.safe_load(f)

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

def pad(data):
    block_size = AES.block_size
    padding_len = block_size - len(data) % block_size
    return data + bytes([padding_len] * padding_len)

def unpad(data):
    padding_len = data[-1]
    return data[:-padding_len]

def hash(value):
    hasher = SHA256.new()
    hasher.update(value.encode('utf-8'))
    return hasher.digest()

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
        return response.json().get("access_token")

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
def encrypt_password(master_key, password):
    master_key = hash(master_key)
    cipher = AES.new(master_key, AES.MODE_CBC)
    iv = cipher.iv
    password_bytes = password.encode('utf-8')
    encrypted = cipher.encrypt(pad(password_bytes))
    return base64.b64encode(iv + encrypted).decode('utf-8')

def decrypt_password(master_key, password):
    master_key = hash(master_key)
    data = base64.b64decode(password)
    iv = data[:AES.block_size]
    encrypted = data[AES.block_size:]
    cipher = AES.new(master_key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(encrypted))
    return decrypted.decode('utf-8')


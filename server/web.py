import uvicorn
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import utils
import os

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")),
    name="static"
)
templates = Jinja2Templates(directory="/app/server/templates")

SERVER_IP = "main_api:8000"

@app.get("/", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login", response_class=HTMLResponse)
def login(request: Request, username: str = Form(...), password: str = Form(...), master_key: str = Form(...)):
    token = utils.login_user(SERVER_IP, username, password)
    if token in ["Register error", "Incorrect password"]:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Неверный логин или пароль."})
    response = RedirectResponse("/dashboard", status_code=302)
    response.set_cookie("token", token)
    response.set_cookie("username", username)
    response.set_cookie("password", password)
    response.set_cookie("master_key", master_key)
    return response

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    token = request.cookies.get("token")
    username = request.cookies.get("username")
    password = request.cookies.get("password")
    master_key = request.cookies.get("master_key")
    if not utils.check_token(SERVER_IP, token):
        token = utils.login_user(SERVER_IP, username, password)
    raw_data = utils.get_passwords(SERVER_IP, token)
    passwords = []
    for site, creds in raw_data.items():
        login, enc_pass = creds
        password = utils.decrypt_password(master_key, enc_pass)
        passwords.append({"site": site, "login": login, "password": password})
    return templates.TemplateResponse("dashboard.html", {"request": request, "passwords": passwords, "username": username})

@app.post("/add-password", response_class=HTMLResponse)
def add_password(request: Request, service: str = Form(...), login: str = Form(...), password: str = Form(...)):
    token = request.cookies.get("token")
    username = request.cookies.get("username")
    user_password = request.cookies.get("password")
    master_key = request.cookies.get("master_key")
    if not utils.check_token(SERVER_IP, token):
        token = utils.login_user(SERVER_IP, username, user_password)
    encrypted = utils.encrypt_password(master_key, password)
    utils.add_password(SERVER_IP, token, service, login, encrypted)
    return RedirectResponse("/dashboard", status_code=302)

@app.post("/delete-password", response_class=HTMLResponse)
def delete_password(request: Request, service: str = Form(...)):
    token = request.cookies.get("token")
    username = request.cookies.get("username")
    password = request.cookies.get("password")
    if not utils.check_token(SERVER_IP, token):
        token = utils.login_user(SERVER_IP, username, password)
    utils.delete_password(SERVER_IP, token, service)
    return RedirectResponse("/dashboard", status_code=302)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
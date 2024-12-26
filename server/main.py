from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from db_manager import DatabaseManager
import utils
import logging
import jwt
import uvicorn

logger = logging.getLogger(__name__)

config = utils.config_load()
TOKEN_TIME = 30

try:
    db = DatabaseManager(db_name=config["dataBaseName"], user=config["dataBaseUser"], password=config["dataBasePassword"],
                     host=config["dataBaseHost"], port=config["dataBasePort"])
    db.connect()
    db.create_tables()
    logger.info("Connect to database")
except Exception as e:
    logger.error("Faled connect to database", e)
    exit(0)

app = FastAPI()

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=TOKEN_TIME)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config["tokenAPIKey"], algorithm="HS256")
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, config["tokenAPIKey"], algorithms="HS256")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/ping")
def ping():
    return "Pong"

@app.get("/token/check")
def check_token(token: str):
    if not token:
        return "BADTOKEN"

    try:
        verify_token(token)
        return "OK"
    except HTTPException as e:
        return "BADTOKEN"


@app.post("/user/login", tags=["User"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user_check = db.login_user(login=form_data.username, hash_password=utils.hash(form_data.password))
    match user_check:
        case "User not found":
            return "User not found"
        case "Incorrect password":
            return "Incorrect password"

    access_token = create_access_token(data={"sub": form_data.username, "user_id": user_check})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/user/register", tags=["User"])
def register_user(username: str, password: str):
    password = utils.hash(password)
    if db.login_user(login=username, hash_password=password) in ["User not found", "Incorrect password"]:
        db.register_user(username, password)
        return "Success"
    return "User alredy register"

@app.get("/password/get", tags=["Password"])
def get_passwords(token: str):
    payload = verify_token(token)
    user_id = payload.get("user_id")
    return db.get_user_passwords(user_id)

@app.post("/password/add", tags=["Password"])
def add_password(token: str , service, login, password):
    payload = verify_token(token)
    user_id = payload.get("user_id")
    db.add_password(user_id, service, login, password)
    return "Success"

@app.post("/password/delete", tags=["Password"])
def delete_password(token: str, service):
    payload = verify_token(token)
    user_id = payload.get("user_id")
    db.delete_password(user_id, service)
    return "Success"


if __name__ == "__main__":
    uvicorn.run(app, port=config["portAPI"])


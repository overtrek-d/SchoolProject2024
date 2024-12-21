from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from pydantic import BaseModel
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

app = FastAPI()

class User(BaseModel):
    user_id: int
    login: str
    hash_password: str
class Password(BaseModel):
    password_id: int
    owner_id: int
    service: str
    service_login: str
    service_password: str

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


@app.post("/user/login")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user_check = db.login_user(login=form_data.username, hash_password=utils.hash(form_data.password))
    match user_check:
        case "User not found":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        case "Incorrect password":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password",
                headers={"WWW-Authenticate": "Bearer"},
            )

    access_token = create_access_token(data={"sub": form_data.username, "user_id": user_check})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/user/register")
def register_user(username: str, password: str):
    password = utils.hash(password)
    if db.login_user(login=username, hash_password=password) in ["User not found", "Incorrect password"]:
        db.register_user(username, password)
        return "Success"
    return "User alredy register"

@app.get("/password/get")
def get_password(token: str = Depends(OAuth2PasswordBearer(tokenUrl="token"))):
    payload = verify_token(token)
    user_id = payload.get("user_id")
    return db.get_user_passwords(user_id)

if __name__ == "__main__":
    uvicorn.run(app, port=55535)

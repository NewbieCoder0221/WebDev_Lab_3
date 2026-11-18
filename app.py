import hashlib
import hmac
import secrets

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from database import create_db_and_tables, engine
from models import Account, LoginRequest, RegisterRequest, Users


# This uses Python's built-in PBKDF2 password hashing.
# A different random salt is generated for every registered account.
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
    ).hex()
    return f"{salt}${password_hash}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, saved_hash = stored_hash.split("$", 1)
        new_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
        ).hex()
        return hmac.compare_digest(new_hash, saved_hash)
    except ValueError:
        return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

# Allows the HTML pages opened with a local development server to contact FastAPI.
origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "null",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "Monster Hunter Survey API is running."}


@app.post("/register")
def register_account(account_data: RegisterRequest):
    username = account_data.username.strip()
    password = account_data.password

    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password are required.")
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")

    with Session(engine) as session:
        statement = select(Account).where(Account.username == username)
        existing_account = session.exec(statement).first()

        if existing_account:
            raise HTTPException(status_code=409, detail="Username is already registered.")

        new_account = Account(
            username=username,
            password_hash=hash_password(password),
        )
        session.add(new_account)
        session.commit()

    return {"status": "success", "message": "Account registered successfully."}


@app.post("/usersLogin")
def login_account(login_data: LoginRequest):
    username = login_data.username.strip()

    with Session(engine) as session:
        statement = select(Account).where(Account.username == username)
        account = session.exec(statement).first()

        if account is None or not verify_password(login_data.password, account.password_hash):
            raise HTTPException(status_code=401, detail="Incorrect username or password.")

    return {"status": "success", "message": "Login successful."}


# This endpoint saves the Monster Hunter survey answers from index.html.
@app.post("/users")
def save_survey(survey: Users):
    with Session(engine) as session:
        session.add(survey)
        session.commit()
        session.refresh(survey)
        return {"status": "success", "message": "Survey submitted successfully.", "id": survey.id}


@app.get("/users/{user_id}")
def read_survey(user_id: int):
    with Session(engine) as session:
        survey = session.get(Users, user_id)
        if survey is None:
            raise HTTPException(status_code=404, detail="Survey response not found.")
        return survey

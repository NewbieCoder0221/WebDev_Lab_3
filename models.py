from sqlmodel import Field, SQLModel


# This table stores the answers submitted through index.html.
class Users(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user: str
    gender: str
    weapon: str
    armor: str
    element: str
    level: int
    least_favorite_monster: str
    most_favorite_monster: str
    hunts_done: int
    Ruger_Aidal_Kill_Confirm: str


# This separate table stores login accounts.
# The password_hash field contains a hashed password, never the original password.
class Account(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password_hash: str


# These models describe the data received from the HTML pages.
# They are not database tables.
class RegisterRequest(SQLModel):
    username: str
    password: str


class LoginRequest(SQLModel):
    username: str
    password: str

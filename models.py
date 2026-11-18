from sqlmodel import Field , SQLModel

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

class user(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    user: str
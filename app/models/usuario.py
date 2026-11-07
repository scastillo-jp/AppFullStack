from sqlmodel import SQLModel, Field

class Usuario(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(
        min_length=3,
        max_length=50,
        unique=True,
        index=True
    )
    email: str | None = Field(default=None, max_length=254, unique=True, index=True)
    hashed_password:str
from typing import Annotated

from pydantic import StringConstraints
from sqlmodel import SQLModel, Field

EmailAddress = Annotated[
    str,
    StringConstraints(
        min_length=6,
        max_length=254,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    )
]

class UsuarioCreate(SQLModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailAddress
    password: str = Field(min_length=8)

class UsuarioRead(SQLModel):
    id: int
    username: str
    email: EmailAddress | None

class Token(SQLModel):
    access_token: str
    token_type: str
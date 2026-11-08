from typing import Annotated, Literal

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
    email: EmailAddress
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=2, max_length=100)
    cedula: str = Field(min_length=5, max_length=20)
    address: str = Field(min_length=5, max_length=250)
    city: str = Field(min_length=2, max_length=100)
    phone: str = Field(min_length=7, max_length=30)
    role: Literal["administrador", "cliente"] = "cliente"

class UsuarioRead(SQLModel):
    id: int
    username: str
    email: EmailAddress | None
    full_name: str | None
    cedula: str | None
    address: str | None
    city: str | None
    phone: str | None
    role: str

class UsuarioUpdate(SQLModel):
    email: EmailAddress | None = None
    full_name: str | None = Field(default=None, min_length=2, max_length=100)
    cedula: str | None = Field(default=None, min_length=5, max_length=20)
    address: str | None = Field(default=None, min_length=5, max_length=250)
    city: str | None = Field(default=None, min_length=2, max_length=100)
    phone: str | None = Field(default=None, min_length=7, max_length=30)

class Token(SQLModel):
    access_token: str
    token_type: str
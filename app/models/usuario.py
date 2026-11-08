from sqlmodel import SQLModel, Field

ROLES = ["administrador", "cliente"]
ROL_ADMINISTRADOR = ROLES[0]


class Usuario(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(
        min_length=3,
        max_length=50,
        unique=True,
        index=True
    )
    email: str | None = Field(default=None, max_length=254, unique=True, index=True)
    hashed_password: str
    full_name: str | None = Field(default=None, max_length=100)
    cedula: str | None = Field(default=None, max_length=20, unique=True, index=True)
    address: str | None = Field(default=None, max_length=250)
    city: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=30)
    role: str = Field(default=ROLES[1], max_length=20, index=True)
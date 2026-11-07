from sqlmodel import SQLModel, Field

class Producto(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=300)
    price: float = Field(gt=0)
    stock: int = Field(default=0, ge=0)
    user_id: int = Field(foreign_key="usuario.id", index=True)
from sqlmodel import Field, SQLModel


class CarritoItemCreate(SQLModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(default=1, ge=1)


class CarritoItemUpdate(SQLModel):
    quantity: int = Field(ge=1)

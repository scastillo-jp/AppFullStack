from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class Carrito(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("user_id", name="uq_carrito_user"),)

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="usuario.id", index=True)


class CarritoItem(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("cart_id", "product_id", name="uq_carrito_item_product"),
    )

    id: int | None = Field(default=None, primary_key=True)
    cart_id: int = Field(foreign_key="carrito.id", index=True)
    product_id: int = Field(foreign_key="producto.id", index=True)
    quantity: int = Field(gt=0)

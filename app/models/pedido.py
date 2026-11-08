from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import Numeric
from sqlmodel import Field, SQLModel


class Pedido(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="usuario.id", index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        index=True
    )
    status: str = Field(default="pendiente", index=True, max_length=20)
    payment_status: str = Field(default="pagado", max_length=20)
    total: Decimal = Field(sa_type=Numeric(10, 2), ge=0)
    full_name: str
    address: str
    city: str
    phone: str


class PedidoItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="pedido.id", index=True)
    product_id: int | None = Field(default=None, foreign_key="producto.id")
    product_name: str = Field(max_length=100)
    image_path: str | None = Field(default=None, max_length=500)
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(sa_type=Numeric(10, 2), ge=0)

from datetime import datetime
from decimal import Decimal
from typing import Literal

from sqlmodel import SQLModel


class PedidoItemRead(SQLModel):
    id: int
    product_id: int | None
    product_name: str
    image_path: str | None
    quantity: int
    unit_price: Decimal


class PedidoRead(SQLModel):
    id: int
    created_at: datetime
    status: str
    payment_status: str
    total: Decimal
    full_name: str
    address: str
    city: str
    phone: str
    items: list[PedidoItemRead]


class PedidoEstadoUpdate(SQLModel):
    status: Literal["procesando", "enviado", "entregado"]

from decimal import Decimal

from sqlalchemy import update
from sqlmodel import select

from app.core.money import quantize_money
from app.models.carrito import Carrito, CarritoItem
from app.models.pedido import Pedido, PedidoItem
from app.models.producto import Producto
from app.models.usuario import Usuario
from app.schemas.pedido import PedidoEstadoUpdate


def _serialize_order(order: Pedido, session):
    items = session.exec(
        select(PedidoItem)
        .where(PedidoItem.order_id == order.id)
        .order_by(PedidoItem.id)
    ).all()
    return {
        "id": order.id,
        "created_at": order.created_at,
        "status": order.status,
        "payment_status": order.payment_status,
        "total": order.total,
        "full_name": order.full_name,
        "address": order.address,
        "city": order.city,
        "phone": order.phone,
        "items": items,
    }


def create_order(user: Usuario, session):
    if not all((user.full_name, user.address, user.city, user.phone)):
        raise ValueError("Completa tu nombre y dirección antes de realizar la compra")

    cart = session.exec(
        select(Carrito).where(Carrito.user_id == user.id)
    ).first()
    if cart is None:
        raise ValueError("El carrito está vacío")

    rows = session.exec(
        select(CarritoItem, Producto)
        .join(Producto, CarritoItem.product_id == Producto.id)
        .where(CarritoItem.cart_id == cart.id)
    ).all()
    if not rows:
        raise ValueError("El carrito está vacío")
    for item, product in rows:
        if item.quantity > product.stock:
            raise ValueError(
                f"Inventario insuficiente para el producto {product.name}"
            )

    total = sum(
        (
            quantize_money(product.price) * item.quantity
            for item, product in rows
        ),
        Decimal("0")
    )
    order = Pedido(
        user_id=user.id,
        total=total,
        full_name=user.full_name,
        address=user.address,
        city=user.city,
        phone=user.phone,
        status="pendiente",
        payment_status="pagado",
    )
    session.add(order)
    session.flush()

    for item, product in rows:
        unit_price = quantize_money(product.price)
        stock_update = session.exec(
            update(Producto)
            .where(
                Producto.id == product.id,
                Producto.stock >= item.quantity
            )
            .values(stock=Producto.stock - item.quantity)
            .execution_options(synchronize_session=False)
        )
        if stock_update.rowcount != 1:
            session.rollback()
            raise ValueError(
                f"Inventario insuficiente para el producto {product.name}"
            )
        session.add(
            PedidoItem(
                order_id=order.id,
                product_id=product.id,
                product_name=product.name,
                image_path=product.image_path,
                quantity=item.quantity,
                unit_price=unit_price,
            )
        )
        session.delete(item)

    session.commit()
    session.refresh(order)
    return _serialize_order(order, session)


def get_orders(user_id: int | None, session):
    query = select(Pedido).order_by(Pedido.created_at.desc())
    if user_id is not None:
        query = query.where(Pedido.user_id == user_id)
    return [_serialize_order(order, session) for order in session.exec(query).all()]


def get_order(order_id: int, user_id: int | None, session):
    query = select(Pedido).where(Pedido.id == order_id)
    if user_id is not None:
        query = query.where(Pedido.user_id == user_id)
    order = session.exec(query).first()
    return _serialize_order(order, session) if order else None


def update_order_status(
    order_id: int,
    status_data: PedidoEstadoUpdate,
    session
):
    order = session.get(Pedido, order_id)
    if order is None:
        return None
    next_status = {
        "pendiente": "procesando",
        "procesando": "enviado",
        "enviado": "entregado",
    }.get(order.status)
    if status_data.status != next_status:
        raise ValueError("El estado debe avanzar en el orden establecido")
    order.status = status_data.status
    session.add(order)
    session.commit()
    session.refresh(order)
    return _serialize_order(order, session)

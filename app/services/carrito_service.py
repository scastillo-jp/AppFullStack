from sqlmodel import select

from app.core.money import quantize_money
from app.models.carrito import Carrito, CarritoItem
from app.models.categoria import Categoria
from app.models.producto import Producto


def _get_or_create_cart(user_id: int, session):
    cart = session.exec(
        select(Carrito).where(Carrito.user_id == user_id)
    ).first()
    if cart is None:
        cart = Carrito(user_id=user_id)
        session.add(cart)
        session.commit()
        session.refresh(cart)
    return cart


def get_cart(user_id: int, session):
    cart = _get_or_create_cart(user_id, session)
    rows = session.exec(
        select(CarritoItem, Producto, Categoria)
        .join(Producto, CarritoItem.product_id == Producto.id)
        .outerjoin(Categoria, Producto.category_id == Categoria.id)
        .where(CarritoItem.cart_id == cart.id)
    ).all()
    items = []
    for item, product, category in rows:
        unit_price = quantize_money(product.price)
        items.append({
            "id": item.id,
            "product_id": product.id,
            "name": product.name,
            "image_path": product.image_path,
            "category_name": category.name if category else None,
            "price": float(unit_price),
            "stock": product.stock,
            "quantity": item.quantity,
            "subtotal": float(unit_price * item.quantity),
        })
    return {
        "id": cart.id,
        "items": items,
        "item_count": sum(item["quantity"] for item in items),
        "total": float(sum(
            (quantize_money(item["subtotal"]) for item in items),
            quantize_money(0)
        )),
    }


def add_item(user_id: int, product_id: int, quantity: int, session):
    product = session.get(Producto, product_id)
    if product is None:
        raise LookupError("Producto no encontrado")
    if product.stock < quantity:
        raise ValueError("La cantidad solicitada supera el inventario disponible")

    cart = _get_or_create_cart(user_id, session)
    item = session.exec(
        select(CarritoItem).where(
            CarritoItem.cart_id == cart.id,
            CarritoItem.product_id == product_id
        )
    ).first()
    new_quantity = quantity + (item.quantity if item else 0)
    if new_quantity > product.stock:
        raise ValueError("La cantidad solicitada supera el inventario disponible")
    if item:
        item.quantity = new_quantity
    else:
        item = CarritoItem(
            cart_id=cart.id,
            product_id=product_id,
            quantity=quantity
        )
    session.add(item)
    session.commit()
    return get_cart(user_id, session)


def update_item(user_id: int, item_id: int, quantity: int, session):
    cart = _get_or_create_cart(user_id, session)
    item = session.exec(
        select(CarritoItem).where(
            CarritoItem.id == item_id,
            CarritoItem.cart_id == cart.id
        )
    ).first()
    if item is None:
        return None
    product = session.get(Producto, item.product_id)
    if product is None:
        raise LookupError("Producto no encontrado")
    if quantity > product.stock:
        raise ValueError("La cantidad solicitada supera el inventario disponible")
    item.quantity = quantity
    session.add(item)
    session.commit()
    return get_cart(user_id, session)


def remove_item(user_id: int, item_id: int, session):
    cart = _get_or_create_cart(user_id, session)
    item = session.exec(
        select(CarritoItem).where(
            CarritoItem.id == item_id,
            CarritoItem.cart_id == cart.id
        )
    ).first()
    if item is None:
        return False
    session.delete(item)
    session.commit()
    return True

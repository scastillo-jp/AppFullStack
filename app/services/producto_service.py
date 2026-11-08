from sqlmodel import select

from app.models.categoria import Categoria
from app.models.carrito import CarritoItem
from app.models.pedido import PedidoItem
from app.models.producto import Producto
from app.schemas.producto import ProductoCreate, ProductoUpdate


def _product_data(product: Producto, category: Categoria | None):
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "stock": product.stock,
        "category_id": product.category_id,
        "category_name": category.name if category else None,
        "image_path": product.image_path,
    }


def get_products(session, search: str | None = None, category_id: int | None = None):
    query = select(Producto, Categoria).outerjoin(
        Categoria,
        Producto.category_id == Categoria.id
    )
    if search:
        query = query.where(Producto.name.ilike(f"%{search.strip()}%"))
    if category_id is not None:
        query = query.where(Producto.category_id == category_id)
    rows = session.exec(query.order_by(Producto.name)).all()
    return [_product_data(product, category) for product, category in rows]


def get_product(product_id: int, session):
    result = session.exec(
        select(Producto, Categoria)
        .outerjoin(Categoria, Producto.category_id == Categoria.id)
        .where(Producto.id == product_id)
    ).first()
    if result is None:
        return None
    product, category = result
    return _product_data(product, category)


def _validate_category(category_id: int | None, session):
    if category_id is not None and session.get(Categoria, category_id) is None:
        raise ValueError("Categoría no encontrada")


def create_product(product_data: ProductoCreate, user_id: int, session):
    _validate_category(product_data.category_id, session)
    product = Producto(**product_data.model_dump(), user_id=user_id)
    session.add(product)
    session.commit()
    session.refresh(product)
    return get_product(product.id, session)


def update_product(
    product_id: int,
    product_data: ProductoUpdate,
    session
):
    product = session.get(Producto, product_id)
    if product is None:
        return None

    changes = product_data.model_dump(exclude_unset=True)
    if "category_id" in changes:
        _validate_category(changes["category_id"], session)
    for field_name, value in changes.items():
        setattr(product, field_name, value)

    session.add(product)
    session.commit()
    session.refresh(product)
    return get_product(product_id, session)


def delete_product(product_id: int, session):
    product = session.get(Producto, product_id)
    if product is None:
        return "not_found"

    in_cart = session.exec(
        select(CarritoItem.id).where(CarritoItem.product_id == product_id)
    ).first()
    in_order = session.exec(
        select(PedidoItem.id).where(PedidoItem.product_id == product_id)
    ).first()
    if in_cart or in_order:
        return "in_use"

    session.delete(product)
    session.commit()
    return "deleted"

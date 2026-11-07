from sqlmodel import select

from app.models.producto import Producto
from app.schemas.producto import ProductoCreate, ProductoUpdate


def get_products(user_id: int, session):
    query = select(Producto).where(
        Producto.user_id == user_id
    )

    return session.exec(query).all()


def get_product(product_id: int, user_id: int, session):
    return session.exec(
        select(Producto).where(
            Producto.id == product_id,
            Producto.user_id == user_id
        )
    ).first()


def create_product(product_data: ProductoCreate, user_id: int, session):
    product = Producto(
        **product_data.model_dump(),
        user_id=user_id
    )

    session.add(product)
    session.commit()
    session.refresh(product)

    return product


def update_product(
    product_id: int,
    product_data: ProductoUpdate,
    user_id: int,
    session
):
    product = get_product(product_id, user_id, session)
    if product is None:
        return None

    for field_name, value in product_data.model_dump(exclude_unset=True).items():
        setattr(product, field_name, value)

    session.add(product)
    session.commit()
    session.refresh(product)

    return product


def delete_product(product_id: int, user_id: int, session):
    product = get_product(product_id, user_id, session)
    if product is None:
        return False

    session.delete(product)
    session.commit()

    return True

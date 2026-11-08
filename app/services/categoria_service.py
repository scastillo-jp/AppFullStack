from sqlmodel import select

from app.models.categoria import Categoria
from app.models.producto import Producto
from app.schemas.categoria import CategoriaCreate, CategoriaUpdate


def get_categories(session):
    return session.exec(select(Categoria).order_by(Categoria.name)).all()


def create_category(category_data: CategoriaCreate, session):
    normalized_name = category_data.name.strip()
    if len(normalized_name) < 2:
        raise ValueError("El nombre de la categoría debe tener al menos 2 caracteres")
    existing = session.exec(
        select(Categoria).where(Categoria.name == normalized_name)
    ).first()
    if existing:
        raise ValueError("Ya existe una categoría con ese nombre")

    category_fields = category_data.model_dump()
    category_fields["name"] = normalized_name
    category = Categoria(**category_fields)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


def update_category(category_id: int, category_data: CategoriaUpdate, session):
    category = session.get(Categoria, category_id)
    if category is None:
        return None

    changes = category_data.model_dump(exclude_unset=True)
    if not changes:
        raise ValueError("Debes indicar al menos un campo para actualizar")
    if "name" in changes and changes["name"] is not None:
        changes["name"] = changes["name"].strip()
        if len(changes["name"]) < 2:
            raise ValueError("El nombre de la categoría debe tener al menos 2 caracteres")
        existing = session.exec(
            select(Categoria).where(
                Categoria.name == changes["name"],
                Categoria.id != category_id
            )
        ).first()
        if existing:
            raise ValueError("Ya existe una categoría con ese nombre")
    for field_name, value in changes.items():
        setattr(category, field_name, value)

    session.add(category)
    session.commit()
    session.refresh(category)
    return category


def delete_category(category_id: int, session):
    category = session.get(Categoria, category_id)
    if category is None:
        return "not_found"
    product_id = session.exec(
        select(Producto.id).where(Producto.category_id == category_id)
    ).first()
    if product_id is not None:
        return "in_use"
    session.delete(category)
    session.commit()
    return "deleted"

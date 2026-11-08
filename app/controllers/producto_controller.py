from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, Response, status

from app.db.database import SessionDep
from app.dependencies.auth import CurrentAdmin, CurrentUser
from app.schemas.producto import ProductoCreate, ProductoUpdate
from app.services import producto_service as product_service


router = APIRouter(tags=["Productos"])


@router.get("/productos")
def get_products(
    current_user: CurrentUser,
    session: SessionDep,
    search: str | None = None,
    category_id: Annotated[int | None, Query(gt=0)] = None
):
    return product_service.get_products(session, search, category_id)


@router.post(
    "/productos",
    status_code=status.HTTP_201_CREATED
)
def create_product(
    product_data: ProductoCreate,
    current_admin: CurrentAdmin,
    session: SessionDep
):
    try:
        return product_service.create_product(
            product_data,
            current_admin.id,
            session
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        ) from error


@router.get("/productos/{id}")
def get_product(
    product_id: Annotated[int, Path(alias="id", gt=0)],
    current_user: CurrentUser,
    session: SessionDep
):
    product = product_service.get_product(product_id, session)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    return product


@router.put("/productos/{id}")
def update_product(
    product_id: Annotated[int, Path(alias="id", gt=0)],
    product_data: ProductoUpdate,
    current_admin: CurrentAdmin,
    session: SessionDep
):
    try:
        product = product_service.update_product(
            product_id,
            product_data,
            session
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        ) from error
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    return product


@router.delete(
    "/productos/{id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_product(
    product_id: Annotated[int, Path(alias="id", gt=0)],
    current_admin: CurrentAdmin,
    session: SessionDep
) -> Response:
    result = product_service.delete_product(product_id, session)
    if result == "not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    if result == "in_use":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar un producto incluido en un carrito o pedido"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)

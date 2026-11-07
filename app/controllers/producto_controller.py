from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Response, status

from app.db.database import SessionDep
from app.dependencies.auth import CurrentUser
from app.schemas.producto import ProductoCreate, ProductoUpdate
from app.services import producto_service as product_service


router = APIRouter(tags=["Productos"])

@router.get("/productos")
def get_products(
    current_user: CurrentUser,
    session: SessionDep
):
    return product_service.get_products(
        current_user.id,
        session
    )


@router.post(
    "/productos",
    status_code=status.HTTP_201_CREATED
)
def create_product(
    product_data: ProductoCreate,
    current_user: CurrentUser,
    session: SessionDep
):
    return product_service.create_product(
        product_data,
        current_user.id,
        session
    )


@router.get(
    "/productos/{id}"
)
def get_product(
    product_id: Annotated[int, Path(alias="id")],
    current_user: CurrentUser,
    session: SessionDep
):
    product = product_service.get_product(
        product_id,
        current_user.id,
        session
    )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )

    return product


@router.put(
    "/productos/{id}"
)
def update_product(
    product_id: Annotated[int, Path(alias="id")],
    product_data: ProductoUpdate,
    current_user: CurrentUser,
    session: SessionDep
):
    product = product_service.update_product(
        product_id,
        product_data,
        current_user.id,
        session
    )

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
    product_id: Annotated[int, Path(alias="id")],
    current_user: CurrentUser,
    session: SessionDep
) -> Response:
    deleted = product_service.delete_product(
        product_id,
        current_user.id,
        session
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


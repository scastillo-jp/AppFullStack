from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Response, status

from app.db.database import SessionDep
from app.dependencies.auth import CurrentUser
from app.schemas.carrito import CarritoItemCreate, CarritoItemUpdate
from app.services import carrito_service


router = APIRouter(prefix="/carrito", tags=["Carrito"])


@router.get(
    "",
    summary="Consultar mi carrito",
    description="Devuelve los artículos y el total del carrito del usuario autenticado.",
)
def get_cart(current_user: CurrentUser, session: SessionDep):
    return carrito_service.get_cart(current_user.id, session)


@router.post(
    "/items",
    summary="Añadir un producto al carrito",
    description=(
        "Añade un producto al carrito o incrementa su cantidad si ya existe. "
        "La cantidad no puede superar el inventario disponible."
    ),
)
def add_cart_item(
    item_data: CarritoItemCreate,
    current_user: CurrentUser,
    session: SessionDep
):
    try:
        return carrito_service.add_item(
            current_user.id,
            item_data.product_id,
            item_data.quantity,
            session
        )
    except LookupError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        ) from error
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


@router.patch(
    "/items/{item_id}",
    summary="Cambiar cantidad de un artículo",
    description=(
        "Actualiza la cantidad de un artículo del carrito autenticado. "
        "La cantidad debe ser mayor que cero y no superar el inventario."
    ),
)
def update_cart_item(
    item_id: Annotated[
        int,
        Path(gt=0, description="Identificador del artículo del carrito.")
    ],
    item_data: CarritoItemUpdate,
    current_user: CurrentUser,
    session: SessionDep
):
    try:
        cart = carrito_service.update_item(
            current_user.id,
            item_id,
            item_data.quantity,
            session
        )
    except LookupError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        ) from error
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error
    if cart is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artículo no encontrado en el carrito"
        )
    return cart


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Quitar un artículo del carrito",
    description="Elimina un artículo del carrito del usuario autenticado.",
)
def remove_cart_item(
    item_id: Annotated[
        int,
        Path(gt=0, description="Identificador del artículo del carrito.")
    ],
    current_user: CurrentUser,
    session: SessionDep
) -> Response:
    removed = carrito_service.remove_item(
        current_user.id,
        item_id,
        session
    )
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artículo no encontrado en el carrito"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)

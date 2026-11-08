from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Response, status

from app.db.database import SessionDep
from app.dependencies.auth import CurrentAdmin, CurrentUser
from app.schemas.categoria import CategoriaCreate, CategoriaRead, CategoriaUpdate
from app.services import categoria_service


router = APIRouter(prefix="/categorias", tags=["Categorías"])


@router.get("", response_model=list[CategoriaRead])
def get_categories(current_user: CurrentUser, session: SessionDep):
    return categoria_service.get_categories(session)


@router.post("", response_model=CategoriaRead, status_code=status.HTTP_201_CREATED)
def create_category(
    category_data: CategoriaCreate,
    current_admin: CurrentAdmin,
    session: SessionDep
):
    try:
        return categoria_service.create_category(category_data, session)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


@router.put("/{category_id}", response_model=CategoriaRead)
def update_category(
    category_id: Annotated[int, Path(gt=0)],
    category_data: CategoriaUpdate,
    current_admin: CurrentAdmin,
    session: SessionDep
):
    try:
        category = categoria_service.update_category(
            category_id,
            category_data,
            session
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: Annotated[int, Path(gt=0)],
    current_admin: CurrentAdmin,
    session: SessionDep
) -> Response:
    result = categoria_service.delete_category(category_id, session)
    if result == "not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )
    if result == "in_use":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar una categoría que contiene productos"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)

from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Response, status

from app.db.database import SessionDep
from app.dependencies.auth import CurrentAdmin
from app.schemas.usuario import UsuarioRead
from app.services import usuario_service


router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get(
    "",
    response_model=list[UsuarioRead],
    summary="Listar usuarios",
    description=(
        "Devuelve los perfiles de todos los usuarios. Requiere rol administrador "
        "porque la respuesta contiene datos personales."
    ),
)
def get_users(current_admin: CurrentAdmin, session: SessionDep):
    return usuario_service.get_users(session)


@router.get(
    "/{user_id}",
    response_model=UsuarioRead,
    summary="Consultar usuario por ID",
    description=(
        "Devuelve el perfil del usuario indicado. Requiere rol administrador."
    ),
)
def get_user(
    user_id: Annotated[
        int,
        Path(gt=0, description="Identificador del usuario.")
    ],
    current_admin: CurrentAdmin,
    session: SessionDep
):
    user = usuario_service.get_user(user_id, session)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar usuario",
    description=(
        "Elimina al usuario indicado y su carrito. No permite eliminar usuarios "
        "con pedidos o productos asociados, ni al último administrador. "
        "Requiere rol administrador."
    ),
)
def delete_user(
    user_id: Annotated[
        int,
        Path(gt=0, description="Identificador del usuario.")
    ],
    current_admin: CurrentAdmin,
    session: SessionDep
) -> Response:
    if current_admin.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No puedes eliminar tu propia cuenta de administrador"
        )

    result = usuario_service.delete_user(user_id, session)
    if result == "not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    if result == "last_admin":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar al último administrador"
        )
    if result == "in_use":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar un usuario con pedidos o productos asociados"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)

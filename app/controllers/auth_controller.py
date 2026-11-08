from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.db.database import SessionDep
from app.schemas.usuario import UsuarioCreate, UsuarioRead, UsuarioUpdate, Token
from app.services import usuario_service as user_service
from app.core.security import create_access_token
from app.dependencies.auth import CurrentUser, OptionalCurrentUser
from app.models.usuario import ROL_ADMINISTRADOR

router = APIRouter(tags=["Auth"], prefix="/auth")

@router.post(
    "/register",
    response_model=UsuarioRead,
    summary="Registrar un cliente",
    description=(
        "Crea una cuenta con los datos de contacto y el rol indicado. "
        "El rol se omite en el registro público y por defecto es 'cliente'. "
        "Para crear una cuenta con rol 'administrador', incluye un JWT de "
        "un administrador existente en Authorization: Bearer. Sin ese permiso "
        "la solicitud con rol administrador se rechaza."
    ),
)
def register_user(
    user_data: UsuarioCreate,
    session: SessionDep,
    current_user: OptionalCurrentUser
):
    if (
        user_data.role == ROL_ADMINISTRADOR
        and (current_user is None or current_user.role != ROL_ADMINISTRADOR)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere autenticación de administrador para crear otro administrador"
        )

    user = user_service.register_user(user_data, session)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario ya existe"
        )

    return user

@router.post(
    "/login",
    response_model=Token,
    summary="Iniciar sesión",
    description=(
        "Valida el correo y la contraseña del usuario y devuelve un JWT. "
        "En el formulario OAuth2, envía el correo en el campo 'username'."
    ),
)
def login(
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep
):
    user = user_service.authenticate_user(
        credentials.username,
        credentials.password,
        session
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = create_access_token({"sub": user.username})

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get(
    "/me",
    response_model=UsuarioRead,
    summary="Consultar mi perfil",
    description=(
        "Devuelve los datos de la cuenta autenticada según el JWT enviado "
        "en el encabezado Authorization: Bearer."
    ),
)
def get_profile(current_user: CurrentUser):
    return current_user


@router.patch(
    "/me",
    response_model=UsuarioRead,
    summary="Actualizar mi perfil",
    description=(
        "Actualiza parcialmente los datos de contacto de la cuenta autenticada. "
        "Solo se modifican los campos enviados; el rol no se puede cambiar "
        "con este endpoint."
    ),
)
def update_profile(
    user_data: UsuarioUpdate,
    current_user: CurrentUser,
    session: SessionDep
):
    try:
        return user_service.update_user(current_user, user_data, session)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error

from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.db.database import SessionDep
from app.schemas.usuario import UsuarioCreate, UsuarioRead, UsuarioUpdate, Token
from app.services import usuario_service as user_service
from app.core.security import create_access_token
from app.dependencies.auth import CurrentUser

router = APIRouter(tags=["Auth"], prefix="/auth")

@router.post(
    "/register",
    response_model=UsuarioRead,
)
def register_user(user_data: UsuarioCreate, session: SessionDep):
    user = user_service.register_user(user_data, session)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario ya existe"
        )

    return user

@router.post(
    "/login",
    response_model=Token
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


@router.get("/me", response_model=UsuarioRead)
def get_profile(current_user: CurrentUser):
    return current_user


@router.patch("/me", response_model=UsuarioRead)
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
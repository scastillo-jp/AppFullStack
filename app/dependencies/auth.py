
import jwt

from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import select

from app.db.database import SessionDep
from app.core.config import SECRET_KEY, ALGORITHM
from app.models.usuario import ROL_ADMINISTRADOR, Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
optional_oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    auto_error=False
)


def _get_user_from_token(token: str, session):
    auth_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar la autenticación",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        username = payload.get("sub")
        if username is None:
            raise auth_error

    except jwt.InvalidTokenError:
        raise auth_error

    user = session.exec(
        select(Usuario).where(Usuario.username == username)
    ).first()

    if user is None:
        raise auth_error

    return user


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDep
):
    return _get_user_from_token(token, session)


def get_optional_current_user(
    token: Annotated[str | None, Depends(optional_oauth2_scheme)],
    session: SessionDep
):
    if token is None:
        return None
    return _get_user_from_token(token, session)


CurrentUser = Annotated[Usuario, Depends(get_current_user)]
OptionalCurrentUser = Annotated[Usuario | None, Depends(get_optional_current_user)]


def get_current_admin(current_user: CurrentUser) -> Usuario:
    if current_user.role != ROL_ADMINISTRADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere el rol de administrador"
        )
    return current_user


CurrentAdmin = Annotated[Usuario, Depends(get_current_admin)]

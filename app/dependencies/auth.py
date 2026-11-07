
import jwt

from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import select

from app.db.database import SessionDep
from app.core.config import SECRET_KEY, ALGORITHM
from app.models.usuario import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDep
):
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


CurrentUser = Annotated[Usuario, Depends(get_current_user)]

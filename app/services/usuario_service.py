from sqlmodel import or_, select

from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate
from app.core.security import hash_password, verify_password


def register_user(user_data: UsuarioCreate, session):
    email = str(user_data.email).lower()
    existing_user = session.exec(
        select(Usuario).where(
            or_(
                Usuario.username == user_data.username,
                Usuario.email == email
            )
        )
    ).first()

    if existing_user:
        return None

    user = Usuario(
        username=user_data.username,
        email=email,
        hashed_password=hash_password(user_data.password)
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


def authenticate_user(username: str, password: str, session):
    user = session.exec(
        select(Usuario).where(
            Usuario.username == username
        )
    ).first()

    if user is None:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user
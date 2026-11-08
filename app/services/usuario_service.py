from sqlmodel import or_, select

from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate
from app.core.security import hash_password, verify_password


def register_user(user_data: UsuarioCreate, session):
    email = str(user_data.email).lower()
    existing_user = session.exec(
        select(Usuario).where(
            or_(
                Usuario.username == email,
                Usuario.email == email,
                Usuario.cedula == user_data.cedula
            )
        )
    ).first()

    if existing_user:
        return None

    user = Usuario(
        username=email,
        email=email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        cedula=user_data.cedula,
        address=user_data.address,
        city=user_data.city,
        phone=user_data.phone,
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


def authenticate_user(email: str, password: str, session):
    normalized_email = email.lower()
    user = session.exec(
        select(Usuario).where(Usuario.email == normalized_email)
    ).first()

    if user is None:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


def update_user(user: Usuario, user_data: UsuarioUpdate, session):
    changes = user_data.model_dump(exclude_unset=True)
    for field_name in ("email", "cedula"):
        value = changes.get(field_name)
        if value is not None:
            changes[field_name] = value.lower() if field_name == "email" else value
            duplicate = session.exec(
                select(Usuario).where(
                    getattr(Usuario, field_name) == changes[field_name],
                    Usuario.id != user.id
                )
            ).first()
            if duplicate:
                raise ValueError(f"Ya existe un usuario con ese {field_name}")
        elif field_name in changes:
            raise ValueError(f"{field_name} no puede ser nulo")

    for field_name, value in changes.items():
        setattr(user, field_name, value)
    if not changes:
        raise ValueError("Debes indicar al menos un campo para actualizar")
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
from typing import Annotated
from fastapi import FastAPI, Depends
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy import inspect, text
from app.core.config import DATABASE_URL
import app.models

engine = create_engine(
    DATABASE_URL
)

def create_tables(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    if engine.dialect.name == "sqlite":
        with engine.begin() as connection:
            table_names = set(inspect(connection).get_table_names())
            if "usuario" in table_names:
                user_columns = {
                    column["name"]
                    for column in inspect(connection).get_columns("usuario")
                }
                user_migrations = {
                    "email": "VARCHAR",
                    "full_name": "VARCHAR(100)",
                    "cedula": "VARCHAR(20)",
                    "address": "VARCHAR(250)",
                    "city": "VARCHAR(100)",
                    "phone": "VARCHAR(30)",
                    "role": "VARCHAR(20) NOT NULL DEFAULT 'cliente'",
                }
                for column_name, column_type in user_migrations.items():
                    if column_name not in user_columns:
                        connection.execute(
                            text(
                                f'ALTER TABLE "usuario" ADD COLUMN "{column_name}" '
                                f"{column_type}"
                            )
                        )
                connection.execute(
                    text(
                        "CREATE UNIQUE INDEX IF NOT EXISTS ix_usuario_email "
                        "ON usuario (email)"
                    )
                )
                connection.execute(
                    text(
                        "CREATE UNIQUE INDEX IF NOT EXISTS ix_usuario_cedula "
                        "ON usuario (cedula)"
                    )
                )
                connection.execute(
                    text(
                        "CREATE INDEX IF NOT EXISTS ix_usuario_role "
                        "ON usuario (role)"
                    )
                )
            if "producto" in table_names:
                product_columns = {
                    column["name"]
                    for column in inspect(connection).get_columns("producto")
                }
                product_migrations = {
                    "category_id": "INTEGER REFERENCES categoria(id)",
                    "image_path": "VARCHAR(500)",
                }
                for column_name, column_type in product_migrations.items():
                    if column_name not in product_columns:
                        connection.execute(
                            text(
                                f'ALTER TABLE "producto" ADD COLUMN "{column_name}" '
                                f"{column_type}"
                            )
                        )
                connection.execute(
                    text(
                        "CREATE INDEX IF NOT EXISTS ix_producto_category_id "
                        "ON producto (category_id)"
                    )
                )
    yield

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
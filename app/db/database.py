from typing import Annotated
from fastapi import FastAPI, Depends
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy import inspect, text
from app.core.config import DATABASE_URL

engine = create_engine(
    DATABASE_URL
)

def create_tables(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    if engine.dialect.name == "sqlite":
        with engine.begin() as connection:
            user_columns = {
                column["name"]
                for column in inspect(connection).get_columns("usuario")
            }
            if "email" not in user_columns:
                connection.execute(
                    text('ALTER TABLE "usuario" ADD COLUMN email VARCHAR')
                )
            connection.execute(
                text(
                    "CREATE UNIQUE INDEX IF NOT EXISTS ix_usuario_email "
                    "ON usuario (email)"
                )
            )
    yield

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
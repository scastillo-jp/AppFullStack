from sqlmodel import Field, SQLModel


class Categoria(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True, min_length=2, max_length=80)
    description: str | None = Field(default=None, max_length=300)
    image_path: str | None = Field(default=None, max_length=500)

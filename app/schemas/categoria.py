from pydantic import model_validator
from sqlmodel import Field, SQLModel


class CategoriaCreate(SQLModel):
    name: str = Field(min_length=2, max_length=80)
    description: str | None = Field(default=None, max_length=300)
    image_path: str | None = Field(default=None, max_length=500)


class CategoriaUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=2, max_length=80)
    description: str | None = Field(default=None, max_length=300)
    image_path: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_update(self):
        if not self.model_fields_set:
            raise ValueError("Debes indicar al menos un campo para actualizar")
        if "name" in self.model_fields_set and self.name is None:
            raise ValueError("name no puede ser nulo")
        return self


class CategoriaRead(SQLModel):
    id: int
    name: str
    description: str | None
    image_path: str | None

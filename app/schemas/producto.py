from pydantic import field_validator, model_validator
from sqlmodel import Field, SQLModel
from app.core.money import quantize_money

class ProductoCreate(SQLModel):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=300)
    price: float = Field(gt=0)
    stock: int = Field(default=0, ge=0)
    category_id: int | None = Field(default=None, gt=0)
    image_path: str | None = Field(default=None, max_length=500)

    @field_validator("price")
    @classmethod
    def normalize_price(cls, value: float) -> float:
        normalized = quantize_money(value)
        if normalized <= 0:
            raise ValueError("price must be at least 0.01")
        return float(normalized)


class ProductoUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=300)
    price: float | None = Field(default=None, gt=0)
    stock: int | None = Field(default=None, ge=0)
    category_id: int | None = Field(default=None, gt=0)
    image_path: str | None = Field(default=None, max_length=500)

    @field_validator("price")
    @classmethod
    def normalize_price(cls, value: float | None) -> float | None:
        if value is None:
            return None
        normalized = quantize_money(value)
        if normalized <= 0:
            raise ValueError("price must be at least 0.01")
        return float(normalized)

    @model_validator(mode="after")
    def validate_update(self):
        if not self.model_fields_set:
            raise ValueError("At least one product field must be provided")

        for field_name in ("name", "price", "stock"):
            if field_name in self.model_fields_set and getattr(self, field_name) is None:
                raise ValueError(f"{field_name} cannot be null")

        return self
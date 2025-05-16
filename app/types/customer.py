# --- CUSTOMER CLASSES --- #


from typing import Optional
from uuid import UUID

from pydantic import BaseModel, computed_field, field_validator

from app.types import InvalidCountryError, CountryEnum


class CustomerBase(BaseModel):
    full_name: Optional[str] = None
    country_name: Optional[str] = None

    @field_validator('country_name')
    def validate_country(cls, v):
        if v not in [country.value for country in CountryEnum]:
            raise InvalidCountryError(f"Country '{v}' is not supported")
        return v

    @computed_field
    @property
    def country_code(self) -> str | None:
        return (
            CountryEnum.get_country_code(self.country_name)
            if self.country_name
            else None
        )


class CustomerPayload(CustomerBase):
    full_name: str
    country_name: str


class CustomerUpdatePayload(CustomerBase):
    pass


class CustomerResponse(CustomerBase):
    id: UUID
    full_name: str
    country_name: str
    country_code: str
    created_at: str
    updated_at: str


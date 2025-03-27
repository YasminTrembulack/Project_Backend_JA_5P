from dataclasses import dataclass
from enum import Enum

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base_model import BaseModel


@dataclass
class Customer(BaseModel):
    __tablename__ = 'customers'

    full_name: Mapped[str] = mapped_column(String(255), unique=True)
    country_code: Mapped[str] = mapped_column(String(2))
    country_name: Mapped[str] = mapped_column(String(50))


class CountryEnum(str, Enum):
    CN = 'China'
    US = 'United States'
    JP = 'Japan'
    DE = 'Germany'
    KR = 'South Korea'
    IN = 'India'
    FR = 'France'
    IT = 'Italy'
    GB = 'United Kingdom'
    ES = 'Spain'
    MX = 'Mexico'
    BR = 'Brazil'
    TH = 'Thailand'
    RU = 'Russia'
    CZ = 'Czech Republic'
    TR = 'Turkey'

    @classmethod
    def get_country_code(cls, name: str) -> str:
        name_lower = name.lower()
        for code, country in cls.__members__.items():
            if country.value.lower() == name_lower:
                return code
        raise ValueError(f'Country not found: {name}')

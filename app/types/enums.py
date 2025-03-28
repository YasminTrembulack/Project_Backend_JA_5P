from enum import Enum


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


class PriorityEnum(str, Enum):
    LOW = 'Low'
    MEDIUM = 'Medium'
    HIGH = 'High'


class MoldStatusEnum(str, Enum):
    PENDING = 'Pending'
    IN_PROGRESS = 'In Progress'
    COMPLETED = 'Completed'
    SHIPPED = 'Shipped'


class CamStatusEnum(str, Enum):
    PENDING = 'Pending'
    APPROVED = 'Approved'


class PartStatusEnum(str, Enum):
    PENDING = 'Pending'
    IN_PROGRESS = 'In Progress'
    COMPLETED = 'Completed'

from fastapi import APIRouter, status

from app.types.response import CountyResponse, TimeUnitResponse
from app.types.enums import CountryEnum, TimeUnitEnum

router = APIRouter(prefix='/utils')


@router.get(
    '/country', status_code=status.HTTP_200_OK, response_model=CountyResponse
)
def get_countries():
    countries = [country.value for country in CountryEnum]
    return CountyResponse(countries=countries)


@router.get(
    '/time_unit', status_code=status.HTTP_200_OK, response_model=TimeUnitResponse
)
def get_time_unit():
    time_unit = [unit.value for unit in TimeUnitEnum]
    return TimeUnitResponse(time_unit=time_unit)

from fastapi import APIRouter, status

from app.models.customer import CountryEnum
from app.types.schemas import CountyResponse

router = APIRouter(prefix='/utils')


@router.get(
    '/country', status_code=status.HTTP_200_OK, response_model=CountyResponse
)
def get_countries():
    countries = [country.value for country in CountryEnum]
    return CountyResponse(countries=countries)

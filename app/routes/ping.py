from http import HTTPStatus

from fastapi import APIRouter

from app.core.settings import Settings
from app.types.schemas import Health

router = APIRouter()


@router.get('/', status_code=HTTPStatus.OK, response_model=Health)
def read_root():
    return {
        'project_name': Settings().PROJECT_NAME,
        'version': Settings().VERSION
    }

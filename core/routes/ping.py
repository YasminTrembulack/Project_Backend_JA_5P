from http import HTTPStatus

from fastapi import APIRouter

from core.models.schemas import Message

router = APIRouter()


@router.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Pong'}

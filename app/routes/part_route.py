from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_session
from app.middlewares.check_roles import check_roles
from app.services.part_service import PartService
from app.types.schemas import (
    EntityResponse,
    PartPayload,
    PartResponse,
)

router = APIRouter(prefix='/part')


@router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
    response_model=EntityResponse[PartResponse],
)
def create_part(
    part: PartPayload,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'Editor'])),
):
    service = PartService(session)

    db_part = service.part_register(part)

    part_response = PartResponse.model_validate(db_part.to_dict())
    return EntityResponse(message='Part created with success.', data=part_response)

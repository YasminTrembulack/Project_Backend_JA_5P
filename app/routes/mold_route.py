from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_session
from app.middlewares.check_roles import check_roles
from app.services.mold_service import MoldService
from app.types.schemas import (
    EntityResponse,
    MoldPayload,
    MoldResponde,
    # Metadata,
)

router = APIRouter(prefix='/mold')


@router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
    response_model=EntityResponse[MoldResponde],
)
def create_mold(
    mold: MoldPayload,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'Editor'])),
):
    service = MoldService(session)
    db_mold = service.mold_register(mold)
    mold_response = MoldResponde.model_validate(db_mold.to_dict())
    return EntityResponse(message='Mold created with success.', data=mold_response)

import datetime

from fastapi import APIRouter, status

from app.core.settings import Settings
from app.types.schemas import PingResponse

router = APIRouter()


@router.get('/ping', status_code=status.HTTP_200_OK, response_model=PingResponse)
def read_root():
    return {
        'project_name': Settings().PROJECT_NAME,
        'version': Settings().VERSION,
        'timestamp': datetime.utcnow().isoformat()
    }

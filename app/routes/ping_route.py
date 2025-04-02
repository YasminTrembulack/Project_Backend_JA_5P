from datetime import datetime, timezone

import pytz
from fastapi import APIRouter, status

from app.core.settings import Settings
from app.types.schemas import PingResponse

router = APIRouter()


@router.get('/ping', status_code=status.HTTP_200_OK, response_model=PingResponse)
def read_root():
    tz = pytz.timezone(Settings().TZ)
    timestamp = datetime.now(timezone.utc).isoformat()
    return {
        'project_name': Settings().PROJECT_NAME,
        'version': Settings().VERSION,
        'timestamp': datetime.fromisoformat(timestamp)
        .astimezone(tz)
        .strftime('%d/%m/%Y %H:%M:%S'),
    }

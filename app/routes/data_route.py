
from io import BytesIO
from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.db.database import get_session
from app.middlewares.check_roles import check_roles


from app.services.data_service import DataService
from app.types.exceptions import InvalidExcelFileError


router = APIRouter(prefix='/data')

@router.post(
    '/upload-excel', 
    status_code=status.HTTP_200_OK
    # response_model=EntityResponse[MaterialPartResponse],
)
async def import_excel(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    user: None = Depends(check_roles(['Admin', 'Editor']))
):
    if not file.filename.endswith(('.xls', '.xlsx', '.xlsm')):
        raise InvalidExcelFileError()

    contents = await file.read()
    service = DataService(session)
    service.import_excel_from_bytes(contents, user.id)
    
    return {'message': 'Importação realizada com sucesso'}
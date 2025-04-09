from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_session
from app.middlewares.check_roles import check_roles
from app.services.machine_service import MachineService
from app.types.schemas import (
    DeleteResponse,
    EntityResponse,
    GetAllResponse,
    MachinePayload,
    MachineResponse,
    MachineUpdatePayload,
    Metadata,
)

router = APIRouter(prefix='/machine')


@router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
    response_model=EntityResponse[MachineResponse],
)
def create_machine(
    machine: MachinePayload,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'Editor'])),
):
    service = MachineService(session)
    db_machine = service.machine_register(machine)
    machine_response = MachineResponse.model_validate(db_machine.to_dict())
    return EntityResponse(
        message='Machine created with success.', data=machine_response
    )


@router.get(
    '/all',
    status_code=status.HTTP_200_OK,
    response_model=GetAllResponse[MachineResponse],
)
def get_all_machines(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    order_by: str = Query('created_at'),
    desc_order: bool = Query(False),
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'User', 'Editor'])),
):
    service = MachineService(session)
    machines, total_machines = service.get_all_machines(
        page, limit, order_by, desc_order
    )
    total_pages = (total_machines + limit - 1) // limit
    meta = Metadata(
        total=total_machines,
        limit=limit,
        page=page,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1,
        order_by=order_by,
        desc_order=desc_order,
    )
    machines = [MachineResponse.model_validate(m.to_dict()) for m in machines]
    return GetAllResponse(
        message='Machines found successfully.', data=machines, metadata=meta
    )


@router.delete(
    '/delete/{id}',
    status_code=status.HTTP_200_OK,
    response_model=DeleteResponse,
)
def delete_machine(
    id: str,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin'])),
):
    service = MachineService(session)
    service.delete_machine(id)
    return DeleteResponse(message='Machine deleted successfully.')


@router.patch(
    '/update/{id}',
    status_code=status.HTTP_200_OK,
    response_model=EntityResponse[MachineResponse],
)
def update_machine(
    id: str,
    machine: MachineUpdatePayload,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'Editor'])),
):
    service = MachineService(session)
    machine = service.update_machine(id, machine)
    machine_response = MachineResponse.model_validate(machine.to_dict())
    return EntityResponse(
        message='Machine updated successfully.', data=machine_response
    )


@router.get(
    '/{id}',
    status_code=status.HTTP_200_OK,
    response_model=EntityResponse[MachineResponse],
)
def get_machine(
    id: str,
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'User', 'Editor'])),
):
    service = MachineService(session)
    machine = service.get_machine(id)
    machine_response = MachineResponse.model_validate(machine.to_dict())
    return EntityResponse(
        message='Machine found successfully.', data=machine_response
    )

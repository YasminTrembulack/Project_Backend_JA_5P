from typing import List, Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_session
from app.middlewares.check_roles import check_roles
from app.services.machine_service import MachineService
from app.types.base import Metadata
from app.types.payload import (
    MachinePayload,
    MachineQueryParams,
    MachineUpdatePayload,
)
from app.types.response import (
    DeleteResponse,
    EntityResponse,
    GetAllResponse,
    MachineResponse,
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
    query: MachineQueryParams = Depends(),
    associations: List[Literal['operations']] = Query([]),
    session: Session = Depends(get_session),
    _: None = Depends(check_roles(['Admin', 'User', 'Editor'])),
):
    service = MachineService(session)
    machines, total_machines = service.get_all_machines(query)
    total_pages = (total_machines + query.limit - 1) // query.limit
    meta = Metadata(
        total=total_machines,
        limit=query.limit,
        page=query.page,
        total_pages=total_pages,
        has_next=query.page < total_pages,
        has_previous=query.page > 1,
        order_by=query.order_by,
        desc_order=query.desc_order,
    )

    machine_response = []

    for m in machines:
        machine_dict = m.to_dict()
        associations_dict = service.configure_associations_response(m, associations)
        combined_dict = {**machine_dict, **associations_dict}

        machine_response.append(MachineResponse.model_validate(combined_dict))

    return GetAllResponse(
        message='Machines found successfully.', data=machine_response, metadata=meta
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

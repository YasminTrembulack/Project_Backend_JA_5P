from datetime import datetime, timezone
from typing import List, Tuple

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.machine import Machine
from app.repositories.machine_repositorie import MachineRepository
from app.types.exceptions import (
    DataConflictError,
    InvalidFieldError,
    NotFoundError,
)
from app.types.machine import (
    MachineBase,
    MachinePayload,
    MachineUpdatePayload,
)
from app.types.operation import OperationResponse


class MachineService:
    def __init__(self, db: Session):
        self.machine_repo = MachineRepository(db)

    def machine_register(self, payload: MachinePayload) -> Machine:
        if payload.name:
            self._validate_name_uniqueness(payload.name)
        else:
            new_name = self.machine_repo.total_machine(True) + 1
            payload.name = str(new_name)
        return self.machine_repo.create_machine(payload)

    def get_all_machines(
        self, page: int, limit: int, order_by: str, desc_order: bool
    ) -> Tuple[List[Machine], int]:
        if not hasattr(Machine, order_by):
            raise InvalidFieldError(
                f'Field {order_by} does not exist on Machine model'
            )
        offset = (page - 1) * limit
        order = (
            desc(getattr(Machine, order_by))
            if desc_order
            else getattr(Machine, order_by)
        )
        return self.machine_repo.get_all_machines_paginated(offset, limit, order)

    def delete_machine(self, id: str) -> None:
        machine = self._get_machine_or_404(id)
        timestamp = int(datetime.now(timezone.utc).timestamp())
        machine.name = f'deleted_{timestamp}_{machine.name}'
        return self.machine_repo.delete_machine(machine)

    def update_machine(self, id: str, payload: MachineUpdatePayload) -> Machine:
        machine = self._get_machine_or_404(id)
        updated_data = payload.model_dump(exclude_unset=True)

        new_name = updated_data.get('name', machine.name)

        self._validate_name_uniqueness(new_name, id)

        updated_machine = self._update_machine_fields(payload, machine)
        return self.machine_repo.update_machine(updated_machine)

    def get_machine(self, id: str) -> Machine:
        return self._get_machine_or_404(id)

    def _get_machine_or_404(self, id: str) -> Machine:
        machine = self.machine_repo.get_machine_by_field('id', id)
        if not machine:
            raise NotFoundError('Machine not found')
        return machine

    @staticmethod
    def configure_associations_response(
        machine: Machine, associations: List[str]
    ) -> dict:
        def _load_operations():
            return [
                OperationResponse.model_validate(op.to_dict())
                for op in machine.operations
            ]

        loaders = {
            'operations': _load_operations,
        }

        return {
            key: loaders[key]()
            for key in associations
            if key in loaders and getattr(machine, key, None) is not None
        }

    @staticmethod
    def _update_machine_fields(payload: MachineBase, target: Machine) -> Machine:
        for key, value in payload.model_dump(exclude_unset=True).items():
            if hasattr(target, key) and value is not None:
                setattr(target, key, value)
        return target

    def _validate_name_uniqueness(self, name: str, exclude_id: str = None) -> None:
        if self.machine_repo.get_machine_by_field(
            'name', name, exclude_id=exclude_id
        ):
            raise DataConflictError(f"A Machine with name '{name}' already exists.")

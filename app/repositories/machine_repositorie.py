from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy import UnaryExpression
from sqlalchemy.orm import Session

from app.interfaces.machine_repository_interface import IMachineRepository
from app.models.machine import Machine
from app.types.exceptions import InvalidFieldError
from app.types.schemas import MachinePayload

class MachineRepository(IMachineRepository):
    def __init__(self, db: Session):
        self.db = db

    def create_machine(self, machine: MachinePayload) -> Machine:
        db_machine = Machine(
            name=machine.name,
            m_type=machine.m_type,
            status=machine.status
        )
        self.db.add(db_machine)
        self.db.commit()
        self.db.refresh(db_machine)
        return db_machine

    def get_machine_by_field(
        self,
        field_name: str,
        value: str,
        include_inactive: Optional[bool] = False,
        exclude_id: Optional[str] = None,
    ) -> Optional[Machine]:
        user_field = getattr(Machine, field_name, None)
        if not user_field:
            raise InvalidFieldError(
                f'Field {field_name} does not exist on Machine model'
            )
        query = self.db.query(Machine).filter(user_field == value)
        if not include_inactive:
            query = query.filter(Machine.is_active.is_(True))
        if exclude_id:
            query = query.filter(Machine.id != exclude_id)
        return query.first()

    def get_all_machines_paginated(
        self,
        offset: int,
        limit: int,
        order: UnaryExpression,
        include_inactive: Optional[bool] = False,
    ) -> Tuple[List[Machine], int]:
        query = self.db.query(Machine)

        if not include_inactive:
            query = query.filter(Machine.is_active.is_(True))

        machines = query.order_by(order).offset(offset).limit(limit).all()
        total_machines = query.count()

        return machines, total_machines

    def delete_machine(self, machine: Machine) -> None:
        machine.is_active = False
        machine.disabled_at = datetime.now(timezone.utc)
        self.db.commit()

    def update_machine(self, machine: Machine) -> Machine:
        self.db.commit()
        self.db.refresh(machine)
        return machine

    def restore_machine(self, machine: Machine) -> Machine:
        machine.is_active = True
        machine.archived_at = None
        self.db.commit()
        self.db.refresh(machine)
        return machine

    def total_machine(
        self,
        include_inactive: Optional[bool] = False,
    ) -> int:
        query = self.db.query(Machine)
        if not include_inactive:
            query = query.filter(Machine.is_active.is_(True))
        return query.count()


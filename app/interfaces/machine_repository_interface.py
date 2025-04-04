from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from sqlalchemy import UnaryExpression

from app.models.machine import Machine
from app.types.schemas import MachinePayload


class IMachineRepository(ABC):
    @abstractmethod
    def create_machine(self, machine: MachinePayload) -> Machine:
        pass

    @abstractmethod
    def get_machine_by_field(
        self,
        field_name: str,
        value: str,
        include_inactive: Optional[bool] = False,
        exclude_id: Optional[str] = None,
    ) -> Optional[Machine]:
        pass

    @abstractmethod
    def get_all_machines_paginated(
        self,
        offset: int,
        limit: int,
        order: UnaryExpression,
        include_inactive: Optional[bool] = False,
    ) -> Tuple[List[Machine], int]:
        pass

    @abstractmethod
    def delete_machine(self, machine: Machine) -> None:
        pass

    @abstractmethod
    def update_machine(self, machine: Machine) -> Machine:
        pass

    @abstractmethod
    def restore_machine(self, machine: Machine) -> Machine:
        pass

    @abstractmethod
    def total_machine(
        self,
        include_inactive: Optional[bool] = False,
    ) -> int:
        pass
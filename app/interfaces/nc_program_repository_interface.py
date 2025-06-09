from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from sqlalchemy import UnaryExpression

from app.models.nc_program import NcProgram
from app.types.payload import NcProgramPayload


class INcProgramRepository(ABC):
    @abstractmethod
    def create_nc_program(self, nc_program: NcProgramPayload) -> NcProgram:
        pass

    @abstractmethod
    def get_nc_program_by_field(
        self,
        field_name: str,
        value: str,
        include_inactive: Optional[bool] = False,
        exclude_id: Optional[str] = None,
    ) -> Optional[NcProgram]:
        pass

    @abstractmethod
    def get_all_nc_programs_paginated(
        self,
        offset: int,
        limit: int,
        order: UnaryExpression,
        include_inactive: Optional[bool] = False,
    ) -> Tuple[List[NcProgram], int]:
        pass

    @abstractmethod
    def delete_nc_program(self, nc_program: NcProgram) -> None:
        pass

    @abstractmethod
    def update_nc_program(self, nc_program: NcProgram) -> NcProgram:
        pass

    @abstractmethod
    def restore_nc_program(self, nc_program: NcProgram) -> NcProgram:
        pass

    @abstractmethod
    def total_nc_programs(self, include_inactive: Optional[bool] = False) -> int:
        pass

from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy import BinaryExpression, UnaryExpression
from sqlalchemy.orm import Session

from app.interfaces.nc_program_repository_interface import INcProgramRepository
from app.models.nc_program import NcProgram
from app.types.exceptions import InvalidFieldError
from app.types.payload import PaginationParams, NcProgramPayload


class NcProgramRepository(INcProgramRepository):
    def __init__(self, db: Session):
        self.db = db

    def create_nc_program(self, nc_program: NcProgramPayload) -> NcProgram:
        db_nc_program = NcProgram(
            name=nc_program.name,
            responsible=nc_program.responsible,
            path=nc_program.path
        )
        self.db.add(db_nc_program)
        self.db.commit()
        self.db.refresh(db_nc_program)
        return db_nc_program

    def get_nc_program_by_field(
        self,
        field_name: str,
        value: str,
        include_inactive: Optional[bool] = False,
        exclude_id: Optional[str] = None,
    ) -> Optional[NcProgram]:
        nc_program_field = getattr(NcProgram, field_name, None)
        if not nc_program_field:
            raise InvalidFieldError(
                f'Field {field_name} does not exist on NcProgram model'
            )
        query = self.db.query(NcProgram).filter(nc_program_field == value)
        if not include_inactive:
            query = query.filter(NcProgram.is_active.is_(True))
        if exclude_id:
            query = query.filter(NcProgram.id != exclude_id)
        return query.first()

    def get_all_nc_programs_paginated(
        self,
        pagination: PaginationParams,
        order: UnaryExpression,
        filters: Optional[BinaryExpression] = None,
        joins: Optional[List] = [],
    ) -> Tuple[List[NcProgram], int]:
        query = self.db.query(NcProgram)

        if not pagination.include_inactive:
            query = query.filter(NcProgram.is_active.is_(True))

        if filters is not None:
            for join in joins:
                query = query.join(join)
            query = query.filter(filters)

        total_nc_programs = query.count()
        nc_programs = (
            query.order_by(order)
            .offset(pagination.offset)
            .limit(pagination.limit)
            .all()
        )

        return nc_programs, total_nc_programs

    def delete_nc_program(self, nc_program: NcProgram) -> None:
        nc_program.is_active = False
        nc_program.disabled_at = datetime.now(timezone.utc)
        self.db.commit()

    def update_nc_program(self, nc_program: NcProgram) -> NcProgram:
        self.db.commit()
        self.db.refresh(nc_program)
        return nc_program

    def restore_nc_program(self, nc_program: NcProgram) -> NcProgram:
        nc_program.is_active = True
        nc_program.archived_at = None
        self.db.commit()
        self.db.refresh(nc_program)
        return nc_program

    def total_nc_programs(
        self,
        include_inactive: Optional[bool] = False,
    ) -> int:
        query = self.db.query(NcProgram)
        if not include_inactive:
            query = query.filter(NcProgram.is_active.is_(True))
        return query.count()

from typing import List, Tuple

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.mold import Mold
from app.models.operation import Operation, OperationAssociation
from app.models.part import Part
from app.repositories.material_part_repositorie import MaterialPartRepository
from app.repositories.mold_repositorie import MoldRepository
from app.repositories.operation_association_repositorie import (
    OperationAssociationRepository,
)
from app.repositories.operation_repositorie import OperationRepository
from app.repositories.part_repositorie import PartRepository
from app.services.progress_service import ProgressService
from app.types import MachineStatusEnum, MaterialStatusEnum, OpStatusEnum
from app.types import (
    DataConflictError,
    InvalidFieldError,
    InvalidMachineStateError,
    MaterialNotAvailableError,
    NotFoundError,
)
from app.types import (
    OperationAssociationBase,
    OperationAssociationPayload,
    OperationAssociationUpdatePayload,
)


class OperationAssociationService:
    def __init__(self, db: Session):
        self.operation_association_repo = OperationAssociationRepository(db)
        self.material_part_repo = MaterialPartRepository(db)
        self.operation_repo = OperationRepository(db)
        self.mold_repo = MoldRepository(db)
        self.part_repo = PartRepository(db)
        self.progress_service = ProgressService(self.mold_repo, self.part_repo)

    def operation_association_register(
        self, payload: OperationAssociationPayload
    ) -> OperationAssociation:
        machine = self._get_operation_or_404(payload.operation_id).machine

        item = self._get_mold_or_part_or_404(payload.item_id)
        if isinstance(item, Mold):
            payload.item_type = 'Mold'
        else:
            payload.item_type = 'Part'

        if machine and machine.status is not MachineStatusEnum.AVAILABLE:
            raise InvalidMachineStateError(
                f'Machine is not available. Current status: {machine.status}'
            )
        if payload.status == OpStatusEnum.COMPLETED and payload.item_type == 'Part':
            self._validate_material_avaliability(payload.item_id)

        self._validate_ids(payload.item_id, payload.operation_id, payload.item_type)

        new_operation_association = (
            self.operation_association_repo.create_operation_association(payload)
        )

        if payload.item_type == 'Part':
            self.progress_service.update_part_progress(payload.item_id)

        return new_operation_association

    def get_all_operation_associations(
        self, page: int, limit: int, order_by: str, desc_order: bool
    ) -> Tuple[List[OperationAssociation], int]:
        if not hasattr(OperationAssociation, order_by):
            raise InvalidFieldError(
                f'Field {order_by} does not exist on Operation Association model'
            )
        offset = (page - 1) * limit
        order = (
            desc(getattr(OperationAssociation, order_by))
            if desc_order
            else getattr(OperationAssociation, order_by)
        )
        return (
            self.operation_association_repo.get_all_operation_associations_paginated(
                offset, limit, order
            )
        )

    def delete_operation_association(self, id: str) -> None:
        operation_association = self._get_operation_association_or_404(id)
        item = self._get_mold_or_part_or_404(operation_association.item_id)

        self.operation_association_repo.delete_operation_association(
            operation_association
        )
        if isinstance(item, Part):
            self.progress_service.update_part_progress(item.id)

    def update_operation_association(
        self, id: str, payload: OperationAssociationUpdatePayload
    ) -> OperationAssociation:
        operation_association = self._get_operation_association_or_404(id)
        updated_data = payload.model_dump(exclude_unset=True)

        new_item_id = updated_data.get('item_id', operation_association.item_id)
        new_status = updated_data.get('status', operation_association.status)
        its_a_new_status = (
            True if operation_association.status != payload.status else False
        )
        new_operation_id = updated_data.get(
            'operation_id', operation_association.operation_id
        )

        item = self._get_mold_or_part_or_404(new_item_id)
        if isinstance(item, Mold):
            payload.item_type = 'Mold'
        else:
            payload.item_type = 'Part'

        if payload.item_type == 'Part':
            if new_status == OpStatusEnum.COMPLETED:
                self._validate_material_avaliability(new_item_id)

        self._validate_ids(
            new_item_id,
            new_operation_id,
            payload.item_type,
            exclude_id=operation_association.id,
        )

        updated_operation_association = self._update_operation_association_fields(
            payload, operation_association
        )
        new_operation_association = (
            self.operation_association_repo.update_operation_association(
                updated_operation_association
            )
        )

        if payload.item_type == 'Part' and its_a_new_status:
            self.progress_service.update_part_progress(new_item_id)

        return new_operation_association

    def get_operation_association(self, id: str) -> OperationAssociation:
        return self._get_operation_association_or_404(id)

    def _get_operation_association_or_404(self, id: str) -> OperationAssociation:
        operation_association = (
            self.operation_association_repo.get_operation_association_by_field(
                'id', id
            )
        )
        if not operation_association:
            raise NotFoundError('OperationAssociation not found')
        return operation_association

    def _get_operation_or_404(self, id: str) -> Operation:
        operation = self.operation_repo.get_operation_by_field('id', id)
        if not operation:
            raise NotFoundError('Operation not found')
        return operation

    @staticmethod
    def _update_operation_association_fields(
        payload: OperationAssociationBase, target: OperationAssociation
    ) -> OperationAssociation:
        for key, value in payload.model_dump(exclude_unset=True).items():
            if hasattr(target, key) and value is not None:
                setattr(target, key, value)
        return target

    def _get_mold_or_part_or_404(self, id: str) -> Mold | Part:
        mold = self.mold_repo.get_mold_by_field('id', id)
        part = self.part_repo.get_part_by_field('id', id)
        if mold:
            return mold
        if part:
            return part
        raise NotFoundError('No machine or part found with the provided ID')

    def _validate_ids(
        self, item_id: str, operation_id: str, item_type: str, exclude_id: str = None
    ) -> None:
        if self.operation_association_repo.get_by_item_and_operation(
            item_id, operation_id, item_type, exclude_id
        ):
            raise DataConflictError(
                'An operation association for this item already exists.'
            )

    def _validate_material_avaliability(self, id: str):
        if self.material_part_repo.get_by_id_and_status(
            id, MaterialStatusEnum.PENDING
        ):
            raise MaterialNotAvailableError(
                "Cannot change status to 'Completed'"
                'because there are still pending materials.'
            )

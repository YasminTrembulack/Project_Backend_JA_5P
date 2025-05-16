from datetime import date, datetime

from loguru import logger

from app.models.material import MaterialPart
from app.models.mold import Mold
from app.models.operation import OperationAssociation
from app.models.part import Part
from app.repositories.mold_repositorie import MoldRepository
from app.repositories.part_repositorie import PartRepository
from app.types.enums import (
    ItemStatusEnum,
    MaterialStatusEnum,
    OpStatusEnum,
    PriorityEnum,
    SimpleStatusEnum,
)
from app.types.exceptions import NotFoundError


COMPLETED_PERCENTAGE = 100

URGENT_DAYS_THRESHOLD = 5     # urgência se a entrega for em até 5 dias
HIGH_DAYS_THRESHOLD = 15      # alta prioridade até 15 dias
MEDIUM_DAYS_THRESHOLD = 45    # prioridade média até 45 dias

URGENT_PRIORITY_THRESHOLD = 120  # ex: (100 - 0) * 1.2 = 120
HIGH_PRIORITY_THRESHOLD = 75     # ex: (100 - 0) * 0.8 = 80
MEDIUM_PRIORITY_THRESHOLD = 35


class ProgressService:
    def __init__(self, mold_repo: MoldRepository, part_repo: PartRepository):
        self.part_repo = part_repo
        self.mold_repo = mold_repo

    def update_part_progress(self, part_id: str) -> None:
        part = self._get_part_or_404(part_id)

        active_material = [m for m in part.material_associations if m.is_active]
        active_operations = [
            oa for oa in part.operation_associations if oa.is_active
        ]

        progress_percentage = self._calculate_part_progress_percentage(
            active_operations, active_material, part.model_3d, part.nc_program
        )

        part.progress_percentage = progress_percentage
        part.status = self._define_status(progress_percentage)
        print(progress_percentage)
        self.part_repo.update_part(part)

        self._update_mold_progress(part.mold_id)

    @staticmethod
    def calculate_priority(
        delivery_date: datetime, progress_percentage: float
    ) -> PriorityEnum:
        now = datetime.now()
        days_until_delivery = max((delivery_date - now).days, 0)

        if days_until_delivery <= URGENT_DAYS_THRESHOLD:
            progress_weight = 1.8
        elif days_until_delivery <= HIGH_DAYS_THRESHOLD:
            progress_weight = 1.3
        elif days_until_delivery <= MEDIUM_DAYS_THRESHOLD:
            progress_weight = 0.8
        else:
            progress_weight = 0.3

        priority_score = (100 - progress_percentage) * progress_weight

        logger.info(f"DAYS: {days_until_delivery}")
        logger.info(f"WEIGHT: {progress_weight}")
        logger.info(f"PROGRESS: {progress_percentage}")
        logger.info(f"PRIORITY SCORE: {priority_score}\n")

        if priority_score >= URGENT_PRIORITY_THRESHOLD:
            return PriorityEnum.URGENT
        elif priority_score >= HIGH_PRIORITY_THRESHOLD:
            return PriorityEnum.HIGH
        elif priority_score >= MEDIUM_PRIORITY_THRESHOLD:
            return PriorityEnum.MEDIUM
        else:
            return PriorityEnum.LOW

    def _update_mold_progress(self, mold_id: str) -> None:
        mold = self._get_mold_or_404(mold_id)

        active_parts = [p for p in mold.mold_parts if p.is_active]

        progress_percentage = self._calculate_mold_progress_percentage(active_parts)

        mold.priority_updated_at = date.today()
        mold.priority = self.calculate_priority(
            mold.delivery_date, progress_percentage
        )
        mold.status = self._define_status(progress_percentage)
        mold.progress_percentage = progress_percentage

        return self.mold_repo.update_mold(mold)

    @staticmethod
    def _calculate_mold_progress_percentage(active_parts: list[Part]) -> float:
        total = len(active_parts)
        status_weights = {
            ItemStatusEnum.COMPLETED: 1,
            ItemStatusEnum.IN_PROGRESS: 0.5,
            ItemStatusEnum.PENDING: 0,
        }
        done = sum(status_weights.get(ap.status, 0) for ap in active_parts)

        return round((done / total) * 100, 2) if total > 0 else 0

    @staticmethod
    def _calculate_part_progress_percentage(
        active_operations: list[OperationAssociation],
        active_material: list[MaterialPart],
        model_3d: SimpleStatusEnum,
        nc_program: SimpleStatusEnum,
    ) -> float:
        total = len(active_operations) + len(active_material) + 2
        done = (
            sum(1 for oa in active_operations if oa.status == OpStatusEnum.COMPLETED)
            + sum(
                1
                for m in active_material
                if m.status == MaterialStatusEnum.AVAILABLE
            )
            + (1 if model_3d == SimpleStatusEnum.APPROVED else 0)
            + (1 if nc_program == SimpleStatusEnum.APPROVED else 0)
        )
        return round((done / total) * 100, 2) if total > 0 else 0

    @staticmethod
    def _define_status(progress_percentage: float) -> ItemStatusEnum:
        return (
            ItemStatusEnum.COMPLETED
            if progress_percentage == COMPLETED_PERCENTAGE
            else ItemStatusEnum.IN_PROGRESS
            if progress_percentage > 0
            else ItemStatusEnum.PENDING
        )

    def _get_part_or_404(self, id: str) -> Part:
        part = self.part_repo.get_part_by_field('id', id)
        if not part:
            raise NotFoundError('Part not found')
        return part

    def _get_mold_or_404(self, id: str) -> Mold:
        mold = self.mold_repo.get_mold_by_field('id', id)
        if not mold:
            raise NotFoundError('Mold not found')
        return mold

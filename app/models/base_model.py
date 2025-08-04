from datetime import datetime
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseModel(DeclarativeBase):
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    disabled_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    def to_dict(self, exclude: list[str] = None) -> dict:
        """
        Converte a instância para um dicionário, excluindo campos especificados
        """
        exclude = exclude or []
        data = {}

        for column in self.__table__.columns.keys():
            if column not in exclude:
                value = getattr(self, column)
                if isinstance(value, datetime):
                    data[column] = value.isoformat()  # Formata datas
                elif isinstance(value, UUID):
                    data[column] = str(value)  # Converte UUID para string
                else:
                    data[column] = value

        return data

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel

if TYPE_CHECKING:
    from app.types.response import (
        CustomerResponse,
        MachineResponse,
        MaterialPartResponse,
        MaterialResponse,
        MoldResponse,
        OperationAssociationResponse,
        OperationResponse,
        PartResponse,
        UserResponse,
    )


class CustomerRelation(BaseModel):
    molds: Optional[List['MoldResponse']] = []


class MachineRelation(BaseModel):
    operations: Optional[List['OperationResponse']] = []


class MaterialPartRelation(BaseModel):
    material: Optional['MaterialResponse'] = None
    part: Optional['PartResponse'] = None


class MaterialRelation(BaseModel):
    part_associations: List[Optional['MaterialPartResponse']] = []
    parts: List[Optional['PartResponse']] = []


class MoldRelation(BaseModel):
    customer: Optional['CustomerResponse'] = None
    created_by: Optional['UserResponse'] = None
    mold_parts: Optional[List['PartResponse']] = []
    operation_associations: Optional[List['OperationAssociationResponse']] = []


class OperationRelation(BaseModel):
    machine: Optional['MachineResponse'] = None


class OperationAssociationRelation(BaseModel):
    operation: Optional['OperationResponse'] = None
    part: Optional['PartResponse'] = None
    mold: Optional['MoldResponse'] = None
    

class PartRelation(BaseModel):
    material_associations: Optional[List['MaterialPartResponse']] = []
    operation_associations: Optional[List['OperationAssociationResponse']] = []
    mold: Optional['MoldResponse'] = None


class UserRelation(BaseModel):
    molds_created: Optional[List['MoldResponse']] = []

from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from app.types.reponse import (
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


class CustomerRelation:
    molds: Optional[List['MoldResponse']] = []


class MachineRelation:
    operations: Optional[List['OperationResponse']] = []


class MaterialPartRelation:
    material: Optional['MaterialResponse'] = None
    part: Optional['PartResponse'] = None


class MoldRelation:
    customer: Optional['CustomerResponse'] = None
    created_by: Optional['UserResponse'] = None
    mold_parts: Optional[List['PartResponse']] = []
    operation_associations: Optional[List['OperationAssociationResponse']] = []


class OperationRelation:
    machine: Optional['MachineResponse'] = None


class PartRelation:
    material_associations: Optional[List['MaterialPartResponse']] = []
    operation_associations: Optional[List['OperationAssociationResponse']] = []
    mold: Optional['MoldResponse'] = None


CustomerRelation.model_rebuild()
MachineRelation.model_rebuild()
MaterialPartRelation.model_rebuild()
MoldRelation.model_rebuild()
PartRelation.model_rebuild()

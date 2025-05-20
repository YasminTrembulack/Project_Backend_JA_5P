
from app.models.customer import Customer
from app.models.machine import Machine
from app.models.material import Material
from app.models.material_part import MaterialPart
from app.models.mold import Mold
from app.models.operation import Operation
from app.models.operation_association import OperationAssociation
from app.models.part import Part
from app.models.user import User

from typing import List, Optional, Tuple
from sqlalchemy.sql.elements import BinaryExpression


ALLOWED_FIELDS = {
    'customer': {
        'mold': Customer.molds,
        'full_name': Customer.full_name,
        'country_code': Customer.country_code,
        'country_name': Customer.country_name,
    },
    'mold': {
        'customer': Mold.customer,
        'user': Mold.created_by,
        'part': Mold.mold_parts,
        'name': Mold.name,
        'delivery_date': Mold.delivery_date,
        'priority': Mold.priority,
        'status': Mold.status,
    },
    'machine': {
        'operation': Machine.operations,
        'name': Machine.name,
        'm_type': Machine.m_type,
        'status': Machine.status,
    },
    'material_part': {
        'material': MaterialPart.material,
        'part': MaterialPart.part,
        'status': MaterialPart.status,
        'expected_delivery_date': MaterialPart.expected_delivery_date,
    },
    'material': {
        'part': Material.parts,
        'name': Material.name,
        'description': Material.description,
        'unit_of_measure': Material.unit_of_measure,
        'stock_quantity': Material.stock_quantity,
        'lead_time': Material.lead_time,
    },
    'operation_association': {
        'operation': OperationAssociation.operation,
        'mold': OperationAssociation.mold,
        'part': OperationAssociation.part,
        'item_type': OperationAssociation.item_type,
        'status': OperationAssociation.status,
    },
    'operation': {
        'machine': Operation.machine,
        'name': Operation.name,
        'op_type': Operation.op_type,
    },
    'part': {
        'operation_association': Part.operation_associations,
        'material_part': Part.material_associations,
        'material': Part.materials,
        'mold': Part.mold,
        'name': Part.name,
        'description': Part.description,
        'status': Part.status,
        'model_3d': Part.model_3d,
        'nc_program': Part.nc_program,
    },
    'user': {
        'full_name': User.full_name,
        'email': User.email,
        'registration_number': User.registration_number,
        'role': User.role,
        'mold': User.molds_created,
    }
} 

class FilterService:
    def __init__(self):
        self.allowed_fields = ALLOWED_FIELDS
    
    def _validate_field(self, entity: str, attr: str):
        if entity not in self.allowed_fields:
            raise ValueError(f"Entidade '{entity}' não é permitida para filtro")
        if attr not in self.allowed_fields[entity]:
            raise ValueError(f"O campo '{attr}' não é permitido para a entidade '{entity}'")

    def build_filter(
        self, main_model: str, field: str, value: str
    ) -> Tuple[Optional[BinaryExpression], List]:
        if not field or not value:
            return None, []
        if '.' not in field:
            raise ValueError("O campo deve estar no formato entidade.campo (ex: customer.name)")

        entity, attr = field.split('.', 1)
        self._validate_field(entity, attr)

        column = self.allowed_fields[entity][attr]
        filter_condition = column.ilike(f"%{value}%")
        print(column)
        print(filter_condition)

        joins = []
        if entity != main_model:
            rel = self.allowed_fields[main_model].get(entity)
            if rel is None:
                raise ValueError(f"Relacionamento '{entity}' não encontrado em '{main_model}'")
            joins.append(rel)

        return filter_condition, joins
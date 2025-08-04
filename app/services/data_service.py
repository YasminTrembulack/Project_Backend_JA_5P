from io import BytesIO
from typing import Dict, List, Tuple
from sqlalchemy.orm import Session
import pandas as pd

from app.repositories.machine_repositorie import MachineRepository
from app.repositories.material_part_repositorie import MaterialPartRepository
from app.repositories.material_repositorie import MaterialRepository
from app.repositories.model_3d_repositorie import Model3DRepository
from app.repositories.mold_repositorie import MoldRepository
from app.repositories.nc_program_repositorie import NcProgramRepository
from app.repositories.operation_association_repositorie import OperationAssociationRepository
from app.repositories.operation_repositorie import OperationRepository
from app.repositories.part_repositorie import PartRepository
from app.services.progress_service import ProgressService
from app.types.enums import MaterialStatusEnum, OpStatusEnum
from app.types.payload import MachinePayload, MaterialPartPayload, MaterialPayload, Model3DPayload, MoldPayload, NcProgramPayload, OperationAssociationPayload, OperationPayload, PartPayload


all_columns = {
    'Name.2.1': 'Model_3D',
    # 'CHEGADA DO AÇO': 'Material',
    'PROGRAMA NC': 'Program_NC'
}

class DataService:
    def __init__(self, db: Session):
        self.mold_repo = MoldRepository(db)
        self.machine_repo = MachineRepository(db)
        self.part_repo = PartRepository(db)
        self.nc_program_repo = NcProgramRepository(db)
        self.model_3d_repo = Model3DRepository(db)
        self.material_repo = MaterialRepository(db)
        self.material_part_repo = MaterialPartRepository(db)
        self.operation_repo = OperationRepository(db)
        self.operation_association_repo = OperationAssociationRepository(db)
        self.progress_service = ProgressService(self.mold_repo, self.part_repo)

    def import_excel_from_bytes(self, contents: bytes, user_id: str):
        excel_file = pd.ExcelFile(BytesIO(contents))
        excel_df = pd.read_excel(excel_file, sheet_name=None)

        excel_df.pop('PADRÃO PREENCHIMENTO')
        progress_molds_df = excel_df.pop('MOLDES EM PROGRESSO')
        materials_df = excel_df.pop('CHEGADA AÇOS')
        program_df = excel_df.pop('PROGRAMAÇÃO')
        
        molds_mapped = self._create_molds_in_progress(progress_molds_df, user_id)
        
        dados_sheets = self._clean_sheets(excel_df, "DADOS ")
        m_sheets = self._clean_sheets(excel_df, "M")
        
        error = []
        
        for sheet_name, dados_df in dados_sheets.items():
            
            mold_code = sheet_name.replace('DADOS ', '')
            mold_id = molds_mapped.pop(mold_code)
            
            if not mold_id:
                error.append(
                    f"Mold {mold_code} not found in sheet 'MOLDES EM PROGRESSO'."
                )
                continue
            
            # df_materials = materials_df[materials_df["MOLDE"].astype(str) == mold_code]
            parts_presence_pivot = self._create_parts_presence_pivot(dados_df, all_columns)

            m_sheet_df = m_sheets.pop(f"M{mold_code}", None)
            
            # Verificar se a planilha existe e não está vazia
            if m_sheet_df is None or m_sheet_df.empty:
                error.append(f"A sheet with name 'M{mold_code}'not found.")
            
            items_dict = dict(
                zip(
                    m_sheet_df['Item'].astype(str),
                    zip(
                        m_sheet_df['Descrição'].astype(str),
                        m_sheet_df['Aço'].astype(str)
                    )
                )
            )

            # Converte para dicionário para busca mais eficiente (opcional)
            parts_dict = parts_presence_pivot.set_index('Part_code').to_dict('index')
            
            operation_dict = self._create_machine_and_operation_if_not_exists(dados_df)
            material_dict = self._create_material_if_not_exists(m_sheet_df)
            
            for  part_code, (description, material) in items_dict.items():
                new_name = self.part_repo.total_parts(True) + 1
                part = self.part_repo.create_part(
                    PartPayload(
                        name=str(new_name),
                        description=description,
                        mold_id=mold_id
                    )
                )
                
                part_data = parts_dict.get(part_code)
                
                if part_data is not None:
                    if part_data['Model_3D'] == '✓':
                        part.model_3d_id = self._create_model_3d()
                    
                    if part_data['Program_NC'] == '✓':
                        part.nc_program_id = self._create_nc_program(program_df, part_code)
                        
                    self.part_repo.update_part(part)
                    
                    material_line = materials_df[
                        (materials_df["REFERÊNCIA"] == part_code) &
                        (materials_df["MOLDE"] == mold_code)
                    ]
                    material_diponivel = not material_line.empty
                    self._create_material_part(part.id, material_dict[material], material_diponivel)

                    for operation_name, operation_id in operation_dict.items():
                        self._create_operation_association(
                            part.id, operation_id, part_data.get(operation_name, 'X') == '✓'
                        )
                    self.progress_service.update_part_progress(part.id)
    
    def _create_molds_in_progress(
        self, df: pd.DataFrame, user_id: str
    ) -> Dict[str, str]:
        mold_filter = df['Moldes Oficiais'].str.contains(r"^Molde\d{4,}$", regex=True, na=False)

        filtered_df = df[mold_filter]

        cleaned_molds_code = filtered_df['Moldes Oficiais'].str.replace(r"^Molde", "", regex=True)

        dates = pd.to_datetime(filtered_df['Data'], errors='coerce')

        mold_data_tuples = list(zip(cleaned_molds_code, dates))

        molds_mapped = {}
        for code, date in mold_data_tuples:  
            print(f"MOLDE: {code}  {date}")          
            mold = self.mold_repo.get_mold_by_field('name', code)
            
            if not mold:
                mold = self.mold_repo.create_mold(
                    MoldPayload(
                        name=code,
                        delivery_date=date,
                        created_by_id=user_id
                    )
                )
                
            molds_mapped[code] = mold.id
            
        return molds_mapped
            
    def _clean_sheets(self, excel_df: pd.DataFrame, prefix: str="") -> pd.DataFrame:
        return {
            name: df.dropna(how='all')
            for name, df in excel_df.items()
            if name.startswith(prefix)
        }
    
    def _create_parts_presence_pivot(
        self,
        data_df: pd.DataFrame,
        all_columns: dict,
    ) -> pd.DataFrame:
        """
        Cria um pivot table mostrando a presença de partes em diferentes colunas
        
        Args:
            data_df: DataFrame com os dados brutos
            all_columns: Dicionário mapeando {coluna_original: nome_novo}
            status_col_for_materials: Coluna com status de material (para filtro ☑)
        
        Returns:
            DataFrame pivotado com ✓/X indicando presença
        """
        values_list = []
        all_columns.update(
            dict(
                (col, col.replace('M_', ''))
                for col in data_df.columns if col.startswith('M_')
            )
        )
        for column, new_column in all_columns.items():
            temp = data_df[[column]].copy()
            
            # Renomeia e adiciona coluna de tipo
            temp = temp.rename(columns={column: 'Part_code'})
            temp['column'] = new_column
            values_list.append(temp)
        
        if not values_list:
            return pd.DataFrame()
        
        # Concatena todos os dados
        values = pd.concat(values_list, ignore_index=True)
        
        # Limpeza e conversão de IDs
        values['Part_code'] = (
            values['Part_code']
            .astype(str)
            .str.strip()
            .replace('', pd.NA)
            .dropna()
        )
        
        # Converte para numérico e depois para string padronizada
        values['Part_code'] = (
            pd.to_numeric(values['Part_code'], errors='coerce')
            .dropna()
            .astype(int)
            .astype(str)
        )
        
        # Cria pivot table (presença/ausência)
        pivot = (
            pd.crosstab(values['Part_code'], values['column'])
            .gt(0)  # Transforma em boolean (True/False)
            .replace({True: '✓', False: 'X'})  # Substitui por símbolos
            .reset_index()
        )
        
        # Filtra linhas onde pelo menos uma coluna tem '✓'
        pivot = pivot[pivot.drop('Part_code', axis=1).eq('✓').any(axis=1)]
        
        return pivot

    def _create_machine_and_operation_if_not_exists(self, dados_df: pd.DataFrame) -> Dict[str, str]:
        machines_names = [col.replace('M_', '') for col in dados_df.columns if col.startswith('M_')]
        
        machines_mapped = {}
        for m in machines_names:
            op_name = m + ' Default'
            machine = self.machine_repo.get_machine_by_field('m_type', m)
            operation = self.operation_repo.get_operation_by_field('op_type', op_name)
            if not machine and not operation:
                new_m_name = self.machine_repo.total_machine(True) + 1
                machine = self.machine_repo.create_machine(
                    MachinePayload(
                        name=str(new_m_name),
                        m_type=m
                    )
                )
                new_op_name = self.operation_repo.total_operation(True) + 1
                operation = self.operation_repo.create_operation(
                    OperationPayload(
                        name=str(new_op_name),
                        machine_id=machine.id,
                        op_type=op_name
                    )
                )
                
            machines_mapped[m] = operation.id
            
        return machines_mapped

    def _create_model_3d(self) -> str:
        new_name = self.model_3d_repo.total_model_3ds(True) + 1
        model_3d = self.model_3d_repo.create_model_3d(
            Model3DPayload(
                name=str(new_name)
            )
        )
        return model_3d.id

    def _create_material_if_not_exists(self, dados_df: pd.DataFrame) -> Dict[str, str]:
        material_names = dados_df['Aço'].astype(str).tolist()
        materials_mapped = {}
        for m in material_names:
            material = self.material_repo.get_material_by_field('description', m)
            if not material:
                new_name = self.material_repo.total_material(True) + 1
                material = self.material_repo.create_material(
                    MaterialPayload(
                        name=str(new_name),
                        description=m,
                        unit_of_measure='Un',
                        lead_time='2 Week',
                        stock_quantity=1
                    )
                )
                
            materials_mapped[m] = material.id
            
        return materials_mapped
    
    def _create_nc_program(self, program_df: pd.DataFrame, part_name: str) -> str:
        program_line = program_df[program_df["REFERENCIA"].astype(str) == part_name]

        responsavel = program_line["PROGRAMADOR"].iloc[0]
        new_name = self.nc_program_repo.total_nc_programs(True) + 1
        nc_program = self.nc_program_repo.create_nc_program(
            NcProgramPayload(
                responsible=responsavel,
                name=str(new_name)
            )
        )
        return nc_program.id
    
    def _create_material_part(self, part_id: str, material_id: str, completed: bool) -> None:
        self.material_part_repo.create_material_part(
            MaterialPartPayload(
                material_id=material_id,
                part_id=part_id,
                status=MaterialStatusEnum.AVAILABLE 
                if completed else MaterialStatusEnum.PENDING
            )
        )
        
    def _create_operation_association(self, part_id: str, operation_id: str, completed: bool) -> None:
        self.operation_association_repo.create_operation_association(
            OperationAssociationPayload(
                item_id=part_id,
                operation_id=operation_id,
                item_type='Part',
                status=OpStatusEnum.COMPLETED 
                if completed else OpStatusEnum.PENDING
            )
        )

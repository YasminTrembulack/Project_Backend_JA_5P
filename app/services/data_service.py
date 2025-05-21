from io import BytesIO
from typing import Dict, List, Tuple
from sqlalchemy.orm import Session
import pandas as pd

from app.repositories.mold_repositorie import MoldRepository
from app.types.payload import MoldPayload


class DataService:
    def __init__(self, db: Session):
        self.mold_repo = MoldRepository(db)
        ...

    def import_excel_from_bytes(self, contents: bytes, user_id: str):
        excel_file = pd.ExcelFile(BytesIO(contents))
        excel_df = pd.read_excel(excel_file, sheet_name=None)

        progress_molds_df = excel_df.pop('MOLDES EM PROGRESSO')
        materials_df = excel_df.pop('CHEGADA AÇOS')
        program_df = excel_df.pop('PROGRAMAÇÃO')
        excel_df.pop('PADRÃO PREENCHIMENTO')
        
        molds_mapped = self.create_molds_in_progress(progress_molds_df, user_id)
        print(f"Molds mapped: {molds_mapped}")
        
        for sheet_name, df in excel_df.items():
            
            mold_code = sheet_name.replace('DADOS ', '')
            df_filtrado = materials_df[materials_df["MOLDE"].astype(str) == mold_code]
            
            print(f"materials_df: {materials_df.head(4)}\n")
            print(f"Mold code: {mold_code}  DF filtrado: {df_filtrado.head(4)}\n")
            
            if df_filtrado.size <= 0:
                continue
            
            mold_id = molds_mapped.get(mold_code)
            print(f"Mold id: {mold_id}  Mold code: {mold_code}")

        
        ...
    
    def create_molds_in_progress(self, df: pd.DataFrame, user_id: str) -> Dict[str, str]:
        mold_filter = df['Moldes Oficiais'].str.contains(r"^Molde\d{4,}$", regex=True, na=False)

        filtered_df = df[mold_filter]

        cleaned_molds_code = filtered_df['Moldes Oficiais'].str.replace(r"^Molde", "", regex=True)

        dates = pd.to_datetime(filtered_df['Data'], errors='coerce')

        mold_data_tuples = list(zip(cleaned_molds_code, dates))

        for code, date in mold_data_tuples:
            # print(f"Molde: {code}, Data: {date}")
            self.mold_repo.delete_mold_by_name(code) #TODO remover isso depois
            
            mold = self.mold_repo.get_mold_by_field('name', code)
            
            molds_mapped = {}
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
            
            
            
            
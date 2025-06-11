
import pandas as pd
from pandas import DataFrame
from database.reader.ps2_reader import PS2Reader
from spec.codestate import CodeStateEntry
import os


class CSVReader(PS2Reader):

    _LINK_TABLES_DIR = "LinkTables"

    @property
    def data_config(self):
        return self.context.data_config

    def _get_table(self, path: str) -> DataFrame:
        if not os.path.exists(path):
            raise FileNotFoundError(f"No CSV file found at '{path}'.")
        return pd.read_csv(path)

    def get_main_table(self) -> DataFrame:
        path = os.path.join(self.data_config.main_table_path)
        return self._get_table(path)

    def add_codestate(self, codestate_id: str, subject_id: str, project_id: str) -> CodeStateEntry:
        pass

    def get_link_table(self, table_name) -> DataFrame:
        path = os.path.join(self.data_config.root_path, self._LINK_TABLES_DIR, f"{table_name}.csv")
        return self._get_table(path)

    def get_metadata_table(self) -> DataFrame:
        path = os.path.join(self.context.data_config.root_path, "Metadata.csv")
        return self._get_table(path)

    def get_link_table_names(self) -> list[str]:
        path = os.path.join(self.context.data_config.root_path, self._LINK_TABLES_DIR)
        if not os.path.exists(path):
            return []
        return [f[:-4] for f in os.listdir(path) if f.endswith('.csv')]
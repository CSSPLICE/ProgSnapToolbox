
import os
import pandas as pd
from pandas import DataFrame
from progsnap2.analytics.ps2_dataset import CodeStatesPreprocessor, LinkTablePreprocessor, Preprocessor
import yaml
import re
from progsnap2.spec.enums import MainTableColumns as Cols, EventType

class PcrsAddEventTypeColumn(Preprocessor):
    def apply(self, dataset, main_table):
        main_table['EventType'] = 'Submit'
        return main_table

class PcrsRenameColumns(Preprocessor):
    """
    Preprocessor that renames columns in MainTable.
    """

    def apply(self, dataset, main_table):
        columns = {'timestamp': Cols.ServerTimestamp, 'score': Cols.Score, 'problem_id': Cols.ProblemID, 'user_id': Cols.SubjectID}
        main_table.rename(columns=columns, inplace=True)
        return main_table

class PcrsFilterColumns(Preprocessor):
    """
    Preprocessor that filter section id column in MainTable.
    """

    def apply(self, dataset, main_table):
        main_table = main_table[main_table['section_id'] == 'Lecture']
        return main_table


class PcrsRenameColumnsLinkTablePreprocessor(LinkTablePreprocessor):
    def apply(self, dataset: "PS2Dataset", link_table_name, link_table: DataFrame) -> DataFrame:
        if link_table_name != "Grades":
            return link_table
        link_table.rename(columns={'AnonID': 'grades_ID', 'Term Test 1': 'Midterm1', 'Term Test 2': 'Midterm2', 'Final Exam': 'Final'}, inplace=True)
        return link_table


class PcrsDropNanGradesLinkTablePreprocessor(LinkTablePreprocessor):
    def apply(self, dataset: "PS2Dataset", link_table_name, link_table: DataFrame) -> DataFrame:
        if link_table_name != "Grades":
            return link_table
        link_table.dropna(subset=['grades_ID'], inplace=True)
        return link_table


class PcrsReplaceMissingGradesLinkTablePreprocessor(LinkTablePreprocessor):
    def apply(self, dataset: "PS2Dataset", link_table_name, link_table: DataFrame) -> DataFrame:
        if link_table_name != "Grades":
            return link_table

        if 'Midterm1' in link_table.columns:
            link_table["Midterm1"] = link_table["Midterm1"].replace("MISSING", 0.0).astype(float)
        if 'Midterm2' in link_table.columns:
            link_table["Midterm2"] = link_table["Midterm2"].replace("MISSING", 0.0).astype(float)
        if 'Final' in link_table.columns:
            link_table["Final"] = link_table["Final"].replace("MISSING", 0.0).astype(float)
        return link_table


class PcrsFilterWithIDMappingLinkTablePreprocessor(LinkTablePreprocessor):

    def __init__(self, id_mapping_file: str):
        self.id_mapping_file = id_mapping_file

    def apply(self, dataset: "PS2Dataset", link_table_name, link_table: DataFrame) -> DataFrame:
        if link_table_name != "Grades":
            return link_table
        
        # load ID mapping file
        path = os.path.join(dataset.data_config.root_path, self.id_mapping_file)
        id_mapping = pd.read_csv(path, dtype=str)
        id_mapping.rename(columns={'PCRS_ID': Cols.SubjectID}, inplace=True)

        # drop rows with SubjectID='-'
        id_mapping = id_mapping[id_mapping[Cols.SubjectID] != '-']

        # make sure both are int
        id_mapping.grades_ID = id_mapping.grades_ID.astype(int)
        link_table.grades_ID = link_table.grades_ID.astype(int)

        # merge with linktable
        link_table = pd.merge(link_table, id_mapping, how='inner', on='grades_ID')
        link_table[Cols.SubjectID] = link_table[Cols.SubjectID].astype(int)

        return link_table


class PcrsStripCodeSHAPreprocessor(CodeStatesPreprocessor):
    
    _LEADING_SHA_RE = re.compile(r"^[a-f0-9]{40}\s*\n?")
    _TRAILING_SHA_RE = re.compile(r"\s*[a-f0-9]{40}\s*\n$")

    def __init__(self, code_col: str = "Code", cleaned_code_col: str = "Code"):
        self.code_col = code_col
        self.cleaned_code_col = cleaned_code_col

    def _clean_code(self, code):
        if not isinstance(code, str):
            return ""

        code = self._LEADING_SHA_RE.sub("", code)
        code = self._TRAILING_SHA_RE.sub("", code)
        return code

    def apply(self, dataset, codestates: DataFrame, subset: DataFrame=None) -> DataFrame:
        try:
            from pandarallel import pandarallel

            pandarallel.initialize(progress_bar=True)
            codestates[self.cleaned_code_col] = codestates[self.code_col].parallel_apply(self._clean_code)
        except ImportError:
            codestates[self.cleaned_code_col] = codestates[self.code_col].apply(self._clean_code)

        return codestates

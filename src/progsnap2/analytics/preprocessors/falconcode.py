
import os
import pandas as pd
from pandas import DataFrame
from progsnap2.analytics.ps2_dataset import CodeStatesPreprocessor, Preprocessor, LinkTablePreprocessor
from progsnap2.spec.enums import MainTableColumns as Cols

class FalconRenameColumnsPreprocessor(Preprocessor):
    """
    Preprocessor that renames column names to match the ones in the spec
    """
    def apply(self, dataset: "PS2Dataset", main_table: DataFrame):
        main_table.rename(columns={"score": "Score", "code_hash": "CodeStateID", 'student_id': Cols.SubjectID, 'problem_id': Cols.ProblemID, 'timestamp': Cols.ServerTimestamp}, inplace=True)
        return main_table

class FalconRemoveGradesOutliers(LinkTablePreprocessor):
    """
    Preprocessor that removes grades outliers
    """

    def __init__(self, gradeOutlierValue: int):
        self.gradeOutlierValue = gradeOutlierValue

    def apply(self, dataset: "PS2Dataset", link_table_name, link_table: DataFrame) -> DataFrame:
        if "Grade" not in link_table.columns:
            return link_table

        # students who have score more than 1900 are probably outliers
        print(f"Dropping {link_table[link_table['Grade'] >= self.gradeOutlierValue].shape[0]} rows equal/higher than {self.gradeOutlierValue}")
        link_table = link_table[link_table["Grade"] <= self.gradeOutlierValue].copy()

        return link_table

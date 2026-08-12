
import os
import pandas as pd
from pandas import DataFrame
from progsnap2.analytics.ps2_dataset import CodeStatesPreprocessor, Preprocessor
from progsnap2.spec.enums import MainTableColumns as Cols


class EOLConvertScoresPreprocessor(Preprocessor):
    """
    Preprocessor that converts the scores in the main table to numbers
    The Score column is in this format "score | total". So we need to split it into two columns and convert it to numeric
    """
    def apply(self, dataset: "PS2Dataset", main_table: DataFrame):
        # if score is string split it
        if main_table["Score"].dtype == object:
            main_table["Score"] = main_table["Score"].str.split("|").str[0]

        # For all datasets, convert it to numeric
        main_table["Score"] = pd.to_numeric(main_table["Score"], errors='coerce')
        return main_table


class EOLDropProblemsPreprocessor(Preprocessor):
    """
    Preprocessor that drops specific problems from the main table
    """
    def __init__(self, problem_id_col: str = Cols.ProblemID, problem_ids: list = None):
        self.problem_id_col = problem_id_col
        self.problem_ids = problem_ids

    def apply(self, dataset: "PS2Dataset", main_table: DataFrame):
        main_table = main_table[~main_table[self.problem_id_col].isin(self.problem_ids)]
        return main_table


class EOLNormalizeCodeStateIDsPreprocessor(CodeStatesPreprocessor):
    """
    Preprocessor that normalizes the CodeStateIDs in the Codestates table to match the ones in the main table
    """

    def __init__(self, codestatesID_col: str = Cols.CodeStateID):
        self.codestatesID_col = codestatesID_col

    def apply(self, dataset: "PS2Dataset", codestates: DataFrame, subset: DataFrame):
        # type of code state IDs in the Codestates table are different from the ones in the main table
        codestates[self.codestatesID_col] = pd.to_numeric(codestates[self.codestatesID_col], errors='coerce')
        uniqueIDs = subset[self.codestatesID_col].unique()
        codestates = codestates[codestates[self.codestatesID_col].isin(uniqueIDs)]
        return codestates
        

class EOLCleanBadCodeStatesPreprocessor(CodeStatesPreprocessor):
    """
    Preprocessor that removes rows with bad CodeStateIDs
    """

    def __init__(self, bad_codestatesIDs: list, codestatesID_col: str = Cols.CodeStateID):
        self.bad_codestatesIDs = bad_codestatesIDs
        self.codestatesID_col = codestatesID_col

    def apply(self, dataset: "PS2Dataset", codestates: DataFrame, subset: DataFrame):
        # drop codesates with bad IDs
        codestates = codestates[~codestates[self.codestatesID_col].isin(self.bad_codestatesIDs)]
        return codestates


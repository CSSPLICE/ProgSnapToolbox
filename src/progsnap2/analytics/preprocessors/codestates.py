
import os
import pandas as pd
from pandas import DataFrame
from progsnap2.analytics.ps2_dataset import CodeStatesPreprocessor, LinkTablePreprocessor, Preprocessor
import yaml
from progsnap2.spec.enums import MainTableColumns as Cols, EventType

class CodeStatesMergeWithDataSubset(CodeStatesPreprocessor):
    """
    Merges the CodeStates table with the given DataFrame on the CodeStateID column.
    """
    def __init__(self, merge_col: str=Cols.CodeStateID):
        self.merge_col = merge_col

    def apply(self, dataset: "PS2Dataset", codestates: DataFrame, data_subset: DataFrame) -> DataFrame:
        return pd.merge(data_subset, codestates, on=self.merge_col, how='inner')


class DropEmptyCodeStatesPreprocessor(CodeStatesPreprocessor):
    """
    Preprocessor that removes rows with empty code
    """

    def __init__(self, code_col: str='Code'):
        self.code_col = code_col

    def apply(self, dataset: "PS2Dataset", codestates: DataFrame, subset: DataFrame=None) -> DataFrame:
        # drop codesates with bad IDs
        return codestates[
            codestates[self.code_col]
                .fillna("")
                .str.strip()
                .ne("")
        ]
        

class SelectColumnsFromSubsetPreprocessor(Preprocessor):
    def __init__(self, columns: [str]):
        self.columns = columns

    def apply(self, dataset: "PS2Dataset", subset: DataFrame) -> DataFrame:
        return subset[self.columns]


"""
Gets the latest row with the maximum score for each SubjectID, ProblemID.
"""
def get_latest_max_score(df: DataFrame, 
    sort_by_cols: [str]=[Cols.SubjectID, Cols.ProblemID, Cols.Score, Cols.ServerTimestamp], 
    sorting_directions: [bool]=[True, True, False, False], 
    group_by_cols: [str]=[Cols.SubjectID, Cols.ProblemID]) -> DataFrame:
    return df.sort_values(sort_by_cols, ascending=sorting_directions).drop_duplicates(subset=group_by_cols, keep='first').reset_index(drop=True)

def merge_metrics_with_data_subset(dataset: DataFrame, metrics_df: DataFrame):
    return pd.concat([dataset.reset_index(drop=True), metrics_df.reset_index(drop=True)], axis=1)

def get_metrics_sum_and_averages(df: DataFrame, code_metrics_columns: [str], group_by: str=Cols.SubjectID) -> DataFrame:
    grouped = df.groupby(group_by, as_index=False)[code_metrics_columns].agg(['sum', 'mean'])
    grouped.columns = ['_'.join(col).strip('_') for col in grouped.columns.values]
    return grouped

def get_metrics_z_scores(df: DataFrame) -> DataFrame:
    from scipy import stats

    numeric_cols = df.select_dtypes(include=["number"]).columns
    # remove the SubjectID from the numeric_cols
    numeric_cols = numeric_cols.difference([Cols.SubjectID])

    df_z = df[numeric_cols].transform(lambda x: (x - x.mean()) / (x.std() if x.std() > 0 else 1))
    df_z = df[[Cols.SubjectID]].join(df_z)
    return df_z

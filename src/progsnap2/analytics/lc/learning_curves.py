from abc import ABC, abstractmethod
from enum import Enum
from progsnap2.analytics.analytics_config import AnalyticsConfig
from progsnap2.spec.enums import CodeStatesTableColumns as CSTCols, MainTableColumns as Cols
import pandas as pd

class LCResult(Enum):
    Correct = "Correct"
    Error = "Error"
    NotApplied = "Not Applied"


class KC(ABC):

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def evaluate_attempts(self, attempts: pd.DataFrame) -> LCResult:
        pass

class LearningCurveCalculator:

    def __init__(
        self,
        kcs: list[KC],
        only_first_attempt: bool = True
    ):
        self.kcs = kcs
        self.only_first_attempt = only_first_attempt

    # TODO we assume it's already sorted
    def evaluate(self, attempts: pd.DataFrame, config: AnalyticsConfig, grouping_columns = None) -> dict[str, LCResult]:
        if CSTCols.Code not in attempts.columns:
            raise ValueError(f"The attempts DataFrame must contain a '{CSTCols.Code}' column.")

        # At least for now, I can't see any reason not to
        attempts = attempts[
            attempts[CSTCols.Code].notnull() &
            attempts[Cols.EventType == config.submit_event]
        ]

        if grouping_columns is None:
            grouping_columns = config.attempt_grouping_columns

        grouped = attempts.groupby(grouping_columns)
        results = []
        for group_name, group_df in grouped:
            row = {}
            # Add each grouping column and values
            if isinstance(group_name, tuple):
                for col, val in zip(grouping_columns, group_name):
                    row[col] = val
            else:
                row[grouping_columns[0]] = group_name
            if self.only_first_attempt:
                group_df = group_df.head(1)
            for kc in self.kcs:
                result = kc.evaluate_attempts(group_df)
                if result is not LCResult.NotApplied:
                    row[kc.name] = 1 if result == LCResult.Correct else 0
            results.append(row)
        return pd.DataFrame(results)

from typing import Final
from pandas import DataFrame, Series
from analytics.metrics.metric import LambdaMetric
from spec.enums import MainTableColumns as Cols


class TimeMetrics:

    ACTIVE_TIME: Final[str] = "ActiveTime"
    """
    The time spent actively working on a problem, ignoring idle time and breaks,
    as well as time after the first correct attempt.
    """
    IDLE_TIME: Final[str] = "IdleTime"
    """
    The time spent idle, not actively working on a problem. Does not inclide breaks,
    as well as time after the first correct attempt.
    Idle time is defined as a gap of time longer than the idle_gap, but shorter than
    the break_gap.
    """
    TOTAL_TIME: Final[str] = "TotalTime"
    """
    The total time spent on a problem, including idle time, but ignoring long breaks, until
    the first correct attempt.
    """
    ACTIVE_TIME_AFTER_CORRECT: Final[str] = "ActiveTimeAfterCorrect"
    """
    The time spent actively working on a problem after the first correct attempt.
    """
    N_BREAKS: Final[str] = "#Breaks"
    """
    The number of breaks taken while working on a problem. A break is a gap of time
    longer than the break_gap.
    """

    START_TIME: Final[str] = "StartTime"
    """
    The time of the first log entry for a problem.
    """
    FIRST_CORRECT_TIME: Final[str] = "FirstCorrectTime"
    """
    The time of the first correct attempt for a problem.
    """


    def __init__(self, idle_gap, break_gap, is_data_already_time_sorted, time_col: str = Cols.ClientTimestamp):
        self.idle_gap = idle_gap
        self.break_gap = break_gap
        self.time_col = time_col
        self.sort_first = not is_data_already_time_sorted

    def calculate(self, rows: DataFrame) -> dict[str, any]:
        if self.sort_first:
            rows = rows.sort_values(by=[self.time_col])


        time_series = rows[self.time_col]

        start_time = time_series.iloc[0]

        time_series_until_correct = time_series
        time_series_after_correct = None
        correct_rows = rows[rows[Cols.Score] >= 1]
        first_correct_time = None
        if len(correct_rows) > 0:
            first_correct_loc = correct_rows.index.get_loc(correct_rows.index[0])
            first_correct_time = time_series.iloc[first_correct_loc]
            first_correct_loc += 1 # Offset by 1 to include the first correct attempt
            time_series_until_correct = time_series.iloc[:first_correct_loc]
            time_series_after_correct = time_series.iloc[first_correct_loc:]

        delta_seconds = time_series_until_correct.diff().dt.total_seconds()
        n_breaks = (delta_seconds > self.break_gap).sum()
        non_break_seconds = delta_seconds[delta_seconds <= self.break_gap]
        idle_time = non_break_seconds[non_break_seconds > self.idle_gap].sum()
        total_time = non_break_seconds.sum()
        active_time = total_time - idle_time

        active_time_after_correct = 0
        if time_series_after_correct is not None:
            delta_seconds_after_correct = time_series_after_correct.diff().dt.total_seconds()
            non_break_seconds_after_correct = delta_seconds_after_correct[delta_seconds_after_correct <= self.break_gap]
            active_time_after_correct = non_break_seconds_after_correct[non_break_seconds_after_correct <= self.idle_gap].sum()

        time_metrics = {
            self.ACTIVE_TIME: active_time,
            self.IDLE_TIME: idle_time,
            self.TOTAL_TIME: total_time,
            self.ACTIVE_TIME_AFTER_CORRECT: active_time_after_correct,
            self.N_BREAKS: n_breaks,
            self.START_TIME: start_time,
            self.FIRST_CORRECT_TIME: first_correct_time
        }
        return Series(time_metrics)

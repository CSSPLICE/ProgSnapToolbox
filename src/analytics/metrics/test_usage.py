

from pandas import DataFrame
from analytics.metrics.metric import MetricCalculator
from spec.enums import MainTableColumns as Cols

original_df = DataFrame()

generic_metrics = GenericMetrics()
score_metrics = ScoreMetrics()
time_metrics = TimeMetrics()

generic_metrics.log_count.disable()


metric_group = MetricCalculator([Cols.SubjectID, Cols.ProblemID])
result = ()

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from progsnap2.analytics.analytics_config import AnalyticsConfig
from progsnap2.spec.enums import CodeStatesTableColumns as CSTCols, MainTableColumns as Cols
import pandas as pd
import seaborn as sns

@dataclass(slots=True)
class KCEvaluation:
    correct: list[str]
    incorrect: list[str]


class KCEvaluator(ABC):

    @abstractmethod
    def evaluate_attempts(self, attempts: pd.DataFrame) -> KCEvaluation:
        pass

class LearningCurveCalculator:

    def __init__(
        self,
        kc_evaluator: KCEvaluator,
        attempts: pd.DataFrame,
        config: AnalyticsConfig,
        grouping_columns = None,
        only_first_attempt: bool = True
    ):
        self.kc_evaluator = kc_evaluator
        self.only_first_attempt = only_first_attempt
        self.attemps = attempts
        self.config = config
        self.grouping_columns = grouping_columns if grouping_columns is not None else config.attempt_grouping_columns
        self.results = self._evaluate()
        self.kcs = self.results["kc"].unique()

    def plot_most_common_kcs(self, n: int = 10, min_subjects = 5):
        most_common_kcs = self.results.groupby("kc")["SubjectID"].nunique().nlargest(n).index
        # plot them on a facet grid
        g = sns.FacetGrid(self.results[self.results["kc"].isin(most_common_kcs)], col="kc", col_wrap=3, sharex=False, sharey=True)
        g.map_dataframe(self._plot_kc_internal, min_subjects=min_subjects)
        g.set_titles("{col_name}")
        return g

    def _plot_kc_internal(self, data, color=None, min_subjects = 5, **kwargs):
        data = data[data.groupby("opportunity")["SubjectID"].transform("nunique") >= min_subjects]
        plot = sns.lineplot(data=data, x="opportunity", y="error", errorbar=("ci", 95), n_boot=1000, estimator="mean")
        counts = data.groupby("opportunity")["SubjectID"].nunique().reset_index(name="n_subjects")
        counts_ax = plot.twinx()
        sns.lineplot(data=counts, x="opportunity", y="n_subjects", color="orange", label="n", ax=counts_ax, alpha=0.5)
        return plot

    def plot_kc(self, kc: str, min_subjects = 5):
        data = self.results[self.results["kc"] == kc]
        self._plot_kc_internal(data, min_subjects=min_subjects)

        # plot_data = []
        # for i in range(1, data["opportunity"].max() + 1):
        #     opportunity_data = data[data["opportunity"] == i]
        #     if len(opportunity_data) < min_subjects:
        #         break
        #     correct_count = opportunity_data["correct"].sum()
        #     total_count = len(opportunity_data)
        #     error = 1 - (correct_count / total_count)
        #     plot_data.append({
        #         "opportunity": i,
        #         "n": total_count,
        #         "error": error,
        #     })


    # TODO we assume it's already sorted
    def _evaluate(self) -> pd.DataFrame:
        if CSTCols.Code not in self.attemps.columns:
            raise ValueError(f"The attempts DataFrame must contain a '{CSTCols.Code}' column.")

        # At least for now, I can't see any reason not to
        attempts = self.attemps[
            self.attemps[CSTCols.Code].notnull() &
            (self.attemps[Cols.EventType] == self.config.submit_event)
        ]

        grouping_columns = self.grouping_columns
        grouped = attempts.groupby(grouping_columns)
        results = []
        for group_name, group_df in grouped:
            row_base = {}
            # Add each grouping column and values
            if isinstance(group_name, tuple):
                for col, val in zip(grouping_columns, group_name):
                    row_base[col] = val
            else:
                row_base[grouping_columns[0]] = group_name
            if self.only_first_attempt:
                group_df = group_df.head(1)
            eval = self.kc_evaluator.evaluate_attempts(group_df)
            for outcome, kcs in zip([1, 0], [eval.correct, eval.incorrect]):
                for kc in kcs:
                    row = row_base.copy()
                    row["kc"] = kc
                    row["correct"] = outcome
                    results.append(row)
            results.append(row_base)

        result_df = pd.DataFrame(results)
        result_df["error"] = 1 - result_df["correct"]
        result_df["opportunity"] = 0
        for _, group in result_df.groupby(["SubjectID", "kc"]):
            result_df.loc[group.index, "opportunity"] = list(range(1, len(group) + 1))
        return result_df


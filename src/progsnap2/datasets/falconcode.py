from progsnap2.analytics.analytics_config import AnalyticsConfig, Granularity, ProgrammingLanguage
from progsnap2.analytics.ps2_dataset import SortPreprocessor, ConvertTimestampPreprocessor, NormalizeGradesLinkTablePreprocessor, SortDatasetAscendingPreprocessor
from progsnap2.database.config import PS2DataConfig
from progsnap2.spec.enums import MainTableColumns as Cols, EventType, CoreTables
from progsnap2.analytics.metrics.code import PythonCodeMetricsProcessor
from progsnap2.analytics.preprocessors.codestates import CodeStatesMergeWithDataSubset
from progsnap2.analytics.preprocessors.falconcode import FalconRenameColumnsPreprocessor, FalconRemoveGradesOutliers

from dataclasses import replace

maintable = CoreTables.MainTable
old = maintable.value
del CoreTables._value2member_map_[old]
maintable._value_ = "runs"
CoreTables._value2member_map_["runs"] = maintable

# Falconcode DB has a different name for the CodeStates table
codestates = CoreTables.CodeStates
old = codestates.value
del CoreTables._value2member_map_[old]
codestates._value_ = "source_code"
CoreTables._value2member_map_["source_code"] = codestates



def _create_data_config(root_path: str):
    return PS2DataConfig(
        root_path=root_path,
        # TODO: Maybe rename to DatasetMetadata and .sqlite3 for consistency when releasing?
        metadata_table_name="Metadata",
        # main_table_file="MainTable.csv",
        sqlalchemy_url=f"mysql+pymysql://root:password@localhost:3306/falcondb_v1",
    )

_base_name = "falconcode"

_base_config = AnalyticsConfig(
    name=_base_name,
    programming_language=ProgrammingLanguage.Python,
    granularity=Granularity.Submission,

    primary_timestamp_column=Cols.ServerTimestamp,
    main_table_preprocessors=[
        SortPreprocessor(),
        FalconRenameColumnsPreprocessor(),
        ConvertTimestampPreprocessor(),
        SortDatasetAscendingPreprocessor(subject_id_col=Cols.SubjectID, problem_id_col=Cols.ProblemID, timestamp_col=Cols.ServerTimestamp),
    ],    
    
    link_table_preprocessors=[
        NormalizeGradesLinkTablePreprocessor(),
    ],

    code_metrics_processor=PythonCodeMetricsProcessor(code_col="source_code"),


    submit_event = EventType.RunProgram,
    final_grade_column="Grade",
) 

S21 = replace(_base_config,
    name=f"{_base_name}_s21",
    create_data_config=_create_data_config,
    start_time="2021-01-07 03:11:28",
    end_time="2021-05-10 00:00:00",
    early_time="2021-02-06 20:23:36",
)
# should be added at the beginning before the normalizer 
S21.link_table_preprocessors = [FalconRemoveGradesOutliers(gradeOutlierValue=2500)] + _base_config.link_table_preprocessors

F21 = replace(_base_config,
    name=f"{_base_name}_f21",
    create_data_config=_create_data_config,
    start_time="2021-07-22 21:04:55",
    end_time="2021-12-03 00:00:00",
    early_time="2021-08-27 19:42:35",
)
# should be added at the beginning before the normalizer 
F21.link_table_preprocessors = [FalconRemoveGradesOutliers(gradeOutlierValue=1900)] + _base_config.link_table_preprocessors

S22 = replace(_base_config,
    name=f"{_base_name}_s22",
    create_data_config=_create_data_config,
    start_time="2022-01-03 19:16:19",
    end_time="2022-05-10 00:00:00", 
    early_time="2022-02-05 14:44:28",
)
# should be added at the beginning before the normalizer 
S22.link_table_preprocessors = [FalconRemoveGradesOutliers(gradeOutlierValue=1900)] + _base_config.link_table_preprocessors

from progsnap2.analytics.analytics_config import AnalyticsConfig, Granularity, ProgrammingLanguage
from progsnap2.analytics.ps2_dataset import SortPreprocessor, ConvertTimestampPreprocessor, NormalizeGradesLinkTablePreprocessor, SortDatasetAscendingPreprocessor
from progsnap2.analytics.metrics.code import PythonCodeMetricsProcessor
from progsnap2.analytics.preprocessors.codestates import CodeStatesMergeWithDataSubset, DropEmptyCodeStatesPreprocessor
from progsnap2.analytics.preprocessors.eol import EOLConvertScoresPreprocessor, EOLDropProblemsPreprocessor, EOLNormalizeCodeStateIDsPreprocessor, EOLCleanBadCodeStatesPreprocessor
from progsnap2.database.config import PS2DataConfig
from progsnap2.spec.enums import MainTableColumns as Cols, EventType, CoreTables
from dataclasses import replace

# EOL DB has a different name for the CodeStates table
codestates = CoreTables.CodeStates
old = codestates.value
del CoreTables._value2member_map_[old]
codestates._value_ = "CodeState"
CoreTables._value2member_map_["CodeState"] = codestates

def _create_data_config(root_path: str):
    return PS2DataConfig(
        root_path=root_path,
        # TODO: Maybe rename to DatasetMetadata and .sqlite3 for consistency when releasing?
        metadata_table_name="Metadata",

        sqlalchemy_url=f"sqlite:///{root_path}/../eol_filtered_v5_2.db", #update this
    )

_base_name = "eol"
EventType.XSubmission_LMS = 'X-Submission.LMS'

_base_config = AnalyticsConfig(
    name=_base_name,
    granularity=Granularity.Edit,

    primary_timestamp_column=Cols.ClientTimestamp,
    primary_problem_grouping_column=Cols.AssignmentID,
        
    main_table_preprocessors=[
        SortPreprocessor(),
        ConvertTimestampPreprocessor(),
        EOLDropProblemsPreprocessor(problem_id_col=Cols.AssignmentID, problem_ids=["sneks_mock_midterm1_f21_question1", "sneks_mock_midterm1_f21_question2"]),
        EOLConvertScoresPreprocessor(),
        SortDatasetAscendingPreprocessor(subject_id_col=Cols.SubjectID, problem_id_col=Cols.AssignmentID, timestamp_col=Cols.ClientTimestamp),
    ],
    codestates_preprocessors=[
        EOLNormalizeCodeStateIDsPreprocessor(),
        DropEmptyCodeStatesPreprocessor(code_col="Contents"),
        CodeStatesMergeWithDataSubset(merge_col=Cols.CodeStateID),
    ],
    code_metrics_processor=PythonCodeMetricsProcessor(code_col="Contents"),

    submit_event = EventType.XSubmission_LMS,

    # compile_error_type_column="ProgramErrorOutput",
    # compile_event=EventType.XSubmission_LMS,
    # compile_error_event=EventType.RunProgram,
    compile_error_type_column = Cols.CompileMessageType,
    compile_event = EventType.Compile,
    compile_error_event = EventType.CompileError,

    grades_link_table_name=None,
    final_grade_column=None,
    programming_language=ProgrammingLanguage.Python,
)

F22_106 = replace(_base_config,
    name=f"{_base_name}_106f22",
    create_data_config=_create_data_config,
    start_time="2022-08-28 15:32:24",
    end_time="2022-12-06 23:59:54",
    early_time="2022-09-17 17:13:54.30",
)
#In eol F22 106 - looks like this student does not have any code state data
# remove rows where CodeStateID is equal 84957
F22_106.codestates_preprocessors = _base_config.codestates_preprocessors + [EOLCleanBadCodeStatesPreprocessor(bad_codestatesIDs=[84957])]


S23_106 = replace(_base_config,
    name=f"{_base_name}_106s23",
    create_data_config=_create_data_config,
    start_time="2023-02-06 18:20:02",
    end_time="2023-05-02 20:33:43",
    early_time="2023-02-23 18:46:46",
)

F23_106 = replace(_base_config,
    name=f"{_base_name}_106f23",
    create_data_config=_create_data_config,
    start_time="2023-08-26 19:43:03",
    end_time="2023-11-14 23:48:08",
    early_time="2023-09-11 20:32:04",

)

S24_106 = replace(_base_config,
    name=f"{_base_name}_106s24",
    create_data_config=_create_data_config,
    start_time="2024-02-02 19:41:12",
    end_time="2024-04-26 23:59:59",
    early_time="2024-02-19 15:44:57",
)

F22_108 = replace(_base_config,
    name=f"{_base_name}_108f22",
    create_data_config=_create_data_config,
    start_time="2022-08-28 08:29:22",
    end_time="2022-12-07 23:59:59",
    early_time="2022-09-17 16:23:29",
)

S23_108 = replace(_base_config,
    name=f"{_base_name}_108s23",
    create_data_config=_create_data_config,
    start_time="2023-02-05 16:28:10",
    end_time="2023-05-11 23:57:49",
    early_time="2023-02-24 17:58:06",
)

F23_108 = replace(_base_config,
    name=f"{_base_name}_108f23",
    create_data_config=_create_data_config,
    start_time="2023-08-27 14:16:02",
    end_time="2023-11-17 21:43:40",
    early_time="2023-09-13 01:21:34",
)

S24_108 = replace(_base_config,
    name=f"{_base_name}_108s24",
    create_data_config=_create_data_config,
    start_time="2024-02-02 15:20:48",
    end_time="2024-04-30 22:18:49",
    early_time="2024-02-20 07:08:24",
)
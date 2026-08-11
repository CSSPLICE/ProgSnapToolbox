from progsnap2.analytics.analytics_config import AnalyticsConfig, Granularity, ProgrammingLanguage
from progsnap2.database.config import PS2DataConfig
from progsnap2.analytics.ps2_dataset import LinkTablePreprocessor, PS2Dataset, Preprocessor, SortPreprocessor, ConvertTimestampPreprocessor, NormalizeGradesLinkTablePreprocessor, RenameFinalGradesColumnLinkTablePreprocessor, SortDatasetAscendingPreprocessor
from progsnap2.spec.enums import MainTableColumns as Cols, EventType
from progsnap2.analytics.preprocessors.pcrs import PcrsRenameColumns, PcrsFilterColumns, PcrsAddEventTypeColumn, PcrsRenameColumnsLinkTablePreprocessor, PcrsReplaceMissingGradesLinkTablePreprocessor, PcrsDropNanGradesLinkTablePreprocessor, PcrsFilterWithIDMappingLinkTablePreprocessor, PcrsStripCodeSHAPreprocessor
from progsnap2.analytics.metrics.code import PythonCodeMetricsProcessor
from dataclasses import replace

from progsnap2.spec.metadata import MetadataValues

def _create_data_config(root_path: str):
    return PS2DataConfig(
        root_path=root_path,
        main_table_file="MainTable.csv",

        # Students' code is stored in the main table
        codestates_in_maintable=True,

        # These datasets don't provide metadata, so we create one that mostly
        # using defaults
        metadata=MetadataValues(
            IsEventOrderingConsistent=True,
            EventOrderScope="Global",
            #CodeStateRepresentation="Keystroke",
        )
    )

_base_name = "pcrs"


_base_config = AnalyticsConfig(
    name=_base_name,
    create_data_config=_create_data_config,
    programming_language=ProgrammingLanguage.Java,

    granularity=Granularity.Submission,

    primary_timestamp_column=Cols.ServerTimestamp,
    main_table_preprocessors=[
        PcrsRenameColumns(),
        PcrsAddEventTypeColumn(),
        ConvertTimestampPreprocessor(),
        PcrsFilterColumns(),
        SortPreprocessor(Cols.ServerTimestamp),
        SortDatasetAscendingPreprocessor(subject_id_col=Cols.SubjectID, problem_id_col=Cols.ProblemID, timestamp_col=Cols.ServerTimestamp),
    ],

    grades_link_table_name="Grades",
    link_table_preprocessors=[
        RenameFinalGradesColumnLinkTablePreprocessor(final_grade_column="Final", new_grade_column="Grade"),
        NormalizeGradesLinkTablePreprocessor(),
        PcrsRenameColumnsLinkTablePreprocessor(),
        PcrsDropNanGradesLinkTablePreprocessor(),
        PcrsReplaceMissingGradesLinkTablePreprocessor(),
        PcrsFilterWithIDMappingLinkTablePreprocessor(id_mapping_file="full_id_mapping.csv"),
    ],

    codestates_preprocessors=[
        PcrsStripCodeSHAPreprocessor(code_col="submission", cleaned_code_col="Code"),
    ],

    code_metrics_processor=PythonCodeMetricsProcessor(code_col="Code"),

    submit_event = EventType.Submit,


    compile_error_type_column="ProgramErrorOutput",
    compile_event=EventType.Submit,
    compile_error_event=EventType.RunTest,

    final_grade_column="Final",
)

F23 = replace(_base_config,
    name=f"{_base_name}_f23",
    start_time="2023-09-06 01:15:40",
    end_time=None,
    early_time="2023-09-24 19:00:00",
)

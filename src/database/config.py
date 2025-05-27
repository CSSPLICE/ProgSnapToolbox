

import os
from typing import Optional
from pydantic import BaseModel, create_model, model_validator
import yaml

from spec.spec_definition import Metadata, ProgSnap2Spec

def create_metadata_values_model(metadata_spec: Metadata) -> type[BaseModel]:
    fields = {}
    for property in metadata_spec.properties:
        fields[property.name] = (Optional[property.datatype.python_type], property.default_value)
    return create_model("MetadataValues", **fields)

class PS2DataConfig(BaseModel):
    root_path: str
    """The root directory of the PrgoSnap2 dataset."""

    # TODO: It doesn't really make sense to include this in the config
    # especially for reading, since it would be provided by the dataset!
    metadata: object

    # TODO: This also doesn't really make sense for reading
    optimize_codestate_ids: bool
    """If true, provided CodeStateIDs are assumed to be local
    to each logging call and will be regenerated to be globally
    unique. If false, the provided CodeStateIDs are used directly.
    """

    # Config for CSV format
    csv_path: str = None

    # Config for SQL/SQLite format
    sqlalchemy_url: str = None
    short_str_length: int = 255
    path_str_length: int = 2048
    echo: bool = False

    @property
    def is_sql_config(self) -> bool:
        return self.sqlalchemy_url is not None

    @property
    def is_csv_config(self) -> bool:
        return self.csv_path is not None

    @model_validator(mode="after")
    def validate_has_path_or_url(cls, values):
        if not values.csv_path and not values.sqlalchemy_url:
            raise ValueError("Either csv_path or sqlalchemy_url must be provided.")
        if values.csv_path and values.sqlalchemy_url:
            raise ValueError("Only one of csv_path or sqlalchemy_url can be provided.")
        return values

    @property
    def codestates_dir(self) -> str:
        return os.path.join(self.root_path, "CodeStates")

    def validate_metadata(self, spec: ProgSnap2Spec) -> bool:
        metadata_class = create_metadata_values_model(spec.metadata)
        try:
            self.metadata = metadata_class(**self.metadata)
            return True
        except ValueError as e:
            print(f"Metadata validation error: {e}")
            return False

    @classmethod
    def from_yaml(cls, yaml_path: str, spec: ProgSnap2Spec) -> "PS2DataConfig":
        with open(yaml_path, "r") as file:
            data = yaml.safe_load(file)
        config = cls(**data)
        config.validate_metadata(spec)
        return config


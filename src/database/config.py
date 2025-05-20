

import os
from typing import Optional
from pydantic import BaseModel, create_model
import yaml

from spec.spec_definition import Metadata, ProgSnap2Spec

def create_metadata_values_model(metadata_spec: Metadata) -> type[BaseModel]:
    fields = {}
    for property in metadata_spec.properties:
        fields[property.name] = (property.datatype.python_type, property.default_value)
    return create_model("MetadataValues", **fields)

class PS2DataConfig(BaseModel):
    root_path: str
    """The root directory of the PrgoSnap2 dataset."""

    metadata: object

    optimize_codestate_ids: bool
    """If true, provided CodeStateIDs are assumed to be local
    to each logging call and will be regenerated to be globally
    unique. If false, the provided CodeStateIDs are used directly.
    """

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
    def from_yaml(cls, yaml_path: str, spec: ProgSnap2Spec = None) -> "PS2DataConfig":
        with open(yaml_path, "r") as file:
            data = yaml.safe_load(file)
        config = cls(**data)
        if spec:
            config.validate_metadata(spec)
        return config

class PS2CSVConfig(PS2DataConfig):
    csv_path: str

class PS2DatabaseConfig(PS2DataConfig):
    sqlalchemy_url: str
    id_str_length: int = 255
    enum_str_length: int = 255
    path_str_length: int = 2048
    echo: bool = False

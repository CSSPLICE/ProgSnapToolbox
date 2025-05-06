

import yaml
from pydantic import BaseModel, create_model

from progsnap2.database.config import PS2CSVConfig, PS2DatabaseConfig, create_metadata_values_model
from progsnap2.spec.spec_definition import ProgSnap2Spec


class CORSConfig(BaseModel):
    allow_origins: list[str] = ["*"]
    allow_credentials: bool = True
    allow_methods: list[str] = ["*"]
    allow_headers: list[str] = ["*"]

class PS2APIConfigBase(BaseModel):
    database_config: PS2DatabaseConfig | PS2CSVConfig

    add_server_timestamps: bool = True
    cors_config: CORSConfig = CORSConfig()

def generate_ps2_api_config_class(ps2_spec: ProgSnap2Spec) -> type[PS2APIConfigBase]:
    fields = {
        'metadata': create_metadata_values_model(ps2_spec.Metadata),
    }
    return create_model("PS2APIConfig", __base__=PS2APIConfigBase, **fields)


def load_api_config(yaml_path: str, ps2_spec: ProgSnap2Spec) -> PS2APIConfigBase:
    with open(yaml_path, "r", encoding='utf-8') as file:
        data = yaml.safe_load(file)
        PS2APIConfig = generate_ps2_api_config_class(ps2_spec)
        return PS2APIConfig(**data)
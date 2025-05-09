
from sqlalchemy import create_engine
from database.setup import create_tables_from_schema
from spec.gen_client import generate_ts_methods
from spec.gen_enums import generate_enums_for_spec
from spec.spec_definition import load_spec

if __name__ == "__main__":
    # Load schema
    schema = load_spec("progsnap2/spec/progsnap2.yaml")

    out = generate_enums_for_spec(schema)
    with open("progsnap2/spec/enums.py", "w") as f:
        f.write(out)

    out = generate_ts_methods(schema)
    # print(out)

    # Connect to database
    engine = create_engine("sqlite:///example.db", echo=True)

    # Create tables
    create_tables_from_schema(schema, engine)
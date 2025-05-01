
from sqlalchemy import create_engine
from progsnap2.database.setup import create_tables_from_schema, load_schema
from progsnap2.spec.gen_client import generate_ts_methods
from progsnap2.spec.spec_definition import load_spec

if __name__ == "__main__":
    # Load schema
    schema = load_spec("progsnap2/spec/progsnap2.yaml")

    out = generate_ts_methods(schema)
    print(out)

    # Connect to database
    # engine = create_engine("sqlite:///example.db", echo=True)

    # Create tables
    # create_tables_from_schema(schema, engine)
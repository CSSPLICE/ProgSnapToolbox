
from sqlalchemy import create_engine
from progsnap2.database.setup import create_tables_from_schema, load_schema


if __name__ == "__main__":
    # Load schema
    schema = load_schema("progsnap2/spec/progsnap2.yaml")

    # Connect to database
    engine = create_engine("sqlite:///example.db", echo=True)

    # Create tables
    create_tables_from_schema(schema, engine)

from api.config import PS2APIConfigBase
from api.events import DataModelGenerator
from database.db_writer_factory import create_db_writer_factory


class ProgSnap2API:
    def __init__(self, config: PS2APIConfigBase):
        self.config = config
        self.db_writer_factory = create_db_writer_factory(config)

    def initialize_or_update_tables(self):
        """
        Initialize or update the tables in the database.
        """
        pass

    def add_event(self, event):
        pass
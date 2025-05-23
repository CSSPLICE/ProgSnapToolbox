
import os
import pytest

from database.config import PS2DatabaseConfig
from database.writer.db_writer_factory import SQLIOFactory
from spec.spec_definition import PS2Versions, ProgSnap2Spec

current_dir = os.path.dirname(os.path.abspath(__file__))

@pytest.fixture(scope="session", autouse=True)
def run_clean_temp_dir():
    # Cleanup the temporary directory before running tests
    cleanup_temp_dir()

@pytest.fixture(scope="session")
def ps2_spec() -> ProgSnap2Spec:
    spec = PS2Versions.v1_0.load()
    return spec

@pytest.fixture(scope="session")
def sqlite_config(ps2_spec) -> PS2DatabaseConfig:
    data_config = os.path.join(current_dir, "sqlite_config.yaml")
    return PS2DatabaseConfig.from_yaml(data_config, ps2_spec)


@pytest.fixture(scope="session")
def sqlite_writer_factory(ps2_spec, sqlite_config):
    return SQLIOFactory(ps2_spec, sqlite_config)


TEMP_DIR = "test_data"

def cleanup_temp_dir():
    # Clean up the temporary directory from prior tests
    import shutil
    import stat
    import shutil
    import errno

    # TODO: Warn/error if file is actually in use...
    def handle_remove_readonly(func, path, exc):
        print (f"Error removing {path}: {exc}")
        excvalue = exc[1]
        if func in (os.rmdir, os.remove, os.unlink) and excvalue.errno == errno.EACCES:
            print(f"Changing permissions of {path} to writable")
            os.chmod(path, stat.S_IWRITE)
            func(path)
        else:
            raise

    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR, onerror=handle_remove_readonly)
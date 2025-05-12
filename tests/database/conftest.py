
import os
import pytest

from database.config import PS2DatabaseConfig
from spec.spec_definition import ProgSnap2Spec

current_dir = os.path.dirname(os.path.abspath(__file__))

@pytest.fixture(scope="session")
def ps2_spec() -> ProgSnap2Spec:
    spec_path = "src/spec/progsnap2.yaml"
    spec = ProgSnap2Spec.from_yaml(spec_path)
    return spec

@pytest.fixture(scope="session")
def sqlite_config(ps2_spec) -> PS2DatabaseConfig:
    data_config = os.path.join(current_dir, "sqlite_config.yaml")
    return PS2DatabaseConfig.from_yaml(data_config, ps2_spec)


TEMP_DIR = "test_data/codestates"

def cleanup_temp_dir():
    # Clean up the temporary directory from prior tests
    import shutil
    import stat
    import shutil
    import errno

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
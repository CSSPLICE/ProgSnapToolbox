import os, sys

src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))
sys.path.insert(0, src_path)

from progsnap2.spec.gen.gen_client import generate_ts_methods
from progsnap2.spec.gen.gen_enums import generate_enums_for_spec
from progsnap2.spec.spec_definition import PS2Versions
import pyperclip

if __name__ == "__main__":
    # Load schema
    schema = PS2Versions.v1_0.load()

    # Generate an enums file based on the current spec
    # Note: If you create a custom spec, create a new enums file for it,
    # rather than overwriting the current one.
    out = generate_enums_for_spec(schema)
    with open("src/progsnap2/spec/enums.py", "w", encoding='utf-8') as f:
        f.write(out)

    # Generate basic TypeScript client code for each event in this spec.
    out = generate_ts_methods(schema)
    pyperclip.copy(out)


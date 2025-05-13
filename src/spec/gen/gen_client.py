from jinja2 import Template

from spec.events import EventType
from spec.spec_definition import ProgSnap2Spec, Column
from spec.datatypes import PS2Datatype
import textwrap

def create_ts_template():
    return """
{{ method_name }}({% for arg in args %}{{ arg.name }}: {{ arg.type }}{% if not loop.last %}, {% endif %}{% endfor %}) {
    this.logEvent(EventType.{{ event_type }}, {
        {% for arg in args %}{{ arg.name }}: {{ arg.name }}{% if not loop.last %}, {% endif %}{% endfor %}
    });
}
"""

def map_to_ts_type(column: Column) -> str:
    if column.datatype == PS2Datatype.Enum:
        return column.name + "Type"
    return column.datatype.typescript_type

def camel_case(s: str):
    parts = s.split(".")
    return parts[0].lower() + ''.join(p.capitalize() for p in parts[1:])

def add_args(columns: list[str], is_required: bool, schema: ProgSnap2Spec, args: list):
    if columns is None:
        return
    for col_name in columns:
        col = next((c for c in schema.main_table.columns if c.name == col_name), None)
        if col:
            ts_type = map_to_ts_type(col)
            name = col.name
            name = name[0].lower() + name[1:]
            if not is_required:
                name = name + "?"
            args.append({"name": name, "type": ts_type})
        else:
            raise ValueError(f"Column {col_name} not found in schema.")

def generate_ts_methods(schema: ProgSnap2Spec) -> str:
    template = Template(create_ts_template())
    methods = []
    for evt in schema.main_table.event_types:
        args = []
        add_args(evt.required_columns, True, schema, args)
        add_args(evt.optional_columns, False, schema, args)

        method_str = template.render(
            method_name=camel_case(evt.name),
            event_type=evt.name.upper().replace(".", "_"),
            args=args
        )
        methods.append(textwrap.indent(method_str, "    "))
    return "\n\n".join(methods)

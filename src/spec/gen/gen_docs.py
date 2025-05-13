

from enum import EnumType
from typing import List

from jinja2 import Template

from spec.datatypes import PS2Datatype
from spec.enums import MainTableColumns
from spec.spec_definition import Column, EnumValue, MainTable, MetadataProperty, ProgSnap2Spec, Property, Requirement

def make_markdown_table(headers, rows):
    # Combine headers and rows to compute the maximum width of each column
    columns = list(zip(*([headers] + rows)))
    col_widths = [max(len(str(cell)) for cell in col) for col in columns]

    # Helper to format a row
    def format_row(row):
        return "| " + " | ".join(str(cell).ljust(width) for cell, width in zip(row, col_widths)) + " |"

    # Build the table
    table = [format_row(headers)]
    separator = "| " + " | ".join("-" * width for width in col_widths) + " |"
    table.append(separator)
    for row in rows:
        table.append(format_row(row))

    return "\n".join(table)

def get_enum_table(enum_values: List[EnumValue]) -> str:
    headers = ["Enum Value", "Description"]
    rows = []
    for enum_value in enum_values:
        description = enum_value.description or ""
        rows.append([enum_value.name, description])
    return headers, rows

def format_enum_table_rows(enum_values: List[EnumValue]) -> str:
    headers, rows = get_enum_table(enum_values)
    return make_markdown_table(headers, rows)

def format_event_type_enum_table(spec: ProgSnap2Spec) -> str:
    headers, rows = get_enum_table(spec.MainTable.event_types)
    headers += ["Required Columns", "Optional Columns"]
    for i, _ in enumerate(rows):
        event_type = spec.MainTable.event_types[i]
        required_columns = ", ".join(event_type.required_columns) if event_type.required_columns else ""
        optional_columns = ", ".join(event_type.optional_columns) if event_type.optional_columns else ""
        rows[i] += [required_columns, optional_columns]
    return make_markdown_table(headers, rows)

# Jinja2 template for enum type section
enum_table_template = Template("""
## {{ enum_type.name }}
* *Datatype*: Enum

**Enum Values**:

{{ table }}
""")

def render_enum_type(enum_type: EnumType) -> str:
    """
    Render a Markdown table for a given EnumType.
    """
    table = format_enum_table_rows(enum_type.values)
    return enum_table_template.render(enum_type=enum_type, table=table)

# TODO: Something's wrong with the MD formatting if this includes bullets (may be in the yaml...)
# --- Shared Helper to Render Description ---
def render_description(description: str) -> str:
    return f"\n{description.strip()}" if description else ""

# --- Shared Renderer for Property, Column, and MetadataProperty ---
def render_property(prop: Property, spec: ProgSnap2Spec) -> str:
    lines = [f"### {prop.name}"]

    if isinstance(prop, Column):
        lines.append(f"* *Requirement Type*: {prop.requirement.value}")

    lines.append(f"* *Datatype*: {prop.datatype.name}")

    if isinstance(prop, MetadataProperty):
        lines.append(f"* *Default value*: {prop.default_value if prop.default_value is not None else 'None'}")

    if prop.datatype == PS2Datatype.Enum:
        lines.append("\n**Enum Values**:\n")
        if prop.name == MainTableColumns.EventType:
            lines.append(format_event_type_enum_table(spec))
        else:
            enum_type = next((et for et in spec.EnumTypes if et.name == prop.name), None)
            if enum_type:
                lines.append(format_enum_table_rows(enum_type.values))
            else:
                raise ValueError(f"Enum type {prop.name} not found in spec.")

    lines.append(render_description(prop.description))
    return "\n".join(lines)

def render_metadata_section(spec: ProgSnap2Spec) -> str:
    lines = ["# Metadata Table"]
    for prop in spec.Metadata.properties:
        lines.append(render_property(prop, spec))
    return "\n\n".join(lines)

def render_main_table_columns_group(columns: List[Column], category: Requirement, spec: ProgSnap2Spec) -> str:
    if category == Requirement.EventSpecific:
        name = "Event-specific Columns"
    elif category == Requirement.Required:
        name = "Universal Required Columns"
    else:
        name = "Universal Optional Columns"

    lines = [f"## {name}"]

    for col in columns:
        lines.append(render_property(col, spec))
    return "\n\n".join(lines)

def render_main_table_columns(spec: ProgSnap2Spec) -> str:
    lines = []

    for category in Requirement:
        columns_subset = [col for col in spec.MainTable.columns if col.requirement == category]
        lines.append(render_main_table_columns_group(columns_subset, category, spec))

    return "\n\n".join(lines)


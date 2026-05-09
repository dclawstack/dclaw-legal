"""Template rendering service — fills `{{variable}}` placeholders."""

import re

from app.models.document_template import DocumentTemplate

_VAR_PATTERN = re.compile(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}")


def render_template(
    template: DocumentTemplate, values: dict[str, str]
) -> tuple[str, list[str]]:
    """Render a template with the supplied values.

    Returns ``(rendered_text, missing_required_variables)``. Required vars are
    those declared in ``template.variables`` with ``required=True``. Unknown
    placeholders in the body are left untouched.
    """
    declared = template.variables or {}
    missing: list[str] = [
        name
        for name, spec in declared.items()
        if spec.get("required", True) and not (values.get(name) or "").strip()
    ]

    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        value = values.get(name)
        if value is None or value == "":
            return match.group(0)
        return str(value)

    rendered = _VAR_PATTERN.sub(replace, template.template_text)
    return rendered, missing

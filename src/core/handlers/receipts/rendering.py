from pathlib import Path

from jinja2 import Environment, FileSystemLoader, Template, select_autoescape


def load_template_from(template_path: str | Path | None = None) -> Template:
    if template_path is None:
        template_path = (
            Path(__file__).resolve().parents[4] / "templates" / "receipt.txt.jinja2"
        )
    template_path = Path(template_path)

    env = Environment(
        loader=FileSystemLoader(str(template_path.parent)),
        autoescape=select_autoescape([]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    return env.get_template(template_path.name)


def build_str_repr_of_receipt(
    receipt_data: dict,
    formatting_config: dict,
    template_path: str | Path | None = None,
) -> str:
    template = load_template_from(template_path)
    context = formatting_config | receipt_data
    return template.render(**context)

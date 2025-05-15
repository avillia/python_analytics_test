from json import load as read_json_from
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, Template, select_autoescape


def generate_template_configs_using(
    width: int,
    config_path: str | Path | None = None,
) -> dict[str, str | int]:
    if config_path is None:
        config_path = Path(__file__).resolve().parents[4] / "templates" / "receipt.json"

    with open(config_path, "r", encoding="utf-8") as file:
        config = read_json_from(file)

    config["width"] = width
    return config


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
    width: int,
    *,
    config_path: str | Path | None = None,
    template_path: str | Path | None = None,
) -> str:
    config = generate_template_configs_using(width, config_path)
    template = load_template_from(template_path)
    context = {**config, **receipt_data}
    return template.render(**context)

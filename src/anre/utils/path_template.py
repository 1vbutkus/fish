from __future__ import annotations

import re
from datetime import date, datetime

PathTemplateArgType = int | str | datetime | date


class PathTemplate:
    def __init__(self, template: str):
        self.template = template
        self.parameters = set(self._parse_template(template))

    def _parse_template(self, template: str) -> list[str]:
        parameters = re.findall(r'\{(\w+)\}', template)

        cleaned_template = template
        for p in parameters:
            cleaned_template = cleaned_template.replace(f'{{{p}}}', '')
        if re.search(r'{|}', cleaned_template):
            raise ValueError(f"Template is wrong '{template}'")
        return parameters

    def _format_arg(self, key: str, value: PathTemplateArgType) -> str:
        if isinstance(value, str):
            if '/' in value:
                raise ValueError(f"Argument '{key}' contains slashes, which are not allowed.")
            return value
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%dT%H_%M_%S')
        if isinstance(value, date):
            return value.strftime('%Y-%m-%d')
        if isinstance(value, int):
            return str(value)
        raise ValueError(f'Unsupported {key} value type {type(value)}')

    def format(self, **kwargs: PathTemplateArgType) -> str:
        keys = set(kwargs.keys())
        missing_params = self.parameters - keys
        extra_params = keys - self.parameters

        if missing_params:
            raise ValueError(f"Missing required arguments: {', '.join(missing_params)}")
        if extra_params:
            raise ValueError(f"Unused arguments provided: {', '.join(extra_params)}")

        kwargs = {key: self._format_arg(key, value) for key, value in kwargs.items()}

        return self.template.format(**kwargs)

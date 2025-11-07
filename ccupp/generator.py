"""Password generation using iterators."""
from collections.abc import Iterator
from itertools import combinations
from itertools import product

from jinja2 import Template


class PasswordGenerator:
    """Password generator using components, templates, prefixes, and suffixes."""

    def __init__(
        self,
        components: dict[str, list[str]],
        delimiters: list[str],
        templates: list[str],
        prefixes: list[str],
        suffixes: list[str],
    ) -> None:
        """
        Initialize password generator.

        Args:
            components: Dictionary mapping component types to lists of component strings
            delimiters: List of delimiter strings
            templates: List of Jinja2 template strings
            prefixes: List of prefix strings
            suffixes: List of suffix strings
        """
        self.components = components
        self.delimiters = delimiters
        self.templates = templates
        self.prefixes = prefixes
        self.suffixes = suffixes

    def _generate_combinations(self) -> Iterator[str]:
        """Generate all possible combinations of components with delimiters."""
        component_values = list(self.components.values())
        for length in range(1, len(component_values) + 1):
            for component_group in combinations(component_values, length):
                for delimiter_group in product(self.delimiters, repeat=length - 1):
                    for component_combination in product(*component_group):
                        password = component_combination[0]
                        for delim, comp in zip(delimiter_group, component_combination[1:]):
                            password += delim + comp
                        yield password

    def generate(self) -> Iterator[str]:
        """
        Generate passwords based on templates, combinations, prefixes, and suffixes.

        Yields:
            Generated password strings
        """
        for tmpl_str in self.templates:
            template = Template(tmpl_str)
            for combination in self._generate_combinations():
                for prefix in self.prefixes:
                    for suffix in self.suffixes:
                        yield template.render(
                            combination=combination,
                            prefix=prefix,
                            suffix=suffix,
                        )

    def generate_unique(self) -> Iterator[str]:
        """
        Generate unique passwords.

        Yields:
            Unique generated password strings
        """
        seen = set()
        for password in self.generate():
            if password not in seen:
                seen.add(password)
                yield password

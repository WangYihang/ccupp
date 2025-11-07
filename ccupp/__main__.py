import sys

import structlog
import typer
import yaml
from pydantic import ValidationError

from ccupp.config import load_persons_from_yaml
from ccupp.generator import PasswordGenerator

app = typer.Typer()
logger = structlog.get_logger()


@app.command()
def generate(
    config: str = typer.Option(
        'config.yaml', '--config', '-c', help='Path to YAML configuration file',
    ),
    prefixes: list[str] = typer.Option(
        ['qwert', '123'], '--prefixes', help='List of prefixes',
    ),
    suffixes: list[str] = typer.Option(
        ['', '123', '@', 'abc', '.', '123.', '!!!'], '--suffixes', help='List of suffixes',
    ),
    delimiters: list[str] = typer.Option(
        ['', '-', '.', '|', '_', '+', '#', '@'], '--delimiters', help='List of delimiters',
    ),
    templates: list[str] = typer.Option(
        ['{{ prefix }}{{ combination }}{{ suffix }}'], '--templates', help='List of templates',
    ),
) -> None:
    """Generate passwords based on user input."""

    # Load persons information from YAML file
    try:
        persons = load_persons_from_yaml(config)
        logger.info('Loaded %d person(s) from: %s', len(persons), config)
    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)
    except yaml.YAMLError as e:
        logger.error('Error parsing YAML file: %s', e)
        sys.exit(1)
    except ValidationError as e:
        logger.error('Validation error in configuration file: %s', e)
        sys.exit(1)

    # Generate passwords for each person
    seen_passwords = set()
    for idx, person in enumerate(persons, 1):
        logger.info('Processing person %d/%d', idx, len(persons))
        components = person.get_components()
        logger.debug('Extracted components: %s', components)

        generator = PasswordGenerator(
            components=components,
            delimiters=delimiters,
            templates=templates,
            prefixes=prefixes,
            suffixes=suffixes,
        )

        # Output unique passwords across all persons
        for password in generator.generate():
            if password not in seen_passwords:
                seen_passwords.add(password)
                print(password)


if __name__ == '__main__':
    app()

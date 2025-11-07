import sys
from importlib import resources
from pathlib import Path

import structlog
import typer
import yaml
from pydantic import ValidationError
from rich.console import Console

from ccupp.config import load_persons_from_yaml
from ccupp.generator import PasswordGenerator

app = typer.Typer()
logger = structlog.get_logger()
console = Console()


def _get_example_config() -> str:
    """Load example configuration from package resources."""
    try:
        with resources.files('ccupp.data').joinpath('config.example.yaml').open(encoding='utf-8') as f:
            return f.read()
    except Exception as exc:
        # Fallback if resources are not available
        raise FileNotFoundError('Example config resource not found') from exc


def _get_example_config_commented() -> str:
    """Load commented example configuration from package resources."""
    try:
        with resources.files('ccupp.data').joinpath('config.example.commented.yaml').open(encoding='utf-8') as f:
            return f.read()
    except Exception as exc:
        # Fallback if resources are not available
        raise FileNotFoundError('Example config resource not found') from exc


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
    except FileNotFoundError:
        console.print(
            f'[red]Error:[/red] Configuration file not found: {config}',
        )
        console.print(
            '[yellow]Hint:[/yellow] Use [cyan]python -m ccupp init[/cyan] to generate an example config file',
        )
        console.print(
            '       Or use [cyan]python -m ccupp example[/cyan] to view the config format',
        )
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


@app.command()
def init(
    output: str = typer.Option(
        'config.yaml',
        '--output',
        '-o',
        help='Output file path for the example configuration',
    ),
) -> None:
    """Generate an example configuration file."""
    try:
        example_config = _get_example_config()
    except FileNotFoundError as e:
        console.print(f'[red]Error:[/red] {e}')
        sys.exit(1)

    output_path = Path(output)
    if output_path.exists():
        console.print(
            f'[yellow]Warning:[/yellow] File {output} already exists',
        )
        if not typer.confirm('Do you want to overwrite it?'):
            console.print('[yellow]Cancelled.[/yellow]')
            return

    try:
        output_path.write_text(example_config, encoding='utf-8')
        console.print(
            f'[green]✓[/green] Example configuration file created: {output_path}',
        )
        console.print(
            '[cyan]Tip:[/cyan] Edit the file and run [cyan]python -m ccupp generate[/cyan]',
        )
    except OSError as e:
        console.print(f'[red]Error:[/red] Failed to create config file: {e}')
        sys.exit(1)


@app.command()
def example() -> None:
    """Show example configuration format."""
    try:
        example_config = _get_example_config_commented()
    except FileNotFoundError as e:
        console.print(f'[red]Error:[/red] {e}')
        sys.exit(1)

    console.print('[bold cyan]Configuration File Format:[/bold cyan]')
    console.print()
    console.print(example_config)
    console.print()
    console.print(
        '[cyan]Tip:[/cyan] Use [cyan]python -m ccupp init[/cyan] to generate a config file',
    )


if __name__ == '__main__':
    app()

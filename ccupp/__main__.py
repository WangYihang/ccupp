"""CCUPP CLI — Chinese Common User Passwords Profiler."""
import json
import sys
from collections import Counter
from importlib import resources
from pathlib import Path

import structlog
import typer
import yaml
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table

from ccupp.config import load_profiles
from ccupp.extractors.components import extract_components
from ccupp.generator import PasswordGenerator

app = typer.Typer(
    name='ccupp',
    help='Chinese Common User Passwords Profiler — generate weak password dictionaries from personal information.',
)
logger = structlog.get_logger()
console = Console(stderr=True)


def _get_resource(filename: str) -> str:
    """Load a resource file from package data."""
    with resources.files('ccupp.data').joinpath(filename).open(encoding='utf-8') as f:
        return f.read()


@app.command()
def generate(
    config: str = typer.Option(
        'config.yaml', '--config', '-c', help='Path to YAML configuration file',
    ),
    output: str = typer.Option(
        None, '--output', '-o', help='Output file path (default: stdout)',
    ),
    format: str = typer.Option(
        'txt', '--format', '-f', help='Output format: txt, json',
    ),
    min_length: int = typer.Option(
        0, '--min-length', help='Minimum password length',
    ),
    max_length: int = typer.Option(
        0, '--max-length', help='Maximum password length (0 = unlimited)',
    ),
    no_leetspeak: bool = typer.Option(
        False, '--no-leetspeak', help='Disable leetspeak transforms',
    ),
    no_cultural: bool = typer.Option(
        False, '--no-cultural', help='Disable Chinese cultural number patterns',
    ),
    no_keyboard: bool = typer.Option(
        False, '--no-keyboard', help='Disable keyboard pattern generation',
    ),
    stats: bool = typer.Option(
        False, '--stats', help='Print generation statistics to stderr',
    ),
) -> None:
    """Generate passwords based on user profile information."""
    # Load profiles
    try:
        profiles = load_profiles(config)
        console.print(f'[dim]Loaded {len(profiles)} profile(s) from {config}[/dim]')
    except FileNotFoundError:
        console.print(f'[red]Error:[/red] Configuration file not found: {config}')
        console.print('[yellow]Hint:[/yellow] Use [cyan]ccupp init[/cyan] to generate an example config file')
        sys.exit(1)
    except yaml.YAMLError as e:
        console.print(f'[red]Error:[/red] Invalid YAML: {e}')
        sys.exit(1)
    except ValidationError as e:
        console.print(f'[red]Error:[/red] Configuration validation failed:\n{e}')
        sys.exit(1)

    # Generate passwords
    seen: set[str] = set()
    passwords: list[str] = []
    length_counter: Counter[str] = Counter()

    for idx, profile in enumerate(profiles, 1):
        console.print(f'[dim]Processing profile {idx}/{len(profiles)}: {profile.surname}{profile.first_name or ""}[/dim]')
        components = extract_components(profile)

        generator = PasswordGenerator(
            components=components,
            enable_leetspeak=not no_leetspeak,
            enable_cultural_numbers=not no_cultural,
            enable_keyboard_patterns=not no_keyboard,
        )

        for pw in generator.generate():
            # Apply length filters
            if min_length and len(pw) < min_length:
                continue
            if max_length and len(pw) > max_length:
                continue
            # Dedup across all profiles
            if pw not in seen:
                seen.add(pw)
                passwords.append(pw)
                if stats:
                    bucket = _length_bucket(len(pw))
                    length_counter[bucket] += 1

    # Output
    out = open(output, 'w', encoding='utf-8') if output else sys.stdout
    try:
        if format == 'json':
            json.dump(passwords, out, ensure_ascii=False, indent=2)
            out.write('\n')
        else:
            for pw in passwords:
                out.write(pw + '\n')
    finally:
        if output:
            out.close()

    # Statistics
    if stats:
        _print_stats(len(passwords), length_counter)
    elif output:
        console.print(f'[green]Generated {len(passwords)} unique passwords → {output}[/green]')


def _length_bucket(length: int) -> str:
    """Categorize password length into buckets."""
    if length <= 6:
        return '1-6'
    elif length <= 8:
        return '7-8'
    elif length <= 12:
        return '9-12'
    elif length <= 16:
        return '13-16'
    else:
        return '17+'


def _print_stats(total: int, length_counter: Counter) -> None:
    """Print generation statistics."""
    console.print()
    table = Table(title='Generation Statistics')
    table.add_column('Metric', style='cyan')
    table.add_column('Value', style='green', justify='right')

    table.add_row('Total passwords', str(total))
    console.print(table)

    if length_counter:
        len_table = Table(title='Length Distribution')
        len_table.add_column('Length', style='cyan')
        len_table.add_column('Count', style='green', justify='right')
        len_table.add_column('Percentage', style='yellow', justify='right')

        for bucket in sorted(length_counter.keys()):
            count = length_counter[bucket]
            pct = f'{count / total * 100:.1f}%'
            len_table.add_row(bucket, str(count), pct)

        console.print(len_table)


@app.command()
def init(
    output: str = typer.Option(
        'config.yaml', '--output', '-o',
        help='Output file path for the example configuration',
    ),
) -> None:
    """Generate an example configuration file."""
    try:
        example_config = _get_resource('config.example.yaml')
    except FileNotFoundError:
        console.print('[red]Error:[/red] Example config resource not found')
        sys.exit(1)

    output_path = Path(output)
    if output_path.exists():
        console.print(f'[yellow]Warning:[/yellow] File {output} already exists')
        if not typer.confirm('Overwrite?'):
            console.print('[yellow]Cancelled.[/yellow]')
            return

    output_path.write_text(example_config, encoding='utf-8')
    console.print(f'[green]Created:[/green] {output_path}')
    console.print('[cyan]Next:[/cyan] Edit the file and run [cyan]ccupp generate[/cyan]')


@app.command()
def example() -> None:
    """Show example configuration format."""
    try:
        content = _get_resource('config.example.commented.yaml')
    except FileNotFoundError:
        console.print('[red]Error:[/red] Example config resource not found')
        sys.exit(1)

    console.print('[bold cyan]Configuration Format:[/bold cyan]\n')
    Console().print(content)
    console.print('\n[cyan]Use[/cyan] [bold]ccupp init[/bold] [cyan]to generate a config file.[/cyan]')


@app.command()
def interactive() -> None:
    """Interactively build a configuration file by answering questions."""
    console.print('[bold cyan]CCUPP Interactive Profile Builder[/bold cyan]\n')

    data: dict = {}
    data['surname'] = typer.prompt('Surname (姓氏)', default='')
    data['first_name'] = typer.prompt('First name (名字)', default='')

    phones = typer.prompt('Phone numbers (comma-separated)', default='')
    data['phone_numbers'] = [p.strip() for p in phones.split(',') if p.strip()] if phones else []

    data['identity'] = typer.prompt('ID number (身份证号)', default='')

    bd = typer.prompt('Birthdate YYYY-MM-DD', default='')
    if bd and '-' in bd:
        parts = bd.split('-')
        data['birthdate'] = parts
    elif bd:
        data['birthdate'] = [bd]

    hometowns = typer.prompt('Hometowns (comma-separated, 家乡)', default='')
    data['hometowns'] = [h.strip() for h in hometowns.split(',') if h.strip()] if hometowns else []

    accounts = typer.prompt('Account names (comma-separated)', default='')
    data['accounts'] = [a.strip() for a in accounts.split(',') if a.strip()] if accounts else []

    old_pw = typer.prompt('Old passwords (comma-separated)', default='')
    data['passwords'] = [p.strip() for p in old_pw.split(',') if p.strip()] if old_pw else []

    # Write config
    output_path = typer.prompt('Save config to', default='config.yaml')
    path = Path(output_path)

    # Merge with existing if present
    existing = []
    if path.exists():
        with open(path, encoding='utf-8') as f:
            existing = yaml.safe_load(f) or []
        if not isinstance(existing, list):
            existing = [existing]

    existing.append(data)
    path.write_text(yaml.dump(existing, allow_unicode=True, default_flow_style=False), encoding='utf-8')
    console.print(f'\n[green]Profile saved to {path}[/green]')
    console.print(f'[cyan]Run:[/cyan] [bold]ccupp generate -c {path}[/bold]')


if __name__ == '__main__':
    app()

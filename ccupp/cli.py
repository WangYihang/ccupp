"""Command-line interface."""
import argparse


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description='Password Generator using Personal Information',
    )
    parser.add_argument(
        '--config', '-c',
        type=str,
        default='config.yaml',
        help='Path to YAML configuration file (default: config.yaml)',
    )
    parser.add_argument(
        '--prefixes', nargs='*',
        default=['qwert', '123'],
        help='List of prefixes',
    )
    parser.add_argument(
        '--suffixes', nargs='*',
        default=['', '123', '@', 'abc', '.', '123.', '!!!'],
        help='List of suffixes',
    )
    parser.add_argument(
        '--delimiters', nargs='*',
        default=['', '-', '.', '|', '_', '+', '#', '@'],
        help='List of delimiters',
    )
    parser.add_argument(
        '--templates', nargs='*',
        default=['{{ prefix }}{{ combination }}{{ suffix }}'],
        help='List of templates',
    )
    return parser.parse_args()

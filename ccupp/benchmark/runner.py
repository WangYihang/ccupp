"""Benchmark runner — evaluates password generation tools against datasets."""
from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

from rich.console import Console
from rich.table import Table

from ccupp.benchmark.datasets import get_builtin_common_passwords
from ccupp.benchmark.datasets import load_password_set
from ccupp.benchmark.profiles import BENCHMARK_PROFILES
from ccupp.benchmark.tools import BaseTool
from ccupp.benchmark.tools import ToolResult
from ccupp.models import Profile


@dataclass
class DatasetEvaluation:
    """Evaluation result against a single dataset."""
    dataset_name: str
    dataset_size: int
    hits: int
    hit_rate: float
    hit_passwords: list[str] = field(default_factory=list)


@dataclass
class ProfileBenchmark:
    """Benchmark result for a single profile across all tools."""
    profile_name: str
    results: dict[str, ToolResult] = field(default_factory=dict)
    dataset_evals: dict[str, dict[str, DatasetEvaluation]] = field(default_factory=dict)
    # tool_name -> dataset_name -> DatasetEvaluation


@dataclass
class BenchmarkReport:
    """Complete benchmark report."""
    profiles: dict[str, ProfileBenchmark] = field(default_factory=dict)


class BenchmarkRunner:
    """Run benchmarks comparing password generation tools."""

    def __init__(
        self,
        tools: list[BaseTool],
        datasets: dict[str, set[str]] | None = None,
        console: Console | None = None,
    ):
        self.tools = tools
        self.datasets = datasets or {'common-passwords': get_builtin_common_passwords()}
        self.console = console or Console(stderr=True)

    def add_dataset(self, name: str, passwords: set[str]) -> None:
        """Add a password dataset for evaluation."""
        self.datasets[name] = passwords

    def add_dataset_file(self, name: str, path: str | Path) -> None:
        """Add a password dataset from a file."""
        self.datasets[name] = load_password_set(path)
        self.console.print(f'[dim]Loaded dataset "{name}": {len(self.datasets[name]):,} passwords[/dim]')

    def run(
        self,
        profiles: dict[str, Profile] | None = None,
    ) -> BenchmarkReport:
        """Run the full benchmark."""
        if profiles is None:
            profiles = BENCHMARK_PROFILES

        report = BenchmarkReport()

        for profile_name, profile in profiles.items():
            self.console.print(f'\n[bold cyan]Profile: {profile_name}[/bold cyan]')
            pb = ProfileBenchmark(profile_name=profile_name)

            for tool in self.tools:
                self.console.print(f'  [dim]Running {tool.name}...[/dim]', end='')
                result = tool.generate(profile)
                pb.results[tool.name] = result

                if result.error:
                    self.console.print(f' [red]ERROR: {result.error}[/red]')
                else:
                    self.console.print(
                        f' [green]{result.count:,} passwords[/green] in {result.duration_seconds:.2f}s'
                    )

                # Evaluate against datasets
                pb.dataset_evals[tool.name] = {}
                for ds_name, ds_passwords in self.datasets.items():
                    hits = result.passwords & ds_passwords
                    hit_rate = len(hits) / len(ds_passwords) if ds_passwords else 0
                    pb.dataset_evals[tool.name][ds_name] = DatasetEvaluation(
                        dataset_name=ds_name,
                        dataset_size=len(ds_passwords),
                        hits=len(hits),
                        hit_rate=hit_rate,
                        hit_passwords=sorted(hits)[:50],  # Keep top 50 for reporting
                    )

            report.profiles[profile_name] = pb

        return report

    def print_report(self, report: BenchmarkReport) -> None:
        """Print a formatted benchmark report."""
        console = Console()  # stdout for the report

        # === Overall comparison table ===
        console.print('\n[bold]== Benchmark Results ==[/bold]\n')

        for profile_name, pb in report.profiles.items():
            console.print(f'[bold cyan]Profile: {profile_name}[/bold cyan]')

            # Generation stats table
            gen_table = Table(title='Generation Statistics')
            gen_table.add_column('Tool', style='cyan')
            gen_table.add_column('Passwords', justify='right', style='green')
            gen_table.add_column('Time (s)', justify='right')
            gen_table.add_column('Passwords/s', justify='right')

            for tool_name, result in pb.results.items():
                rate = int(result.count / result.duration_seconds) if result.duration_seconds > 0 else 0
                gen_table.add_row(
                    tool_name,
                    f'{result.count:,}',
                    f'{result.duration_seconds:.3f}',
                    f'{rate:,}',
                )
            console.print(gen_table)

            # Dataset hit rate table
            if self.datasets:
                hit_table = Table(title='Dataset Hit Rates')
                hit_table.add_column('Tool', style='cyan')
                for ds_name in self.datasets:
                    hit_table.add_column(f'{ds_name}\n(hits / rate)', justify='right')

                for tool_name in pb.results:
                    row = [tool_name]
                    for ds_name in self.datasets:
                        ev = pb.dataset_evals.get(tool_name, {}).get(ds_name)
                        if ev:
                            row.append(f'{ev.hits} / {ev.hit_rate:.1%}')
                        else:
                            row.append('-')
                    hit_table.add_row(*row)
                console.print(hit_table)

            # Overlap analysis between tools
            tool_names = list(pb.results.keys())
            if len(tool_names) >= 2:
                overlap_table = Table(title='Tool Overlap Analysis')
                overlap_table.add_column('Comparison', style='cyan')
                overlap_table.add_column('Overlap', justify='right')
                overlap_table.add_column('Only in A', justify='right', style='yellow')
                overlap_table.add_column('Only in B', justify='right', style='yellow')

                for i, ta in enumerate(tool_names):
                    for tb in tool_names[i + 1:]:
                        pws_a = pb.results[ta].passwords
                        pws_b = pb.results[tb].passwords
                        overlap = len(pws_a & pws_b)
                        only_a = len(pws_a - pws_b)
                        only_b = len(pws_b - pws_a)
                        overlap_table.add_row(
                            f'{ta} vs {tb}',
                            f'{overlap:,}',
                            f'{only_a:,}',
                            f'{only_b:,}',
                        )
                console.print(overlap_table)

            # Length distribution comparison
            len_table = Table(title='Length Distribution')
            len_table.add_column('Length', style='cyan')
            for tool_name in pb.results:
                len_table.add_column(tool_name, justify='right')

            buckets = ['1-6', '7-8', '9-12', '13-16', '17-24', '25+']

            def _bucket(length: int) -> str:
                if length <= 6:
                    return '1-6'
                elif length <= 8:
                    return '7-8'
                elif length <= 12:
                    return '9-12'
                elif length <= 16:
                    return '13-16'
                elif length <= 24:
                    return '17-24'
                else:
                    return '25+'

            for bucket in buckets:
                row = [bucket]
                for tool_name, result in pb.results.items():
                    count = sum(1 for pw in result.passwords if _bucket(len(pw)) == bucket)
                    pct = count / result.count * 100 if result.count else 0
                    row.append(f'{count:,} ({pct:.0f}%)')
                len_table.add_row(*row)

            console.print(len_table)
            console.print()

    def export_json(self, report: BenchmarkReport, path: str | Path) -> None:
        """Export benchmark report as JSON."""
        data = {}
        for profile_name, pb in report.profiles.items():
            data[profile_name] = {
                'results': {
                    tool_name: {
                        'count': r.count,
                        'duration_seconds': r.duration_seconds,
                        'error': r.error,
                    }
                    for tool_name, r in pb.results.items()
                },
                'dataset_evals': {
                    tool_name: {
                        ds_name: {
                            'dataset_size': ev.dataset_size,
                            'hits': ev.hits,
                            'hit_rate': ev.hit_rate,
                            'hit_passwords': ev.hit_passwords,
                        }
                        for ds_name, ev in evals.items()
                    }
                    for tool_name, evals in pb.dataset_evals.items()
                },
            }

        Path(path).write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + '\n',
            encoding='utf-8',
        )

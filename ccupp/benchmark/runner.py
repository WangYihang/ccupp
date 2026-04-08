"""Benchmark runner — evaluates password generation tools against datasets."""
from __future__ import annotations

import json
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

from rich.console import Console
from rich.table import Table

from ccupp.benchmark.academic import get_targeted_papers
from ccupp.benchmark.datasets import PairedRecord
from ccupp.benchmark.datasets import get_builtin_common_passwords
from ccupp.benchmark.datasets import load_paired_dataset
from ccupp.benchmark.datasets import load_password_set
from ccupp.benchmark.metrics import GuessNumberStats
from ccupp.benchmark.metrics import compute_guess_curve
from ccupp.benchmark.metrics import compute_guess_numbers
from ccupp.benchmark.metrics import compute_pii_embedding_rate
from ccupp.benchmark.metrics import compute_success_rate_at_n
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
class AcademicEvaluation:
    """Academic metrics for a paired PII-password dataset."""
    dataset_name: str
    num_targets: int
    success_rates: dict[int, float] = field(default_factory=dict)
    guess_numbers: GuessNumberStats = field(default_factory=GuessNumberStats)
    guess_curve: list[tuple[int, float]] = field(default_factory=list)
    coverage: float = 0.0
    pii_embedding_rate: dict[str, float] = field(default_factory=dict)


@dataclass
class ProfileBenchmark:
    """Benchmark result for a single profile across all tools."""
    profile_name: str
    results: dict[str, ToolResult] = field(default_factory=dict)
    dataset_evals: dict[str, dict[str, DatasetEvaluation]] = field(default_factory=dict)
    academic_evals: dict[str, dict[str, AcademicEvaluation]] = field(default_factory=dict)
    # tool_name -> dataset_name -> AcademicEvaluation


@dataclass
class BenchmarkReport:
    """Complete benchmark report."""
    profiles: dict[str, ProfileBenchmark] = field(default_factory=dict)
    paired_evals: dict[str, dict[str, AcademicEvaluation]] = field(default_factory=dict)
    # tool_name -> dataset_name -> AcademicEvaluation (aggregated across all paired records)


class BenchmarkRunner:
    """Run benchmarks comparing password generation tools."""

    def __init__(
        self,
        tools: list[BaseTool],
        datasets: dict[str, set[str]] | None = None,
        paired_datasets: dict[str, list[PairedRecord]] | None = None,
        console: Console | None = None,
    ):
        self.tools = tools
        self.datasets = datasets or {'common-passwords': get_builtin_common_passwords()}
        self.paired_datasets = paired_datasets or {}
        self.console = console or Console(stderr=True)

    def add_dataset(self, name: str, passwords: set[str]) -> None:
        """Add a password dataset for evaluation."""
        self.datasets[name] = passwords

    def add_dataset_file(self, name: str, path: str | Path) -> None:
        """Add a password dataset from a file."""
        self.datasets[name] = load_password_set(path)
        self.console.print(f'[dim]Loaded dataset "{name}": {len(self.datasets[name]):,} passwords[/dim]')

    def add_paired_dataset(self, name: str, path: str | Path) -> None:
        """Add a PII-password paired dataset for academic evaluation."""
        records = load_paired_dataset(path)
        self.paired_datasets[name] = records
        self.console.print(f'[dim]Loaded paired dataset "{name}": {len(records):,} records[/dim]')

    def run(
        self,
        profiles: dict[str, Profile] | None = None,
        max_paired_records: int = 0,
    ) -> BenchmarkReport:
        """Run the full benchmark."""
        if profiles is None:
            profiles = BENCHMARK_PROFILES

        report = BenchmarkReport()

        # === Standard benchmark (per-profile) ===
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

                # Evaluate against password-only datasets
                pb.dataset_evals[tool.name] = {}
                for ds_name, ds_passwords in self.datasets.items():
                    hits = result.passwords & ds_passwords
                    hit_rate = len(hits) / len(ds_passwords) if ds_passwords else 0
                    pb.dataset_evals[tool.name][ds_name] = DatasetEvaluation(
                        dataset_name=ds_name,
                        dataset_size=len(ds_passwords),
                        hits=len(hits),
                        hit_rate=hit_rate,
                        hit_passwords=sorted(hits)[:50],
                    )

                # PII Embedding Rate (academic metric on standard profiles)
                pb.academic_evals[tool.name] = {}
                pii_rate = compute_pii_embedding_rate(result.passwords, profile)
                pb.academic_evals[tool.name]['pii_embedding'] = AcademicEvaluation(
                    dataset_name='pii_embedding',
                    num_targets=0,
                    pii_embedding_rate=pii_rate,
                )

            report.profiles[profile_name] = pb

        # === Paired evaluation (academic metrics) ===
        if self.paired_datasets:
            self.console.print('\n[bold cyan]Paired Dataset Evaluation (Academic Metrics)[/bold cyan]')

            for ds_name, records in self.paired_datasets.items():
                eval_records = records[:max_paired_records] if max_paired_records > 0 else records
                self.console.print(f'  [dim]Dataset: {ds_name} ({len(eval_records)} records)[/dim]')

                for tool in self.tools:
                    self.console.print(f'    [dim]Running {tool.name}...[/dim]', end='')
                    acad_eval = self._evaluate_paired(tool, eval_records, ds_name)
                    if tool.name not in report.paired_evals:
                        report.paired_evals[tool.name] = {}
                    report.paired_evals[tool.name][ds_name] = acad_eval
                    self.console.print(
                        f' [green]coverage={acad_eval.coverage:.1%}, '
                        f'SR@100={acad_eval.success_rates.get(100, 0):.1%}[/green]'
                    )

        return report

    def _evaluate_paired(
        self,
        tool: BaseTool,
        records: list[PairedRecord],
        ds_name: str,
    ) -> AcademicEvaluation:
        """Evaluate a tool against PII-password paired records."""
        all_targets: set[str] = set()
        all_ordered: list[str] = []
        found_count = 0
        all_ranks: list[int] = []
        per_record_sr: dict[int, list[float]] = {}  # N -> list of per-record 0/1

        for record in records:
            result = tool.generate(record.profile)
            target = record.target_password
            all_targets.add(target)

            # Check coverage (unordered)
            if target in result.passwords:
                found_count += 1

            # If ordered, compute Success Rate @ N and Guess Number
            if result.ordered_passwords:
                target_set = {target}
                sr = compute_success_rate_at_n(result.ordered_passwords, target_set)
                for n, rate in sr.items():
                    per_record_sr.setdefault(n, []).append(rate)

                gn = compute_guess_numbers(result.ordered_passwords, target_set)
                all_ranks.extend(gn.ranks)

                # Use first record's full output for the guess curve sample
                if not all_ordered:
                    all_ordered = result.ordered_passwords

        # Aggregate Success Rate @ N (average across records)
        agg_sr: dict[int, float] = {}
        for n, rates in per_record_sr.items():
            agg_sr[n] = sum(rates) / len(rates)

        # Aggregate Guess Numbers
        import statistics
        guess_stats = GuessNumberStats(
            found=len(all_ranks),
            total=len(records),
            min_rank=min(all_ranks) if all_ranks else 0,
            max_rank=max(all_ranks) if all_ranks else 0,
            median_rank=statistics.median(all_ranks) if all_ranks else 0,
            mean_rank=statistics.mean(all_ranks) if all_ranks else 0,
            ranks=all_ranks,
        )

        # Guess curve from first record (representative)
        curve = compute_guess_curve(all_ordered, all_targets) if all_ordered else []

        return AcademicEvaluation(
            dataset_name=ds_name,
            num_targets=len(records),
            success_rates=agg_sr,
            guess_numbers=guess_stats,
            guess_curve=curve,
            coverage=found_count / len(records) if records else 0,
        )

    def print_report(self, report: BenchmarkReport) -> None:
        """Print a formatted benchmark report."""
        console = Console()

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

            # Overlap analysis
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
                        overlap_table.add_row(
                            f'{ta} vs {tb}',
                            f'{len(pws_a & pws_b):,}',
                            f'{len(pws_a - pws_b):,}',
                            f'{len(pws_b - pws_a):,}',
                        )
                console.print(overlap_table)

            # Length distribution
            len_table = Table(title='Length Distribution')
            len_table.add_column('Length', style='cyan')
            for tool_name in pb.results:
                len_table.add_column(tool_name, justify='right')

            def _bucket(length: int) -> str:
                if length <= 6: return '1-6'
                elif length <= 8: return '7-8'
                elif length <= 12: return '9-12'
                elif length <= 16: return '13-16'
                elif length <= 24: return '17-24'
                else: return '25+'

            for bucket in ['1-6', '7-8', '9-12', '13-16', '17-24', '25+']:
                row = [bucket]
                for tool_name, result in pb.results.items():
                    count = sum(1 for pw in result.passwords if _bucket(len(pw)) == bucket)
                    pct = count / result.count * 100 if result.count else 0
                    row.append(f'{count:,} ({pct:.0f}%)')
                len_table.add_row(*row)
            console.print(len_table)

            # PII Embedding Rate table
            pii_table = Table(title='PII Embedding Rate')
            pii_table.add_column('Tool', style='cyan')
            for col in ['Name', 'Date', 'Phone', 'Account', 'Overall']:
                pii_table.add_column(col, justify='right')

            for tool_name in pb.results:
                acad = pb.academic_evals.get(tool_name, {}).get('pii_embedding')
                if acad and acad.pii_embedding_rate:
                    r = acad.pii_embedding_rate
                    pii_table.add_row(
                        tool_name,
                        f'{r.get("name", 0):.1%}',
                        f'{r.get("date", 0):.1%}',
                        f'{r.get("phone", 0):.1%}',
                        f'{r.get("account", 0):.1%}',
                        f'{r.get("overall", 0):.1%}',
                    )
            console.print(pii_table)
            console.print()

        # === Paired Dataset Academic Metrics ===
        if report.paired_evals:
            console.print('[bold]== Academic Metrics (Paired Evaluation) ==[/bold]\n')

            # Success Rate @ N with academic comparison
            sr_table = Table(title='Success Rate @ N (with Academic Comparison)')
            sr_table.add_column('Method', style='cyan')
            sr_table.add_column('Venue', style='dim')
            for n in [10, 100, 1000, 10_000]:
                sr_table.add_column(f'SR@{n}', justify='right')

            # Add measured results
            for tool_name, ds_evals in report.paired_evals.items():
                for ds_name, acad in ds_evals.items():
                    sr_table.add_row(
                        f'{tool_name}',
                        f'[green](measured)[/green]',
                        *[f'[bold green]{acad.success_rates.get(n, 0):.1%}[/bold green]'
                          for n in [10, 100, 1000, 10_000]],
                    )

            # Add academic baselines
            for paper in get_targeted_papers():
                sr_table.add_row(
                    paper.name,
                    f'{paper.venue} {paper.year}',
                    *[f'{paper.success_rates.get(n, 0):.1%}' if n in paper.success_rates else '-'
                      for n in [10, 100, 1000, 10_000]],
                )

            console.print(sr_table)

            # Guess Number statistics
            gn_table = Table(title='Guess Number Statistics')
            gn_table.add_column('Tool', style='cyan')
            gn_table.add_column('Dataset', style='dim')
            gn_table.add_column('Found', justify='right', style='green')
            gn_table.add_column('Not Found', justify='right', style='red')
            gn_table.add_column('Min Rank', justify='right')
            gn_table.add_column('Median Rank', justify='right')
            gn_table.add_column('Mean Rank', justify='right')
            gn_table.add_column('Max Rank', justify='right')

            for tool_name, ds_evals in report.paired_evals.items():
                for ds_name, acad in ds_evals.items():
                    gn = acad.guess_numbers
                    gn_table.add_row(
                        tool_name, ds_name,
                        str(gn.found), str(gn.not_found),
                        str(gn.min_rank) if gn.found else '-',
                        f'{gn.median_rank:.0f}' if gn.found else '-',
                        f'{gn.mean_rank:.0f}' if gn.found else '-',
                        str(gn.max_rank) if gn.found else '-',
                    )
            console.print(gn_table)

            # Coverage
            cov_table = Table(title='Coverage')
            cov_table.add_column('Tool', style='cyan')
            cov_table.add_column('Dataset', style='dim')
            cov_table.add_column('Targets', justify='right')
            cov_table.add_column('Found', justify='right', style='green')
            cov_table.add_column('Coverage', justify='right', style='bold')

            for tool_name, ds_evals in report.paired_evals.items():
                for ds_name, acad in ds_evals.items():
                    cov_table.add_row(
                        tool_name, ds_name,
                        str(acad.num_targets),
                        str(acad.guess_numbers.found),
                        f'{acad.coverage:.1%}',
                    )
            console.print(cov_table)
            console.print()

    def export_json(self, report: BenchmarkReport, path: str | Path) -> None:
        """Export benchmark report as JSON."""
        data: dict = {}

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
                'pii_embedding_rate': {
                    tool_name: (
                        pb.academic_evals.get(tool_name, {}).get('pii_embedding', AcademicEvaluation(dataset_name='', num_targets=0)).pii_embedding_rate
                    )
                    for tool_name in pb.results
                },
            }

        if report.paired_evals:
            data['_academic_paired'] = {
                tool_name: {
                    ds_name: {
                        'num_targets': acad.num_targets,
                        'success_rates': {str(k): v for k, v in acad.success_rates.items()},
                        'coverage': acad.coverage,
                        'guess_numbers': {
                            'found': acad.guess_numbers.found,
                            'total': acad.guess_numbers.total,
                            'min_rank': acad.guess_numbers.min_rank,
                            'max_rank': acad.guess_numbers.max_rank,
                            'median_rank': acad.guess_numbers.median_rank,
                            'mean_rank': acad.guess_numbers.mean_rank,
                        },
                        'guess_curve': acad.guess_curve,
                    }
                    for ds_name, acad in ds_evals.items()
                }
                for tool_name, ds_evals in report.paired_evals.items()
            }

        Path(path).write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + '\n',
            encoding='utf-8',
        )

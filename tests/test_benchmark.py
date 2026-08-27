"""Tests for the benchmark framework."""
import json
import tempfile
from pathlib import Path

import pytest

from pii2pw.benchmark.academic import ACADEMIC_RESULTS
from pii2pw.benchmark.academic import get_targeted_papers
from pii2pw.benchmark.datasets import PairedRecord
from pii2pw.benchmark.datasets import get_builtin_common_passwords
from pii2pw.benchmark.datasets import load_paired_dataset
from pii2pw.benchmark.datasets import load_paired_dataset_verbose
from pii2pw.benchmark.metrics import GuessNumberStats
from pii2pw.benchmark.metrics import aggregate_guess_curve
from pii2pw.benchmark.metrics import aggregate_success_rate_at_n
from pii2pw.benchmark.metrics import compute_guess_curve
from pii2pw.benchmark.metrics import compute_guess_numbers
from pii2pw.benchmark.metrics import compute_pii_embedding_rate
from pii2pw.benchmark.metrics import compute_success_rate_at_n
from pii2pw.benchmark.profiles import BENCHMARK_PROFILES
from pii2pw.benchmark.profiles import get_profile
from pii2pw.benchmark.profiles import list_profiles
from pii2pw.benchmark.runner import BenchmarkRunner
from pii2pw.benchmark.tools import PII2PWTool
from pii2pw.models import Profile


class TestProfiles:
    def test_list_profiles(self):
        names = list_profiles()
        assert 'zh_full' in names
        assert 'en_full' in names
        assert len(names) >= 5

    def test_get_profile(self):
        p = get_profile('zh_full')
        assert p.surname == '李'
        assert p.first_name == '二狗'

    def test_get_profile_unknown(self):
        with pytest.raises(KeyError):
            get_profile('nonexistent')


class TestDatasets:
    def test_builtin_common_passwords(self):
        passwords = get_builtin_common_passwords()
        assert len(passwords) > 50
        assert '123456' in passwords
        assert 'password' in passwords
        assert '5201314' in passwords


class TestPairedDataset:
    def test_load_jsonl(self, tmp_path):
        data = [
            {'surname': '李', 'first_name': '伟', 'birthdate': ['1990', '01', '15'], 'target_password': 'liwei1990'},
            {'surname': '张', 'first_name': '明', 'target_password': 'zhangming123'},
        ]
        jsonl_file = tmp_path / 'test.jsonl'
        jsonl_file.write_text('\n'.join(json.dumps(d, ensure_ascii=False) for d in data), encoding='utf-8')

        records = load_paired_dataset(jsonl_file)
        assert len(records) == 2
        assert records[0].profile.surname == '李'
        assert records[0].target_password == 'liwei1990'
        assert records[1].profile.surname == '张'

    def test_load_csv(self, tmp_path):
        csv_content = 'surname,first_name,birthdate,target_password\n李,伟,1990;01;15,liwei1990\n'
        csv_file = tmp_path / 'test.csv'
        csv_file.write_text(csv_content, encoding='utf-8')

        records = load_paired_dataset(csv_file)
        assert len(records) == 1
        assert records[0].profile.surname == '李'
        assert records[0].target_password == 'liwei1990'

    def test_skip_records_without_target(self, tmp_path):
        data = [
            {'surname': '李', 'target_password': 'test123'},
            {'surname': '张'},  # No target_password
        ]
        jsonl_file = tmp_path / 'test.jsonl'
        jsonl_file.write_text('\n'.join(json.dumps(d, ensure_ascii=False) for d in data), encoding='utf-8')

        with pytest.warns(UserWarning, match='1 of 2 rows'):
            records = load_paired_dataset(jsonl_file)
        assert len(records) == 1

    def test_skipped_rows_are_reported_not_silent(self, tmp_path):
        """A malformed row must never vanish without a trace.

        This harness turns dropped records into shifted success rates with
        no visible cause, so the loader reports what it could not parse.
        """
        jsonl_file = tmp_path / 'test.jsonl'
        jsonl_file.write_text(
            '{"surname": "\u674e", "target_password": "test123"}\n'
            'not json at all\n'
            '{"surname": "\u5f20"}\n',
            encoding='utf-8',
        )

        load = load_paired_dataset_verbose(jsonl_file)
        assert len(load.records) == 1
        assert load.total_rows == 3
        assert [line for line, _ in load.skipped] == [2, 3]
        assert 'JSONDecodeError' in load.skipped[0][1]
        assert 'target_password' in load.skipped[1][1]

    def test_strict_raises_on_malformed_row(self, tmp_path):
        jsonl_file = tmp_path / 'test.jsonl'
        jsonl_file.write_text('{"surname": "x"}\n', encoding='utf-8')

        with pytest.raises(ValueError, match='could not be parsed'):
            load_paired_dataset(jsonl_file, strict=True)

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_paired_dataset('/nonexistent/file.jsonl')

    def test_unsupported_format(self, tmp_path):
        (tmp_path / 'test.xml').write_text('<data/>')
        with pytest.raises(ValueError):
            load_paired_dataset(tmp_path / 'test.xml')


class TestMetrics:
    def test_success_rate_at_n(self):
        ordered = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'] * 10
        targets = {'c', 'g', 'x'}  # x is not in list

        sr = compute_success_rate_at_n(ordered, targets, n_values=[5, 10, 50])
        assert sr[5] == pytest.approx(1 / 3)   # found 'c' within first 5
        assert sr[10] == pytest.approx(2 / 3)  # found 'c' and 'g' within first 10
        assert sr[50] == pytest.approx(2 / 3)  # 'x' never found

    def test_success_rate_empty_targets(self):
        sr = compute_success_rate_at_n(['a', 'b'], set(), [10])
        assert sr[10] == 0.0

    def test_success_rate_empty_passwords(self):
        sr = compute_success_rate_at_n([], {'a'}, [10])
        assert sr[10] == 0.0

    def test_guess_numbers(self):
        ordered = ['a', 'b', 'c', 'd', 'e']
        targets = {'b', 'e'}

        gn = compute_guess_numbers(ordered, targets)
        assert gn.found == 2
        assert gn.total == 2
        assert gn.min_rank == 2  # 'b' at position 2
        assert gn.max_rank == 5  # 'e' at position 5
        assert gn.median_rank == 3.5
        assert gn.ranks == [2, 5]

    def test_guess_numbers_not_found(self):
        ordered = ['a', 'b', 'c']
        targets = {'x', 'y'}

        gn = compute_guess_numbers(ordered, targets)
        assert gn.found == 0
        assert gn.total == 2
        assert gn.not_found == 2

    def test_guess_numbers_empty(self):
        gn = compute_guess_numbers([], set())
        assert gn.found == 0
        assert gn.total == 0

    def test_guess_curve(self):
        ordered = [f'pw{i}' for i in range(100)]
        targets = {'pw5', 'pw50', 'pw99'}

        curve = compute_guess_curve(ordered, targets, sample_points=[10, 50, 100])
        assert len(curve) == 3
        # At N=10: found pw5 (1/3)
        assert curve[0] == (10, pytest.approx(1 / 3))
        # At N=50: found pw5 (1/3) — pw50 is at index 50 (rank 51), not within 50
        assert curve[1] == (50, pytest.approx(1 / 3))
        # At N=100: found all 3
        assert curve[2] == (100, pytest.approx(3 / 3))

    def test_guess_curve_empty(self):
        curve = compute_guess_curve([], set())
        assert curve == []

    def test_pii_embedding_rate(self):
        profile = Profile(
            surname='李',
            first_name='伟',
            birthdate=('1990', '01', '15'),
            phone_numbers=['13800138000'],
            accounts=['liwei'],
        )
        passwords = {'liwei1990', 'wei123', '138000abc', 'randompass', '19900115'}

        rate = compute_pii_embedding_rate(passwords, profile)
        assert rate['overall'] > 0  # At least some passwords contain PII
        assert 0 <= rate['name'] <= 1
        assert 0 <= rate['date'] <= 1
        assert 0 <= rate['phone'] <= 1

    def test_pii_embedding_rate_empty(self):
        rate = compute_pii_embedding_rate(set(), Profile())
        assert rate['overall'] == 0.0


class TestAcademicData:
    def test_academic_results_not_empty(self):
        assert len(ACADEMIC_RESULTS) >= 6

    def test_targeted_papers(self):
        targeted = get_targeted_papers()
        assert len(targeted) >= 4
        names = [p.name for p in targeted]
        assert 'TarGuess-III' in names
        assert 'PassLLM-I' in names

    def test_paper_fields(self):
        for paper in ACADEMIC_RESULTS:
            assert paper.name
            assert paper.authors
            assert paper.venue
            assert paper.year >= 2014


class TestPII2PWTool:
    def test_is_available(self):
        tool = PII2PWTool()
        assert tool.is_available()
        assert tool.name == 'PII2PW'

    def test_generate(self):
        tool = PII2PWTool()
        profile = get_profile('zh_full')
        result = tool.generate(profile)
        assert result.count > 0
        assert result.error is None
        assert result.duration_seconds >= 0
        assert len(result.passwords) == result.count

    def test_generate_preserves_order(self):
        tool = PII2PWTool()
        profile = get_profile('zh_full')
        result = tool.generate(profile)
        assert len(result.ordered_passwords) > 0
        assert len(result.ordered_passwords) == result.count
        # First password should be old_password (Priority 1)
        assert result.ordered_passwords[0] == 'old_password'

    def test_generate_minimal(self):
        tool = PII2PWTool()
        profile = get_profile('zh_minimal')
        result = tool.generate(profile)
        assert result.count > 0


class TestBenchmarkRunner:
    def test_run_single_tool(self):
        tools = [PII2PWTool()]
        runner = BenchmarkRunner(tools=tools)
        report = runner.run(profiles={'zh_minimal': get_profile('zh_minimal')})
        assert 'zh_minimal' in report.profiles
        pb = report.profiles['zh_minimal']
        assert 'PII2PW' in pb.results
        assert pb.results['PII2PW'].count > 0

    def test_dataset_evaluation(self):
        tools = [PII2PWTool()]
        runner = BenchmarkRunner(tools=tools)
        report = runner.run(profiles={'zh_full': get_profile('zh_full')})
        pb = report.profiles['zh_full']
        assert 'PII2PW' in pb.dataset_evals
        assert 'common-passwords' in pb.dataset_evals['PII2PW']
        ev = pb.dataset_evals['PII2PW']['common-passwords']
        assert ev.hits >= 0
        assert 0 <= ev.hit_rate <= 1

    def test_pii_embedding_computed(self):
        tools = [PII2PWTool()]
        runner = BenchmarkRunner(tools=tools)
        report = runner.run(profiles={'zh_full': get_profile('zh_full')})
        pb = report.profiles['zh_full']
        acad = pb.academic_evals.get('PII2PW', {}).get('pii_embedding')
        assert acad is not None
        assert acad.pii_embedding_rate['overall'] > 0

    def test_paired_evaluation(self, tmp_path):
        # Create synthetic paired data where target passwords match PII2PW output
        data = [
            {'surname': '李', 'first_name': '伟', 'birthdate': ['1990', '01', '15'], 'target_password': 'liwei'},
            {'surname': '张', 'first_name': '明', 'birthdate': ['1985', '06', '20'], 'target_password': 'nonexistent_xyz'},
        ]
        jsonl_file = tmp_path / 'test.jsonl'
        jsonl_file.write_text('\n'.join(json.dumps(d, ensure_ascii=False) for d in data), encoding='utf-8')

        tools = [PII2PWTool()]
        runner = BenchmarkRunner(tools=tools)
        runner.add_paired_dataset('test', jsonl_file)

        report = runner.run(profiles={'zh_minimal': get_profile('zh_minimal')})

        # Check paired evaluation exists
        assert 'PII2PW' in report.paired_evals
        assert 'test' in report.paired_evals['PII2PW']
        acad = report.paired_evals['PII2PW']['test']
        assert acad.num_targets == 2
        # 'liwei' should be found (it's name pinyin), 'nonexistent_xyz' should not
        assert acad.coverage > 0
        assert 10 in acad.success_rates or 100 in acad.success_rates


class TestAggregateMetrics:
    """Aggregation across independently-guessed targets.

    Each target is attacked with a dictionary built for its own profile, so
    these aggregate per-record ranks. The earlier implementation matched one
    record's dictionary against every record's password, which reported a
    guess curve two orders of magnitude below the Success Rate @ N computed
    from the same run.
    """

    def test_success_rate_counts_ranks_within_n(self):
        ranks = [1, 50, 500, 5000, None]
        sr = aggregate_success_rate_at_n(ranks)
        assert sr[10] == 0.2
        assert sr[100] == 0.4
        assert sr[1000] == 0.6
        assert sr[10_000] == 0.8

    def test_unfound_targets_count_against_the_rate(self):
        """None means that target's own dictionary never produced it."""
        assert aggregate_success_rate_at_n([None, None])[10_000] == 0.0
        assert aggregate_success_rate_at_n([1, None])[10] == 0.5

    def test_curve_agrees_with_success_rate(self):
        """The curve at N is exactly Success Rate @ N — same inputs, same answer."""
        ranks = [3, 42, 900, 12_000, None, 7]
        sr = aggregate_success_rate_at_n(ranks)
        curve = dict(aggregate_guess_curve(ranks))
        for n, rate in sr.items():
            assert curve[n] == rate, f'curve and SR disagree at N={n}'

    def test_curve_is_monotonic(self):
        curve = aggregate_guess_curve([1, 100, 10_000, None])
        rates = [rate for _, rate in curve]
        assert rates == sorted(rates)

    def test_empty_input(self):
        assert aggregate_guess_curve([]) == []
        assert all(v == 0.0 for v in aggregate_success_rate_at_n([]).values())

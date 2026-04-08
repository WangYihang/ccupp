"""Tests for the benchmark framework."""
import pytest

from ccupp.benchmark.datasets import get_builtin_common_passwords
from ccupp.benchmark.profiles import BENCHMARK_PROFILES
from ccupp.benchmark.profiles import get_profile
from ccupp.benchmark.profiles import list_profiles
from ccupp.benchmark.runner import BenchmarkRunner
from ccupp.benchmark.tools import CCUPPTool
from ccupp.benchmark.tools import CUPPTool


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
        # Chinese cultural numbers
        assert '5201314' in passwords


class TestCCUPPTool:
    def test_is_available(self):
        tool = CCUPPTool()
        assert tool.is_available()
        assert tool.name == 'CCUPP'

    def test_generate(self):
        tool = CCUPPTool()
        profile = get_profile('zh_full')
        result = tool.generate(profile)
        assert result.count > 0
        assert result.error is None
        assert result.duration_seconds >= 0
        assert len(result.passwords) == result.count

    def test_generate_minimal(self):
        tool = CCUPPTool()
        profile = get_profile('zh_minimal')
        result = tool.generate(profile)
        assert result.count > 0


class TestBenchmarkRunner:
    def test_run_single_tool(self):
        tools = [CCUPPTool()]
        runner = BenchmarkRunner(tools=tools)
        report = runner.run(profiles={'zh_minimal': get_profile('zh_minimal')})
        assert 'zh_minimal' in report.profiles
        pb = report.profiles['zh_minimal']
        assert 'CCUPP' in pb.results
        assert pb.results['CCUPP'].count > 0

    def test_dataset_evaluation(self):
        tools = [CCUPPTool()]
        runner = BenchmarkRunner(tools=tools)
        report = runner.run(profiles={'zh_full': get_profile('zh_full')})
        pb = report.profiles['zh_full']
        # Should have evaluated against built-in common passwords
        assert 'CCUPP' in pb.dataset_evals
        assert 'common-passwords' in pb.dataset_evals['CCUPP']
        ev = pb.dataset_evals['CCUPP']['common-passwords']
        assert ev.hits >= 0
        assert 0 <= ev.hit_rate <= 1

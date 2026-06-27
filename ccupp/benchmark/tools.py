"""Adapters for running different password generation tools with a unified interface.

Each adapter takes a Profile and returns a set of generated passwords.
"""
from __future__ import annotations

import configparser
import subprocess
import tempfile
import time
from abc import ABC
from abc import abstractmethod
from collections.abc import Iterable
from collections.abc import Iterator
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any

if TYPE_CHECKING:
    from ccupp.models import Profile


@dataclass
class ToolResult:
    """Result of running a password generation tool."""
    tool_name: str
    passwords: set[str]
    count: int
    duration_seconds: float
    error: str | None = None
    ordered_passwords: list[str] = field(default_factory=list)
    # Ordered list preserving generation priority. Empty for tools
    # that don't support ordering (CUPP, bopscrk).


class BaseTool(ABC):
    """Base class for password generation tool adapters."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable tool name."""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the tool is installed and available."""

    @abstractmethod
    def generate(self, profile: Profile) -> ToolResult:
        """Generate passwords for the given profile."""


class CCUPPTool(BaseTool):
    """Adapter for CCUPP (this project)."""

    @property
    def name(self) -> str:
        return 'CCUPP'

    def is_available(self) -> bool:
        try:
            from ccupp.generator import PasswordGenerator
            return True
        except ImportError:
            return False

    def generate(self, profile: Profile) -> ToolResult:
        from ccupp.extractors.components import extract_components
        from ccupp.generator import PasswordGenerator

        start = time.time()
        components = extract_components(profile)
        gen = PasswordGenerator(components=components)
        ordered = list(gen.generate())
        passwords = set(ordered)
        duration = time.time() - start

        return ToolResult(
            tool_name=self.name,
            passwords=passwords,
            count=len(passwords),
            duration_seconds=duration,
            ordered_passwords=ordered,
        )


class CUPPTool(BaseTool):
    """Adapter for CUPP (Common User Passwords Profiler).

    Supports two modes:
    - Direct Python import (if cupp repo is cloned)
    - CLI subprocess (if cupp is installed via pip)
    """

    def __init__(self, cupp_path: str | Path | None = None):
        self._cupp_path = Path(cupp_path) if cupp_path else None

    @property
    def name(self) -> str:
        return 'CUPP'

    def is_available(self) -> bool:
        # Check if cupp.py exists at the given path
        if self._cupp_path and self._cupp_path.exists():
            return True
        # Check if cupp is importable (pip install cupp)
        try:
            result = subprocess.run(
                ['cupp', '--version'],
                capture_output=True, text=True, timeout=5,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _profile_to_cupp_profile(self, profile: Profile) -> dict[str, Any]:
        """Convert our Profile to CUPP's profile dict format."""
        from ccupp.transforms.pinyin import to_pinyin

        # CUPP expects romanized names (not Chinese characters)
        name = to_pinyin(profile.first_name) if profile.first_name else ''
        surname = to_pinyin(profile.surname) if profile.surname else ''

        # Format birthdate as DDMMYYYY
        birthdate = ''
        if profile.birthdate and len(profile.birthdate) >= 3:
            y, m, d = profile.birthdate[0], profile.birthdate[1], profile.birthdate[2]
            birthdate = f'{d}{m}{y}'

        return {
            'name': name.lower(),
            'surname': surname.lower(),
            'nick': profile.accounts[0].lower() if profile.accounts else '',
            'birthdate': birthdate,
            'wife': '',
            'wifen': '',
            'wifeb': '',
            'kid': '',
            'kidn': '',
            'kidb': '',
            'pet': '',
            'company': to_pinyin(profile.workplaces[0][0]).lower() if profile.workplaces else '',
            'words': [to_pinyin(h) for h in profile.hometowns] if profile.hometowns else [''],
            'spechars1': 'y',
            'randnum': 'y',
            'leetmode': 'y',
        }

    def generate(self, profile: Profile) -> ToolResult:
        start = time.time()
        try:
            passwords = self._generate_via_python(profile)
            duration = time.time() - start
            return ToolResult(
                tool_name=self.name,
                passwords=passwords,
                count=len(passwords),
                duration_seconds=duration,
            )
        except Exception as e:
            duration = time.time() - start
            return ToolResult(
                tool_name=self.name,
                passwords=set(),
                count=0,
                duration_seconds=duration,
                error=str(e),
            )

    def _generate_via_python(self, profile: Profile) -> set[str]:
        """Generate passwords by importing CUPP's internals directly."""
        import glob
        import importlib.util
        import os
        import sys
        from io import StringIO
        from unittest.mock import patch

        cupp_profile = self._profile_to_cupp_profile(profile)

        # Find cupp.py
        cupp_py = self._cupp_path
        if not cupp_py or not cupp_py.exists():
            for candidate in [
                Path('/tmp/cupp/cupp.py'),
                Path('cupp/cupp.py'),
                Path.home() / 'cupp' / 'cupp.py',
            ]:
                if candidate.exists():
                    cupp_py = candidate
                    break

        if not cupp_py or not cupp_py.exists():
            raise FileNotFoundError(
                'CUPP not found. Clone it: git clone https://github.com/Mebus/cupp.git /tmp/cupp'
            )

        # Load cupp module
        spec = importlib.util.spec_from_file_location('cupp_bench', str(cupp_py))
        if spec is None or spec.loader is None:
            raise ImportError(f'Could not load CUPP module from {cupp_py}')
        cupp_module: Any = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cupp_module)

        cfg_path = cupp_py.parent / 'cupp.cfg'
        cupp_module.read_config(str(cfg_path))

        # CUPP's print_to_file calls input() for "Hyperspeed Print?" — patch it
        passwords: set[str] = set()
        orig_print_to_file = cupp_module.print_to_file

        def patched_print_to_file(filename: str, unique_list_finished: Iterable[str]) -> None:
            """Write to file without interactive prompts."""
            with open(filename, 'w') as f:
                f.write(os.linesep.join(sorted(unique_list_finished)))

        cupp_module.print_to_file = patched_print_to_file

        # Run in temp dir to avoid polluting cwd
        orig_dir = os.getcwd()
        work_dir = tempfile.mkdtemp(prefix='cupp_bench_')
        os.chdir(work_dir)

        try:
            # Suppress stdout
            with patch('sys.stdout', new_callable=StringIO):
                cupp_module.generate_wordlist_from_profile(cupp_profile)
        except (SystemExit, EOFError):
            pass
        finally:
            os.chdir(orig_dir)
            cupp_module.print_to_file = orig_print_to_file

        # Read generated files
        name = cupp_profile['name']
        for f in glob.glob(os.path.join(work_dir, f'{name}*.txt')):
            with open(f, encoding='utf-8', errors='ignore') as fh:
                for line in fh:
                    pw = line.strip()
                    if pw:
                        passwords.add(pw)
            os.unlink(f)

        # Cleanup
        try:
            os.rmdir(work_dir)
        except OSError:
            pass

        return passwords


class BopscrkTool(BaseTool):
    """Adapter for bopscrk (Before Outset PaSsword CRacKing).

    Uses subprocess to call bopscrk CLI with -w flag for non-interactive mode.
    Install: pip install bopscrk  OR  git clone https://github.com/r3nt0n/bopscrk.git
    """

    def __init__(self, bopscrk_path: str | Path | None = None):
        self._bopscrk_path = Path(bopscrk_path) if bopscrk_path else None

    @property
    def name(self) -> str:
        return 'bopscrk'

    @staticmethod
    def _resolve_executable() -> str | None:
        """Locate the bopscrk CLI executable; pip's `python -m bopscrk` is a no-op."""
        import shutil
        return shutil.which('bopscrk')

    def is_available(self) -> bool:
        exe = self._resolve_executable()
        if not exe:
            return False
        try:
            result = subprocess.run(
                [exe, '--version'], capture_output=True, text=True, timeout=10,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def generate(self, profile: Profile) -> ToolResult:
        from ccupp.transforms.pinyin import to_pinyin

        start = time.time()
        try:
            # Collect keywords from profile
            words = []
            if profile.first_name:
                words.append(to_pinyin(profile.first_name))
            if profile.surname:
                words.append(to_pinyin(profile.surname))
            if profile.birthdate and len(profile.birthdate) >= 3:
                words.append(profile.birthdate[0])  # year
            for acc in profile.accounts:
                words.append(acc)
            for wp in profile.workplaces:
                words.extend(wp)
            for ht in profile.hometowns:
                words.append(to_pinyin(ht))

            if not words:
                return ToolResult(self.name, set(), 0, 0, error='No words for bopscrk')

            exe = self._resolve_executable()
            if not exe:
                return ToolResult(self.name, set(), 0, 0, error='bopscrk not on PATH')

            with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
                tmp_path = tmp.name

            cmd = [
                exe,
                '-w', ','.join(words),
                '-c', '-l',
                '--min', '4', '--max', '24',
                '-o', tmp_path,
            ]

            proc = subprocess.run(
                cmd, capture_output=True, text=True, timeout=300,
            )

            # Preserve bopscrk's emission order so the paired evaluation can
            # treat candidate position as a (coarse) ranking for SR@N. bopscrk
            # has no likelihood model, so this order is its output order, not a
            # relevance ranking — see the SR@N caption note on the site.
            ordered: list[str] = []
            passwords: set[str] = set()
            out_path = Path(tmp_path)
            if out_path.exists():
                with open(out_path, encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        pw = line.strip()
                        if pw and pw not in passwords:
                            passwords.add(pw)
                            ordered.append(pw)
                out_path.unlink()

            duration = time.time() - start
            err = None if passwords else (proc.stderr or proc.stdout or 'bopscrk produced no output')
            return ToolResult(
                self.name, passwords, len(passwords), duration,
                error=err, ordered_passwords=ordered,
            )

        except Exception as e:
            duration = time.time() - start
            return ToolResult(self.name, set(), 0, duration, error=str(e))


class PassLLMTool(BaseTool):
    """Adapter for PassLLM (USENIX Security 2025).

    PassLLM is a 4B-param Qwen3 LoRA-finetuned model for targeted password
    guessing. Inference is GPU-friendly but works on CPU at single-digit
    candidates/second. Setup:
        git clone https://github.com/Tzohar/PassLLM.git /opt/PassLLM
        cd /opt/PassLLM && pip install -r requirements.txt
        curl -L https://github.com/Tzohar/PassLLM/releases/download/v1.3.0/PassLLM-Qwen3-4B-v1.0.pth \
            -o models/PassLLM_LoRA_Weights.pth

    Then point this adapter at the repo via `passllm_path` (or env var
    PASSLLM_PATH). The model is loaded once and cached across generate() calls.
    """

    # PassLLM's schema (see PassLLM/src/config.py:169)
    _SCHEMA_FIELDS = (
        'name', 'birth_year', 'birth_month', 'birth_day',
        'username', 'email', 'address', 'phone', 'city', 'country', 'sister_pw',
    )

    def __init__(self, passllm_path: str | Path | None = None):
        import os
        self._passllm_path = Path(passllm_path) if passllm_path else (
            Path(os.environ['PASSLLM_PATH']) if 'PASSLLM_PATH' in os.environ else None
        )
        self._model: Any = None
        self._tokenizer: Any = None
        self._predict: Any = None  # cached reference to inference.predict_password

    @property
    def name(self) -> str:
        return 'PassLLM'

    def is_available(self) -> bool:
        if not self._passllm_path or not self._passllm_path.exists():
            return False
        return (
            (self._passllm_path / 'app.py').exists()
            and (self._passllm_path / 'inference.py').exists()
            and (self._passllm_path / 'models').exists()
        )

    def _load_model(self) -> None:
        """Lazy-load model + tokenizer from PassLLM's loader (once per process)."""
        if self._model is not None:
            return
        import sys
        import torch
        sys.path.insert(0, str(self._passllm_path))
        try:
            from src.loader import build_model, inject_lora_layers
            from src.config import Config
            from inference import predict_password
            model, tokenizer = build_model()
            model = inject_lora_layers(model)
            ckpt = torch.load(Config.WEIGHTS_FILE, map_location='cpu')
            model.load_state_dict(ckpt, strict=False)
            model.eval()
            self._model = model
            self._tokenizer = tokenizer
            self._predict = predict_password
        finally:
            # Don't poison sys.path beyond this load.
            try:
                sys.path.remove(str(self._passllm_path))
            except ValueError:
                pass

    def _profile_to_passllm_dict(self, profile: Profile) -> dict[str, str]:
        from ccupp.transforms.pinyin import to_pinyin

        first = to_pinyin(profile.first_name) if profile.first_name else ''
        last = to_pinyin(profile.surname) if profile.surname else ''
        full_name = (last + first).strip() or first or last

        y, m, d = '', '', ''
        if profile.birthdate and len(profile.birthdate) >= 3:
            y, m, d = profile.birthdate[0], profile.birthdate[1], profile.birthdate[2]

        out = {
            'name': full_name,
            'birth_year': y,
            'birth_month': m,
            'birth_day': d,
            'username': profile.accounts[0] if profile.accounts else '',
            'phone': profile.phone_numbers[0] if profile.phone_numbers else '',
            'city': to_pinyin(profile.hometowns[0]) if profile.hometowns else '',
        }
        return {k: v for k, v in out.items() if v}

    def generate(self, profile: Profile) -> ToolResult:
        start = time.time()
        try:
            self._load_model()
            pii = self._profile_to_passllm_dict(profile)
            if not pii.get('name'):
                return ToolResult(self.name, set(), 0, 0, error='PassLLM needs at least a name')

            candidates = self._predict(self._model, self._tokenizer, pii)
            # candidates is List[{'password': str, 'score': float, ...}] ranked by
            # log-prob. Preserve ranking for SR@N.
            ordered: list[str] = []
            seen: set[str] = set()
            for cand in candidates:
                pw = cand.get('password', '')
                if pw and pw not in seen:
                    ordered.append(pw)
                    seen.add(pw)
            duration = time.time() - start
            return ToolResult(
                tool_name=self.name,
                passwords=seen,
                count=len(seen),
                duration_seconds=duration,
                ordered_passwords=ordered,
            )
        except Exception as e:
            duration = time.time() - start
            return ToolResult(self.name, set(), 0, duration, error=str(e))


def get_available_tools(
    cupp_path: str | None = None,
    bopscrk_path: str | None = None,
    passllm_path: str | None = None,
) -> list[BaseTool]:
    """Get all available password generation tools."""
    tools: list[BaseTool] = [CCUPPTool()]

    cupp = CUPPTool(cupp_path=cupp_path)
    if cupp.is_available():
        tools.append(cupp)

    bopscrk = BopscrkTool(bopscrk_path=bopscrk_path)
    if bopscrk.is_available():
        tools.append(bopscrk)

    passllm = PassLLMTool(passllm_path=passllm_path)
    if passllm.is_available():
        tools.append(passllm)

    return tools

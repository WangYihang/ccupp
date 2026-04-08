"""Static reference data from published academic papers on password guessing.

These are the reported Success Rate @ N values from peer-reviewed papers,
used for direct comparison with CCUPP's benchmark results.
"""
from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field


@dataclass
class AcademicPaper:
    """Published results from an academic password guessing paper."""
    name: str
    authors: str
    venue: str
    year: int
    approach: str
    targeted: bool  # True = PII-based targeted guessing
    chinese: bool   # True = evaluated on Chinese datasets
    success_rates: dict[int, float] = field(default_factory=dict)
    # N -> success rate (fraction, 0.0-1.0)
    notes: str = ''


# Published results from peer-reviewed papers.
# Success rates are approximate values extracted from paper figures/tables.
# For papers with multiple datasets, we use the Chinese dataset results where available.
ACADEMIC_RESULTS: list[AcademicPaper] = [
    AcademicPaper(
        name='TarGuess-III',
        authors='Wang et al.',
        venue='ACM CCS',
        year=2016,
        approach='PII-tagged PCFG',
        targeted=True,
        chinese=True,
        success_rates={
            10: 0.046,
            100: 0.197,
            1000: 0.454,
        },
        notes='Scenario III (PII-only). Evaluated on 12306+Dodonew Chinese datasets. '
              'The seminal work on targeted password guessing.',
    ),
    AcademicPaper(
        name='Personal-PCFG',
        authors='Li et al.',
        venue='USENIX Security',
        year=2014,
        approach='PCFG with PII semantic tags',
        targeted=True,
        chinese=True,
        success_rates={
            100: 0.128,
            1000: 0.295,
        },
        notes='Found 60.1% of Chinese users embed PII in passwords. '
              'First large-scale PII-password study on Chinese users.',
    ),
    AcademicPaper(
        name='RFGuess-PII',
        authors='Wang & Zou',
        venue='USENIX Security',
        year=2023,
        approach='Random Forest classifier',
        targeted=True,
        chinese=True,
        success_rates={
            10: 0.073,
            100: 0.241,
            1000: 0.487,
        },
        notes='20-28% of common users within 100 guesses. '
              'Evaluated on PII-12306, PII-Dodonew, PII-ClixSense.',
    ),
    AcademicPaper(
        name='PointerGuess',
        authors='Xiu & Wang',
        venue='USENIX Security',
        year=2024,
        approach='Seq2Seq with pointer mechanism',
        targeted=True,
        chinese=True,
        success_rates={
            10: 0.082,
            100: 0.252,
        },
        notes='25.21% success within 100 guesses for cross-site password guessing. '
              'Requires a known sister password.',
    ),
    AcademicPaper(
        name='PassLLM-I',
        authors='Zou & Wang',
        venue='USENIX Security',
        year=2025,
        approach='LLM (7B) fine-tuned with LoRA',
        targeted=True,
        chinese=True,
        success_rates={
            10: 0.098,
            100: 0.316,
            1000: 0.523,
        },
        notes='Current SOTA. 12.54-31.63% within 100 guesses. '
              'Uses Qwen-2 for Chinese support. Requires GPU + training data.',
    ),
    AcademicPaper(
        name='RankGuess-PII',
        authors='Yang & Wang',
        venue='IEEE S&P',
        year=2025,
        approach='RL-based adversarial ranking',
        targeted=True,
        chinese=True,
        success_rates={
            100: 0.278,
            1000: 0.501,
        },
        notes='58-92% of common users within 10^12 guesses. '
              'Latest from the Nankai University group.',
    ),
    # Non-targeted baselines for context
    AcademicPaper(
        name='PassGPT',
        authors='Rando et al.',
        venue='SaTML',
        year=2024,
        approach='GPT-2 trained on password leaks',
        targeted=False,
        chinese=False,
        success_rates={},
        notes='Non-targeted (trawling). Guesses 2x more passwords than PassGAN. '
              'Referenced in CCUPP README.',
    ),
    AcademicPaper(
        name='PassGAN',
        authors='Hitaj et al.',
        venue='ACNS',
        year=2019,
        approach='Improved WGAN',
        targeted=False,
        chinese=False,
        success_rates={},
        notes='Non-targeted. Combined with HashCat matches 51-73% more passwords.',
    ),
]


def get_targeted_papers() -> list[AcademicPaper]:
    """Get only PII-targeted papers (relevant for CCUPP comparison)."""
    return [p for p in ACADEMIC_RESULTS if p.targeted and p.success_rates]


def get_all_papers() -> list[AcademicPaper]:
    """Get all papers including non-targeted baselines."""
    return ACADEMIC_RESULTS

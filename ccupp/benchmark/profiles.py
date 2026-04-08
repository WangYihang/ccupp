"""Standard benchmark profiles for reproducible evaluation.

These profiles represent realistic Chinese and English user personas
with varying amounts of PII. They are synthetic (not real people)
but follow realistic patterns.
"""
from ccupp.models import Profile

# Standard benchmark profiles — synthetic, not real people
BENCHMARK_PROFILES: dict[str, Profile] = {
    'zh_full': Profile(
        surname='李',
        first_name='二狗',
        phone_numbers=['13512345678'],
        identity='220281198309243953',
        birthdate=('1983', '09', '24'),
        hometowns=['四川', '成都', '高新区'],
        places=[['河北', '秦皇岛', '北戴河']],
        social_media=['987654321'],
        workplaces=[['腾讯', 'tencent']],
        educational_institutions=[['清华大学', '清华', 'tsinghua']],
        accounts=['twodogs'],
        passwords=['old_password'],
    ),
    'zh_minimal': Profile(
        surname='王',
        first_name='小明',
        phone_numbers=['13800138000'],
        birthdate=('1990', '01', '01'),
    ),
    'zh_medium': Profile(
        surname='张',
        first_name='伟',
        phone_numbers=['15912345678', '13612345678'],
        identity='110101199505152345',
        birthdate=('1995', '05', '15'),
        hometowns=['北京', '海淀区'],
        workplaces=[['百度', 'baidu']],
        educational_institutions=[['北京大学', '北大', 'pku']],
        accounts=['zhangwei95'],
    ),
    'en_full': Profile(
        surname='Smith',
        first_name='John',
        phone_numbers=['2025551234'],
        birthdate=('1985', '07', '15'),
        hometowns=['NewYork', 'Manhattan'],
        workplaces=[['Google', 'google']],
        educational_institutions=[['MIT', 'mit']],
        accounts=['jsmith'],
        passwords=['Summer2023!'],
    ),
    'en_minimal': Profile(
        surname='Brown',
        first_name='Alice',
        birthdate=('1992', '12', '25'),
    ),
}


def get_profile(name: str) -> Profile:
    """Get a benchmark profile by name."""
    if name not in BENCHMARK_PROFILES:
        available = ', '.join(BENCHMARK_PROFILES.keys())
        raise KeyError(f'Unknown profile: {name}. Available: {available}')
    return BENCHMARK_PROFILES[name]


def list_profiles() -> list[str]:
    """List all available benchmark profile names."""
    return list(BENCHMARK_PROFILES.keys())

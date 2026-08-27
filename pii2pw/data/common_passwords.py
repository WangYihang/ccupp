"""Generic weak passwords used as a fallback during generation.

A meaningful share of users pick a password containing no personal
information at all. No amount of profile-driven rule expansion reaches
those, so the generator emits this list after its high-signal PII stages.

Entries are drawn from published password-analysis literature and vendor
"worst passwords" reports, ordered roughly by observed frequency — the
order is the emission order, so the most common come first.

.. warning::
   This list is deliberately kept separate from
   :data:`pii2pw.benchmark.datasets.TOP_COMMON_PASSWORDS`, which is an
   *evaluation* dataset. They overlap by construction — both enumerate
   common weak passwords — so the built-in ``common-passwords`` benchmark
   dataset is **not** an independent test set for PII2PW. Use an external
   corpus (rockyou, SecLists) when measuring hit rate.
"""
from __future__ import annotations

COMMON_WEAK_PASSWORDS: list[str] = [
    # Globally dominant
    '123456', '123456789', 'password', '12345678', '111111',
    '1234567890', '1234567', 'qwerty', 'abc123', '12345',
    '000000', '1234', 'iloveyou', 'qwerty123', '1q2w3e',
    'admin', 'password1', 'password123', '123123', '654321',
    'qwertyuiop', '1qaz2wsx', 'zxcvbnm', 'asdfgh', 'asdfghjkl',
    '112233', '121212', '555555', '666666', '888888',
    '7777777', '999999', '222222', '333333', 'aaaaaa',
    'abcd1234', 'a123456', 'p@ssw0rd', 'passw0rd', 'welcome',
    'letmein', 'monkey', 'dragon', 'master', 'sunshine',
    'princess', 'football', 'baseball', 'shadow', 'superman',
    'trustno1', 'freedom', 'whatever', 'starwars', 'batman',
    'hello', 'charlie', 'jordan', 'harley', 'ranger',
    'hunter', 'buster', 'thomas', 'robert', 'michael',
    'jennifer', 'jessica', 'michelle', 'ashley', 'amanda',
    'computer', 'internet', 'access', 'matrix', 'killer',
    'changeme', 'default', 'secret', 'test', 'test123',
    'root', 'root123', 'toor', 'guest', 'user',
    'admin123', 'administrator', 'login', 'pass', 'pass123',

    # Chinese-common, from published analyses of CN corpora
    '5201314', '1314520', '520520', '521521', 'woaini',
    'woaini1314', 'woaini520', 'aini1314', '123456a', 'a123456789',
    '168168', '1231231', '11223344', '147258369', '123321',
    '789456123', '159357', '147258', '159753', '456789',
    'asd123456', 'qwe123456', 'abc123456', 'zxc123456', 'q1w2e3r4',
    'wang123', 'li123456', 'zhang123', 'chen123', 'liu123',
    'woshishui', 'nihao123', 'zhongguo', 'beijing', 'shanghai',
    'taobao', 'qqqqqq', 'woaimama', 'buzhidao', 'meiyoumima',
]

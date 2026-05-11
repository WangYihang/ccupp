/**
 * Frozen benchmark figures used throughout the report.
 *
 * Sources:
 *   - CCUPP / CUPP rows: measured locally on April 2026 on a single CPU
 *     thread over the 200-record synthetic dataset described in §1.
 *   - Academic baselines: numbers transcribed from each paper, evaluated
 *     by the original authors on real leaked corpora (12306, Dodonew).
 */

export type Tool = 'CCUPP' | 'CUPP';

export interface GenRow {
  tool: Tool;
  passwords: number;
  time_s: number;
  pwd_per_s: number;
}

export interface ProfileGen {
  profile: string;
  rows: [GenRow, GenRow];           // CCUPP first, CUPP second
}

export const generation: ProfileGen[] = [
  { profile: 'zh_full',    rows: [
    { tool: 'CCUPP', passwords: 12_335, time_s: 0.006, pwd_per_s: 2_216_275 },
    { tool: 'CUPP',  passwords: 28_527, time_s: 0.103, pwd_per_s:   277_964 },
  ]},
  { profile: 'zh_minimal', rows: [
    { tool: 'CCUPP', passwords:  4_244, time_s: 0.002, pwd_per_s: 2_582_046 },
    { tool: 'CUPP',  passwords:  5_230, time_s: 0.018, pwd_per_s:   292_689 },
  ]},
  { profile: 'zh_medium',  rows: [
    { tool: 'CCUPP', passwords:  9_007, time_s: 0.004, pwd_per_s: 2_349_384 },
    { tool: 'CUPP',  passwords: 18_594, time_s: 0.043, pwd_per_s:   430_639 },
  ]},
  { profile: 'en_full',    rows: [
    { tool: 'CCUPP', passwords:  4_432, time_s: 0.002, pwd_per_s: 2_915_031 },
    { tool: 'CUPP',  passwords: 22_304, time_s: 0.045, pwd_per_s:   496_836 },
  ]},
  { profile: 'en_minimal', rows: [
    { tool: 'CCUPP', passwords:  2_076, time_s: 0.001, pwd_per_s: 2_913_166 },
    { tool: 'CUPP',  passwords:  9_546, time_s: 0.022, pwd_per_s:   431_200 },
  ]},
];

export interface PiiRow {
  tool: Tool;
  name: number;
  date: number;
  phone: number;
  account: number;
  overall: number;
}

export interface ProfilePii {
  profile: string;
  rows: [PiiRow, PiiRow];
}

export const piiEmbedding: ProfilePii[] = [
  { profile: 'zh_full',    rows: [
    { tool: 'CCUPP', name: 22.4, date: 20.8, phone:  8.9, account: 5.1, overall: 48.2 },
    { tool: 'CUPP',  name: 27.1, date:  4.6, phone:  0.0, account: 7.3, overall: 33.2 },
  ]},
  { profile: 'zh_minimal', rows: [
    { tool: 'CCUPP', name: 46.4, date: 33.6, phone: 14.5, account: 0.0, overall: 73.7 },
    { tool: 'CUPP',  name: 38.3, date:  4.9, phone:  0.0, account: 0.0, overall: 41.6 },
  ]},
  { profile: 'zh_medium',  rows: [
    { tool: 'CCUPP', name: 28.3, date: 22.2, phone: 11.1, account: 4.3, overall: 54.3 },
    { tool: 'CUPP',  name: 30.4, date:  4.8, phone:  0.0, account: 3.6, overall: 35.2 },
  ]},
];

export interface SrRow {
  method: string;
  venueKey: string;           // i18n key for venue (or fixed string)
  approachKey: string;        // i18n key for approach
  sr10:   number | null;
  sr100:  number | null;
  sr1k:   number | null;
  sr10k:  number | null;
  measured?: boolean;
  ours?: boolean;
}

export const successRate: SrRow[] = [
  { method: 'CCUPP',         venueKey: 'lbl_measured',  approachKey: 'apr_rb_pii',   sr10: 0.0, sr100:  1.0, sr1k: 45.5, sr10k: 84.0, measured: true, ours: true },
  { method: 'CUPP',          venueKey: 'lbl_measured',  approachKey: 'apr_rb',       sr10: 0.0, sr100:  0.0, sr1k:  0.0, sr10k:  0.0, measured: true },
  { method: 'TarGuess-III',  venueKey: 'CCS 2016',      approachKey: 'apr_pcfg_pii', sr10: 4.6, sr100: 19.7, sr1k: 45.4, sr10k: null },
  { method: 'Personal-PCFG', venueKey: 'USENIX 2014',   approachKey: 'apr_pcfg',     sr10: null, sr100: 12.8, sr1k: 29.5, sr10k: null },
  { method: 'RFGuess-PII',   venueKey: 'USENIX 2023',   approachKey: 'apr_rf',       sr10: 7.3, sr100: 24.1, sr1k: 48.7, sr10k: null },
  { method: 'PointerGuess',  venueKey: 'USENIX 2024',   approachKey: 'apr_seq',      sr10: 8.2, sr100: 25.2, sr1k: null, sr10k: null },
  { method: 'PassLLM-I',     venueKey: 'USENIX 2025',   approachKey: 'apr_llm',      sr10: 9.8, sr100: 31.6, sr1k: 52.3, sr10k: null },
  { method: 'RankGuess-PII', venueKey: 'S&P 2025',      approachKey: 'apr_rl',       sr10: null, sr100: 27.8, sr1k: 50.1, sr10k: null },
];

export interface RankRow {
  tool: Tool;
  found: number;
  missed: number;
  coverage: number;        // percent
  min: number | null;
  median: number | null;
  mean: number | null;
  max: number | null;
}

export const rankStats: RankRow[] = [
  { tool: 'CCUPP', found: 168, missed:  32, coverage: 84.0, min: 24, median: 686, mean: 1_775, max: 5_993 },
  { tool: 'CUPP',  found:   0, missed: 200, coverage:  0.0, min: null, median: null, mean: null, max: null },
];

export interface LengthRow {
  bin: string;
  ccupp: number;
  ccuppPct: number;
  cupp: number;
  cuppPct: number;
}

export const lengthDist: LengthRow[] = [
  { bin: '1–6',   ccupp:  2_407, ccuppPct: 20, cupp:    478, cuppPct:  2 },
  { bin: '7–8',   ccupp:  2_080, ccuppPct: 17, cupp:  4_518, cuppPct: 16 },
  { bin: '9–12',  ccupp:  4_388, ccuppPct: 36, cupp: 23_531, cuppPct: 82 },
  { bin: '13–16', ccupp:  2_268, ccuppPct: 18, cupp:      0, cuppPct:  0 },
  { bin: '17–24', ccupp:  1_044, ccuppPct:  8, cupp:      0, cuppPct:  0 },
  { bin: '25+',   ccupp:    148, ccuppPct:  1, cupp:      0, cuppPct:  0 },
];

export interface Reference {
  id: number;
  authors: string;
  title: string;
  venue: string;
}

export const references: Reference[] = [
  { id: 1, authors: 'Wang et al.',     title: 'Targeted Online Password Guessing: An Underestimated Threat',  venue: 'ACM CCS 2016'      },
  { id: 2, authors: 'Li et al.',       title: 'A Large-Scale Empirical Analysis of Chinese Web Passwords',    venue: 'USENIX Sec. 2014' },
  { id: 3, authors: 'Wang & Zou',      title: 'Password Guessing Using Random Forest',                        venue: 'USENIX Sec. 2023' },
  { id: 4, authors: 'Xiu & Wang',      title: 'PointerGuess: Targeted Password Guessing Using Pointer Mechanism', venue: 'USENIX Sec. 2024' },
  { id: 5, authors: 'Zou & Wang',      title: 'Password Guessing Using Large Language Models',                venue: 'USENIX Sec. 2025' },
  { id: 6, authors: 'Yang & Wang',     title: 'RankGuess: Password Guessing Using Adversarial Ranking',       venue: 'IEEE S&P 2025'     },
];

/**
 * Types + academic baselines for the benchmark report.
 *
 * All measured numbers are derived at build time from
 * `benchmark_data/results.json` via `./loader`. The only data hard-coded here
 * is the list of paper baselines (transcribed from each publication) and the
 * bibliography — neither is in JSON.
 */

export type Tool = 'CCUPP' | 'CUPP' | 'bopscrk' | 'PassLLM';

export interface GenRow {
  tool: Tool;
  passwords: number;
  time_s: number;
  pwd_per_s: number;
}

export interface PiiRow {
  tool: Tool;
  name: number;
  date: number;
  phone: number;
  account: number;
  overall: number;
}

export interface SrRow {
  method: string;
  venueKey: string;
  approachKey: string;
  sr10:   number | null;
  sr100:  number | null;
  sr1k:   number | null;
  sr10k:  number | null;
  measured?: boolean;
  ours?: boolean;
}

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

export interface LengthRow {
  bin: string;
  counts: Record<string, number>;
  pcts:   Record<string, number>;
}

export interface Reference {
  id: number;
  authors: string;
  title: string;
  venue: string;
}

/* Academic baselines transcribed from each paper; not in JSON. */
export const academicBaselines: SrRow[] = [
  { method: 'TarGuess-III',  venueKey: 'CCS 2016',      approachKey: 'apr_pcfg_pii', sr10: 4.6,  sr100: 19.7, sr1k: 45.4, sr10k: null },
  { method: 'Personal-PCFG', venueKey: 'USENIX 2014',   approachKey: 'apr_pcfg',     sr10: null, sr100: 12.8, sr1k: 29.5, sr10k: null },
  { method: 'RFGuess-PII',   venueKey: 'USENIX 2023',   approachKey: 'apr_rf',       sr10: 7.3,  sr100: 24.1, sr1k: 48.7, sr10k: null },
  { method: 'PointerGuess',  venueKey: 'USENIX 2024',   approachKey: 'apr_seq',      sr10: 8.2,  sr100: 25.2, sr1k: null, sr10k: null },
  { method: 'PassLLM-I',     venueKey: 'USENIX 2025',   approachKey: 'apr_llm',      sr10: 9.8,  sr100: 31.6, sr1k: 52.3, sr10k: null },
  { method: 'RankGuess-PII', venueKey: 'S&P 2025',      approachKey: 'apr_rl',       sr10: null, sr100: 27.8, sr1k: 50.1, sr10k: null },
];

export const references: Reference[] = [
  { id: 1, authors: 'Wang et al.',     title: 'Targeted Online Password Guessing: An Underestimated Threat',  venue: 'ACM CCS 2016'      },
  { id: 2, authors: 'Li et al.',       title: 'A Large-Scale Empirical Analysis of Chinese Web Passwords',    venue: 'USENIX Sec. 2014' },
  { id: 3, authors: 'Wang & Zou',      title: 'Password Guessing Using Random Forest',                        venue: 'USENIX Sec. 2023' },
  { id: 4, authors: 'Xiu & Wang',      title: 'PointerGuess: Targeted Password Guessing Using Pointer Mechanism', venue: 'USENIX Sec. 2024' },
  { id: 5, authors: 'Zou & Wang',      title: 'Password Guessing Using Large Language Models',                venue: 'USENIX Sec. 2025' },
  { id: 6, authors: 'Yang & Wang',     title: 'RankGuess: Password Guessing Using Adversarial Ranking',       venue: 'IEEE S&P 2025'     },
];

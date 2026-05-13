/**
 * Adapter that exposes the benchmark JSON (produced by `ccupp.benchmark.runner`)
 * as typed structures for the site.
 *
 * Everything measured comes from `benchmark_data/results.json`. The published
 * paper baselines (TarGuess, Personal-PCFG, RFGuess, PointerGuess, PassLLM,
 * RankGuess) are not in JSON; they live in `benchmark.ts` next to types and
 * are merged into `getSuccessRates()` after the measured rows.
 */
import rawResults from '../../../benchmark_data/results.json';

import type {
  Tool, GenRow, PiiRow, SrRow, RankRow, LengthRow,
} from './benchmark';
import { academicBaselines } from './benchmark';

export const PROFILE_ORDER = [
  'zh_full', 'zh_minimal', 'zh_medium', 'en_full', 'en_minimal',
] as const;
export type ProfileName = typeof PROFILE_ORDER[number];

export const PAIRED_DATASET = 'synthetic_200';

type ProfileEntry = {
  results: Record<string, {
    count: number; duration_seconds: number;
    pwd_per_s: number; error: string | null;
  }>;
  pii_embedding_rate: Record<string, {
    name?: number; date?: number; phone?: number;
    account?: number; overall?: number;
  }>;
  length_distribution: Record<string, Record<string, number>>;
  dataset_evals?: Record<string, unknown>;
};

type PairedEntry = {
  num_targets: number;
  success_rates: Record<string, number>;
  coverage: number;
  guess_numbers: {
    found: number; total: number;
    min_rank: number; max_rank: number;
    median_rank: number; mean_rank: number;
  };
};

type Results = Record<string, ProfileEntry> & {
  _academic_paired: Record<string, Record<string, PairedEntry>>;
};

const data = rawResults as unknown as Results;

/** Ordered list of tool names present in the measured data. */
export function getMeasuredTools(): Tool[] {
  const seen = new Set<string>();
  for (const p of PROFILE_ORDER) {
    if (!data[p]) continue;
    for (const t of Object.keys(data[p].results)) seen.add(t);
  }
  return Array.from(seen) as Tool[];
}

export function getGenerationStats(profile: ProfileName): GenRow[] {
  const entry = data[profile];
  if (!entry) return [];
  return Object.entries(entry.results).map(([tool, r]) => ({
    tool: tool as Tool,
    passwords: r.count,
    time_s: r.duration_seconds,
    pwd_per_s: Math.round(r.pwd_per_s),
  }));
}

export function getPiiEmbedding(profile: ProfileName): PiiRow[] {
  const entry = data[profile];
  if (!entry) return [];
  return Object.entries(entry.pii_embedding_rate).map(([tool, r]) => ({
    tool: tool as Tool,
    name:    pct(r.name),
    date:    pct(r.date),
    phone:   pct(r.phone),
    account: pct(r.account),
    overall: pct(r.overall),
  }));
}

/**
 * Measured tools' SR@N + academic baselines, in display order.
 * Tools with empty `success_rates` are surfaced with null values so the
 * renderer prints "—" rather than 0%.
 */
export function getSuccessRates(): SrRow[] {
  const paired = data._academic_paired ?? {};
  const measured: SrRow[] = [];
  for (const tool of getMeasuredTools()) {
    const sr = paired[tool]?.[PAIRED_DATASET]?.success_rates ?? {};
    const has = Object.keys(sr).length > 0;
    measured.push({
      method: tool,
      venueKey: 'lbl_measured',
      approachKey: approachKey(tool),
      sr10:  has ? num(sr['10'])     : null,
      sr100: has ? num(sr['100'])    : null,
      sr1k:  has ? num(sr['1000'])   : null,
      sr10k: has ? num(sr['10000'])  : null,
      measured: true,
      ours: tool === 'CCUPP',
    });
  }
  return [...measured, ...academicBaselines];
}

export function getRankStats(): RankRow[] {
  const paired = data._academic_paired ?? {};
  const out: RankRow[] = [];
  for (const tool of getMeasuredTools()) {
    const ev = paired[tool]?.[PAIRED_DATASET];
    if (!ev) continue;
    const total = ev.num_targets;
    const coveragePct = ev.coverage * 100;
    const foundByCoverage = Math.round(ev.coverage * total);
    const hasRanks = ev.guess_numbers.found > 0;
    out.push({
      tool: tool as Tool,
      found: foundByCoverage,
      missed: total - foundByCoverage,
      coverage: coveragePct,
      min:    hasRanks ? ev.guess_numbers.min_rank    : null,
      median: hasRanks ? Math.round(ev.guess_numbers.median_rank) : null,
      mean:   hasRanks ? Math.round(ev.guess_numbers.mean_rank)   : null,
      max:    hasRanks ? ev.guess_numbers.max_rank    : null,
    });
  }
  return out;
}

const LENGTH_BUCKETS = ['1-6', '7-8', '9-12', '13-16', '17-24', '25+'] as const;

export function getLengthDist(profile: ProfileName): LengthRow[] {
  const entry = data[profile];
  if (!entry) return [];
  const dist = entry.length_distribution;
  const tools = Object.keys(dist) as Tool[];
  const totals: Record<string, number> = {};
  for (const t of tools) {
    totals[t] = Object.values(dist[t]).reduce((a, b) => a + b, 0);
  }
  return LENGTH_BUCKETS.map((bucket) => {
    const counts: Record<string, number> = {};
    const pcts:   Record<string, number> = {};
    for (const t of tools) {
      const c = dist[t][bucket] ?? 0;
      counts[t] = c;
      pcts[t]   = totals[t] > 0 ? (c / totals[t]) * 100 : 0;
    }
    return { bin: bucket.replace('-', '–'), counts, pcts };
  });
}

/** Overlap doughnut for Figure 4a: CCUPP-only vs overlap vs others. */
export function getOverlap(profile: ProfileName): {
  ccuppOnly: number; overlap: number; cuppOnly: number;
} {
  const entry = data[profile];
  if (!entry) return { ccuppOnly: 0, overlap: 0, cuppOnly: 0 };
  const ccupp = entry.results.CCUPP?.count ?? 0;
  const cupp  = entry.results.CUPP?.count ?? 0;
  // Without exposed candidate sets we can't compute exact overlap from JSON;
  // surface counts and let the chart fall back to the (small) historical
  // overlap figure if a future export includes it.
  return { ccuppOnly: ccupp, overlap: 0, cuppOnly: cupp };
}

/* -- helpers -------------------------------------------------------------- */

function num(v: number | undefined): number | null {
  return v === undefined ? null : Math.round(v * 1000) / 10; // 0.455 → 45.5
}

function pct(v: number | undefined): number {
  // pii_embedding_rate values are already fractions in JSON; surface as percent.
  return v === undefined ? 0 : Math.round(v * 1000) / 10;
}

function approachKey(tool: string): string {
  switch (tool) {
    case 'CCUPP':   return 'apr_rb_pii';
    case 'CUPP':    return 'apr_rb';
    case 'bopscrk': return 'apr_rb';
    case 'PassLLM': return 'apr_llm';
    default:        return 'apr_rb';
  }
}

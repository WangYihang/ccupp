/**
 * Chart.js initialisation for the benchmark report.
 *
 * Every chart is built from the JSON-driven data exposed by `../data/loader`;
 * the same numbers feed the tables in `index.astro`. Chart.js itself is loaded
 * via a `<script src>` tag in `Layout.astro`, so the global `Chart` symbol is
 * referenced at runtime here.
 *
 * `initCharts()` returns `{ chartId → Chart instance }` so the i18n runtime
 * can re-label axes and legends on language switch.
 */

declare const Chart: any;

import { academicBaselines } from '../data/benchmark';
import type { Tool } from '../data/benchmark';
import {
  PROFILE_ORDER,
  getGenerationStats,
  getPiiEmbedding,
  getSuccessRates,
  getRankStats,
  getLengthDist,
  getMeasuredTools,
} from '../data/loader';

const palette = {
  ours:     '#8b1a1a',
  baseline: '#555555',
  a:        '#1c4587',
  b:        '#4a7a4a',
  c:        '#a07a1a',
  d:        '#6a3a8a',
  overlap:  '#a07a1a',
  grid:     '#e6e6e6',
} as const;

/* Stable color per measured tool. CCUPP keeps the ours hue; others take
 * neutral / accent colors. */
const TOOL_COLOR: Record<string, string> = {
  CCUPP:   palette.ours,
  CUPP:    palette.baseline,
  bopscrk: palette.b,
  PassLLM: palette.d,
};

const SERIF = "'Source Serif 4', Charter, Cambria, Georgia, serif";
const SANS  = "'Inter', -apple-system, system-ui, sans-serif";

function applyDefaults(): void {
  Chart.defaults.font.family = SANS;
  Chart.defaults.font.size   = 11;
  Chart.defaults.color       = '#333';
  Chart.defaults.borderColor = palette.grid;
  Chart.defaults.plugins.legend.labels.boxWidth  = 10;
  Chart.defaults.plugins.legend.labels.boxHeight = 10;
  Chart.defaults.plugins.legend.labels.font = { family: SANS, size: 11 };
  Chart.defaults.plugins.legend.position = 'top';
  Chart.defaults.plugins.legend.align    = 'end';
  Chart.defaults.plugins.tooltip.titleFont = { family: SANS, weight: '600' };
  Chart.defaults.plugins.tooltip.bodyFont  = { family: SANS };
}

function axis(title?: string) {
  return {
    grid:   { color: palette.grid, drawTicks: false, drawBorder: false, lineWidth: 0.5 },
    border: { display: false },
    ticks:  { color: '#555', padding: 4, font: { family: SANS, size: 10 } },
    title:  title
      ? { display: true, text: title, color: '#333', font: { family: SERIF, size: 11, style: 'italic' } }
      : { display: false },
  };
}

function multiBar(
  canvasId: string,
  labels: string[],
  series: { label: string; data: number[]; color: string }[],
  yTitle: string,
) {
  const el = document.getElementById(canvasId);
  if (!el) return null;
  return new Chart(el as HTMLCanvasElement, {
    type: 'bar',
    data: {
      labels,
      datasets: series.map((s) => ({
        label: s.label,
        data: s.data,
        backgroundColor: s.color,
        borderWidth: 0,
        barPercentage: 0.78,
        categoryPercentage: 0.78,
      })),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: true } },
      scales: { x: axis(), y: axis(yTitle) },
    },
  });
}

export type Charts = Record<string, any>;

export function initCharts(): Charts {
  applyDefaults();
  const charts: Charts = {};

  const measuredTools = getMeasuredTools();
  const toolColor = (t: Tool) => TOOL_COLOR[t] ?? palette.a;
  const perProfile = PROFILE_ORDER.map((p) => ({ profile: p, rows: getGenerationStats(p) }));

  charts.speed = multiBar(
    'speedChart',
    perProfile.map((p) => p.profile),
    measuredTools.map((t) => ({
      label: t,
      color: toolColor(t),
      data: perProfile.map((p) => p.rows.find((r) => r.tool === t)?.pwd_per_s ?? 0),
    })),
    'passwords / second',
  );

  charts.count = multiBar(
    'countChart',
    perProfile.map((p) => p.profile),
    measuredTools.map((t) => ({
      label: t,
      color: toolColor(t),
      data: perProfile.map((p) => p.rows.find((r) => r.tool === t)?.passwords ?? 0),
    })),
    '# candidates generated',
  );

  const piiZh = getPiiEmbedding('zh_full');
  const piiEl = document.getElementById('piiChart');
  if (piiEl) {
    charts.pii = new Chart(piiEl as HTMLCanvasElement, {
      type: 'bar',
      data: {
        labels: ['Name', 'Date', 'Phone', 'Account', 'Overall'],
        datasets: piiZh.map((row) => ({
          label: row.tool,
          data: [row.name, row.date, row.phone, row.account, row.overall],
          backgroundColor: toolColor(row.tool),
          borderWidth: 0,
          barPercentage: 0.78,
          categoryPercentage: 0.72,
        })),
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: true } },
        scales: { x: axis(), y: { ...axis('embedding rate (%)'), suggestedMax: 60, beginAtZero: true } },
      },
    });
  }

  const srEl = document.getElementById('srChart');
  if (srEl) {
    const srRows = getSuccessRates();
    const measuredRows = srRows.filter((r) => r.measured);
    charts.sr = new Chart(srEl as HTMLCanvasElement, {
      type: 'line',
      data: {
        labels: ['10', '10²', '10³', '10⁴'],
        datasets: [
          ...measuredRows.map((r) => ({
            label: `${r.method} (measured)`,
            data: [r.sr10, r.sr100, r.sr1k, r.sr10k],
            borderColor: toolColor(r.method as Tool),
            backgroundColor: (toolColor(r.method as Tool)) + '18',
            borderWidth: r.ours ? 2.5 : 1.5,
            borderDash: r.ours ? undefined : [4, 3],
            pointRadius: r.ours ? 4 : 3,
            pointHoverRadius: 6,
            tension: r.ours ? 0.18 : 0,
            spanGaps: false,
            fill: false,
          })),
          ...academicBaselines.map((r, i) => {
            const colors = [palette.a, palette.b, palette.c, palette.d, palette.overlap, '#555'];
            return {
              label: `${r.method} · ${r.venueKey}`,
              data: [r.sr10, r.sr100, r.sr1k, r.sr10k],
              borderColor: colors[i % colors.length],
              borderWidth: 1.2,
              pointRadius: 3,
              tension: 0.15,
              spanGaps: false,
            };
          }),
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'bottom',
            align: 'center',
            labels: { boxWidth: 18, boxHeight: 2, font: { family: SANS, size: 10 } },
          },
        },
        scales: {
          x: axis('guess budget N'),
          y: { ...axis('success rate (%)'), min: 0, max: 100 },
        },
      },
    });
  }

  // Overlap doughnut — covered total candidates per tool from zh_full.
  // Exact intersection isn't in the JSON, so this falls back to count-only.
  const overlapEl = document.getElementById('overlapChart');
  if (overlapEl) {
    const zhFull = getGenerationStats('zh_full');
    charts.overlap = new Chart(overlapEl as HTMLCanvasElement, {
      type: 'doughnut',
      data: {
        labels: zhFull.map((r) => r.tool),
        datasets: [{
          data: zhFull.map((r) => r.passwords),
          backgroundColor: zhFull.map((r) => toolColor(r.tool)),
          borderColor: '#fff',
          borderWidth: 1.5,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '58%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: { boxWidth: 10, boxHeight: 10, font: { family: SANS, size: 10 } },
          },
        },
      },
    });
  }

  const lengthRows = getLengthDist('zh_full');
  charts.length = multiBar(
    'lengthChart',
    lengthRows.map((r) => r.bin),
    measuredTools.map((t) => ({
      label: t,
      color: toolColor(t),
      data: lengthRows.map((r) => r.pcts[t] ?? 0),
    })),
    'share of output (%)',
  );

  // Expose ranked stats unused-but-loaded so tree-shaking keeps the function call
  // around for future charts; cheap.
  void getRankStats;

  return charts;
}

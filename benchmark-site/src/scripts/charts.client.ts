/**
 * Chart.js initialisation for the benchmark report.
 *
 * Exposes `initCharts()` which builds every chart on the page using a
 * shared academic palette + axis-options helper, and returns a map of
 * `{ chartId → Chart instance }` so the i18n runtime can re-label
 * axes / datasets on language switch.
 *
 * Chart.js is loaded via a separate `<script src>` in the HTML head;
 * this module references the global `Chart` constructor at runtime.
 */

declare const Chart: any;

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

function bar(canvasId: string, labels: string[], ccupp: number[], cupp: number[], yTitle: string) {
  const el = document.getElementById(canvasId);
  if (!el) return null;
  return new Chart(el as HTMLCanvasElement, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        { label: 'CCUPP', data: ccupp, backgroundColor: palette.ours,     borderWidth: 0, barPercentage: 0.7, categoryPercentage: 0.72 },
        { label: 'CUPP',  data: cupp,  backgroundColor: palette.baseline, borderWidth: 0, barPercentage: 0.7, categoryPercentage: 0.72 },
      ],
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

  charts.speed = bar(
    'speedChart',
    ['zh_full', 'zh_minimal', 'zh_medium', 'en_full', 'en_minimal'],
    [2_216_275, 2_582_046, 2_349_384, 2_915_031, 2_913_166],
    [  277_964,   292_689,   430_639,   496_836,   431_200],
    'passwords / second',
  );

  charts.count = bar(
    'countChart',
    ['zh_full', 'zh_minimal', 'zh_medium', 'en_full', 'en_minimal'],
    [12_335, 4_244, 9_007, 4_432, 2_076],
    [28_527, 5_230, 18_594, 22_304, 9_546],
    '# candidates generated',
  );

  const piiEl = document.getElementById('piiChart');
  if (piiEl) {
    charts.pii = new Chart(piiEl as HTMLCanvasElement, {
      type: 'bar',
      data: {
        labels: ['Name', 'Date', 'Phone', 'Account', 'Overall'],
        datasets: [
          { label: 'CCUPP', data: [22.4, 20.8, 8.9, 5.1, 48.2], backgroundColor: palette.ours,     borderWidth: 0, barPercentage: 0.66, categoryPercentage: 0.72 },
          { label: 'CUPP',  data: [27.1, 4.6, 0.0, 7.3, 33.2],  backgroundColor: palette.baseline, borderWidth: 0, barPercentage: 0.66, categoryPercentage: 0.72 },
        ],
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
    charts.sr = new Chart(srEl as HTMLCanvasElement, {
      type: 'line',
      data: {
        labels: ['10', '10²', '10³', '10⁴'],
        datasets: [
          { label: 'CCUPP (measured)', data: [0,   1.0,  45.5, 84.0], borderColor: palette.ours,     backgroundColor: palette.ours + '18', borderWidth: 2.5, pointRadius: 4, pointHoverRadius: 6, tension: 0.18, fill: false },
          { label: 'CUPP (measured)',  data: [0,   0,    0,    0.0],  borderColor: palette.baseline, borderWidth: 1.5, borderDash: [4, 3], pointRadius: 3, tension: 0 },
          { label: 'TarGuess-III · CCS 2016',  data: [4.6, 19.7, 45.4, null], borderColor: palette.a, borderWidth: 1.5, pointRadius: 3, tension: 0.15, spanGaps: false },
          { label: 'RFGuess-PII · Sec. 2023',  data: [7.3, 24.1, 48.7, null], borderColor: palette.b, borderWidth: 1.5, pointRadius: 3, tension: 0.15, spanGaps: false },
          { label: 'PointerGuess · Sec. 2024', data: [8.2, 25.2, null, null], borderColor: palette.c, borderWidth: 1.5, pointRadius: 3, tension: 0.15, spanGaps: false },
          { label: 'PassLLM-I · Sec. 2025',    data: [9.8, 31.6, 52.3, null], borderColor: palette.d, borderWidth: 1.5, pointRadius: 3, tension: 0.15, spanGaps: false },
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

  const overlapEl = document.getElementById('overlapChart');
  if (overlapEl) {
    charts.overlap = new Chart(overlapEl as HTMLCanvasElement, {
      type: 'doughnut',
      data: {
        labels: ['CCUPP only', 'Overlap', 'CUPP only'],
        datasets: [{
          data: [12_085, 250, 28_277],
          backgroundColor: [palette.ours, palette.overlap, palette.baseline],
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

  charts.length = bar(
    'lengthChart',
    ['1–6', '7–8', '9–12', '13–16', '17–24', '25+'],
    [20, 17, 36, 18, 8, 1],
    [ 2, 16, 82,  0, 0, 0],
    'share of output (%)',
  );

  return charts;
}

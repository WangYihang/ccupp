/**
 * Runtime EN ↔ 中文 toggle.
 *
 * Strategy
 *   • Every translatable node carries `data-i18n="key"` (textContent
 *     replacement) or `data-i18n-html="key"` (innerHTML replacement).
 *   • On first run we snapshot the rendered English text/HTML as the
 *     canonical EN value, so we never need to ship two copies in the
 *     DOM — the SSR-rendered English IS the English version.
 *   • On switch we rewrite the snapshots back (→ EN) or look up `ZH[k]`
 *     (→ 中文), then rewire chart axis / dataset labels.
 *   • Preference is persisted in `localStorage["ccupp-lang"]`.
 */

import { ZH, docTitles, type StringKey } from '../data/i18n';
import type { Charts } from './charts.client';

type Lang = 'en' | 'zh';

const STORAGE_KEY = 'ccupp-lang';

interface ChartMessages {
  measured:   string;
  y_pps:      string;
  y_count:    string;
  y_pii:      string;
  x_n:        string;
  y_sr:       string;
  x_len:      string;
  y_share:    string;
  pii_labels: [string, string, string, string, string];
}

const CHART_EN: ChartMessages = {
  measured:   '(measured)',
  y_pps:      'passwords / second',
  y_count:    '# candidates generated',
  y_pii:      'embedding rate (%)',
  x_n:        'guess budget N',
  y_sr:       'success rate (%)',
  x_len:      'length (chars)',
  y_share:    'share of output (%)',
  pii_labels: ['Name', 'Date', 'Phone', 'Account', 'Overall'],
};

const CHART_ZH: ChartMessages = {
  measured:   '（实测）',
  y_pps:      '候选 / 秒',
  y_count:    '候选总数',
  y_pii:      '嵌入率（%）',
  x_n:        '猜测预算 N',
  y_sr:       '成功率（%）',
  x_len:      '长度（字符）',
  y_share:    '输出占比（%）',
  pii_labels: ['姓名', '日期', '电话', '账号', '整体'],
};

function snapshotOriginals(): void {
  document.querySelectorAll<HTMLElement>('[data-i18n]').forEach((el) => {
    if (el.dataset.orig === undefined) el.dataset.orig = el.textContent ?? '';
  });
  document.querySelectorAll<HTMLElement>('[data-i18n-html]').forEach((el) => {
    if (el.dataset.origHtml === undefined) el.dataset.origHtml = el.innerHTML;
  });
}

function applyDom(lang: Lang): void {
  document.querySelectorAll<HTMLElement>('[data-i18n]').forEach((el) => {
    const k = el.dataset.i18n as StringKey;
    el.textContent = lang === 'zh' && ZH[k] !== undefined ? ZH[k] : (el.dataset.orig ?? '');
  });
  document.querySelectorAll<HTMLElement>('[data-i18n-html]').forEach((el) => {
    const k = el.dataset.i18nHtml as StringKey;
    el.innerHTML = lang === 'zh' && ZH[k] !== undefined ? ZH[k] : (el.dataset.origHtml ?? '');
  });
}

/** Strip any " (measured)"/"（实测）" suffix so we can re-attach in the target lang. */
function stripMeasured(label: string): string {
  return label.replace(/\s*\((measured|实测)\)\s*$/u, '')
              .replace(/\s*（(measured|实测)）\s*$/u, '');
}

function applyCharts(lang: Lang, charts: Charts): void {
  const t = lang === 'zh' ? CHART_ZH : CHART_EN;

  const relabelMeasured = (chart: any) => {
    for (const ds of chart.data.datasets) {
      // Tool names (CCUPP / CUPP / bopscrk / PassLLM) are language-neutral; only
      // the " (measured)" suffix translates. SR-chart academic-baseline datasets
      // ("TarGuess-III · CCS 2016") have no suffix and pass through unchanged.
      const bare = stripMeasured(ds.label ?? '');
      // Heuristic: a dataset is "measured" when the bare label is a known tool
      // (no venue dot). Academic baselines all contain " · " for the venue.
      const isMeasured = !bare.includes('·');
      ds.label = isMeasured ? `${bare} ${t.measured}` : bare;
    }
  };

  if (charts.speed) {
    charts.speed.options.scales.y.title.text = t.y_pps;
    charts.speed.update();
  }
  if (charts.count) {
    charts.count.options.scales.y.title.text = t.y_count;
    charts.count.update();
  }
  if (charts.pii) {
    charts.pii.data.labels = t.pii_labels;
    charts.pii.options.scales.y.title.text = t.y_pii;
    charts.pii.update();
  }
  if (charts.sr) {
    relabelMeasured(charts.sr);
    charts.sr.options.scales.x.title.text = t.x_n;
    charts.sr.options.scales.y.title.text = t.y_sr;
    charts.sr.update();
  }
  if (charts.overlap) {
    // Overlap labels are tool names; keep as-is.
    charts.overlap.update();
  }
  if (charts.length) {
    charts.length.options.scales.x.title.text = t.x_len;
    charts.length.options.scales.y.title.text = t.y_share;
    charts.length.update();
  }
}

function applyChrome(lang: Lang): void {
  const btn = document.getElementById('lang-toggle');
  if (btn) btn.textContent = lang === 'zh' ? 'EN' : '中文';
  document.documentElement.lang = lang;
  document.title = docTitles[lang];
}

export function setupI18n(charts: Charts): void {
  snapshotOriginals();

  let current: Lang = 'en';
  const set = (lang: Lang): void => {
    current = lang;
    applyDom(lang);
    applyCharts(lang, charts);
    applyChrome(lang);
    try { localStorage.setItem(STORAGE_KEY, lang); } catch { /* ignore quota / private mode */ }
  };

  const btn = document.getElementById('lang-toggle');
  if (btn) btn.addEventListener('click', () => set(current === 'en' ? 'zh' : 'en'));

  let saved: string | null = null;
  try { saved = localStorage.getItem(STORAGE_KEY); } catch { /* ignore */ }
  if (saved === 'zh') set('zh');
}

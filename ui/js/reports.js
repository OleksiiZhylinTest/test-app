import { IS_SERVED, STORE_KEYS } from './config.js';
import { store } from './store.js';
import { getReports, deleteReport } from './api.js';

const reportsList   = () => document.getElementById('reports-list');
const reportsEmpty  = () => document.getElementById('reports-empty');
const reportsSelect = () => document.getElementById('reports-filter-select');

let _activeFilter = '';
let _lastEntries  = [];

function renderReports(entries) {
  _lastEntries = entries || [];
  const listEl   = reportsList();
  const emptyEl  = reportsEmpty();
  const selectEl = reportsSelect();

  // Rebuild dropdown options from unique filter names (insertion order = newest-first)
  if (selectEl) {
    const seen = new Set();
    const names = [];
    for (const e of _lastEntries) {
      const key = e.filter_name || e.ts;
      if (!seen.has(key)) { seen.add(key); names.push(key); }
    }
    // Preserve current selection if still valid
    if (_activeFilter && !seen.has(_activeFilter)) _activeFilter = '';
    selectEl.innerHTML = '<option value="">All filters</option>';
    for (const name of names) {
      const opt = document.createElement('option');
      opt.value = name;
      opt.textContent = name;
      if (name === _activeFilter) opt.selected = true;
      selectEl.appendChild(opt);
    }
  }

  // Compute display subset
  const visible = _activeFilter
    ? _lastEntries.filter((e) => (e.filter_name || e.ts) === _activeFilter)
    : _lastEntries.slice(0, 20);

  listEl.innerHTML = '';
  if (!visible.length) {
    emptyEl.hidden = false;
    return;
  }
  emptyEl.hidden = true;

  for (const { ts, html_file, md_file } of visible) {
    const hFile = html_file || 'report.html';
    const li = document.createElement('li');

    const htmlLink = document.createElement('a');
    htmlLink.href = `generated/reports/${ts}/${hFile}`;
    htmlLink.target = '_blank';
    htmlLink.rel = 'noopener';
    htmlLink.innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg> ${hFile}`;
    htmlLink.style.cssText = 'flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;';

    const removeBtn = document.createElement('button');
    removeBtn.className = 'btn btn-danger';
    removeBtn.style.cssText = 'font-size:0.72rem;padding:4px 10px;flex-shrink:0;';
    removeBtn.textContent = 'Remove';
    removeBtn.type = 'button';
    removeBtn.addEventListener('click', async () => {
      removeBtn.disabled = true;
      removeBtn.textContent = 'Removing…';
      if (IS_SERVED) {
        try { await deleteReport(ts, hFile); } catch {}
      }
      const saved = store.getJSON(STORE_KEYS.REPORTS) || [];
      store.setJSON(STORE_KEYS.REPORTS, saved.filter(
        (r) => !(r.ts === ts && r.html_file === hFile)
      ));
      loadReports();
    });

    li.appendChild(htmlLink);
    li.appendChild(removeBtn);
    listEl.appendChild(li);
  }
}

export async function loadReports() {
  if (IS_SERVED) {
    try {
      const data = await getReports();
      if (Array.isArray(data.reports)) {
        const serverKeys = new Set(data.reports.map((r) => `${r.ts}|${r.html_file}`));
        const local = store.getJSON(STORE_KEYS.REPORTS) || [];
        const localMap = {};
        for (const r of local) { localMap[`${r.ts}|${r.html_file}`] = r; }
        const enriched = data.reports.map((r) => ({
          ...r,
          filter_name: localMap[`${r.ts}|${r.html_file}`]?.filter_name || null,
        }));
        const localOnly = local.filter((r) => !serverKeys.has(`${r.ts}|${r.html_file}`));
        renderReports([...enriched, ...localOnly]);
        return;
      }
    } catch {
      // fall through to localStorage fallback
    }
  }
  renderReports(store.getJSON(STORE_KEYS.REPORTS) || []);
}

export function addReport(ts, htmlFile, mdFile, filterName) {
  const saved = store.getJSON(STORE_KEYS.REPORTS) || [];
  if (!saved.find((r) => r.ts === ts && r.html_file === htmlFile)) {
    saved.unshift({ ts, html_file: htmlFile || null, md_file: mdFile || null, filter_name: filterName || null });
    store.setJSON(STORE_KEYS.REPORTS, saved.slice(0, 50));
  }
  loadReports();
}

export function initReportsFilter() {
  const selectEl = reportsSelect();
  if (!selectEl) return;
  selectEl.addEventListener('change', () => {
    _activeFilter = selectEl.value;
    renderReports(_lastEntries);
  });
}

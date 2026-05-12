import { getFilters } from './api.js';

let _currentSlug = '';
let _records = [];
let _roster = {}; // {username: role}

// ── helpers ──────────────────────────────────────────────────────────────────

function _escHtml(s) {
  return String(s ?? '')
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function _setStatus(msg, isError = false) {
  const el = document.getElementById('dau-import-status');
  if (!el) return;
  el.textContent = msg;
  el.style.color = isError ? 'var(--error)' : 'var(--text-muted)';
}

function _setRecordError(msg) {
  const el = document.getElementById('err-dau-record');
  if (!el) return;
  el.textContent = msg;
  el.classList.toggle('visible', !!msg);
}

// ── ISO week helpers ──────────────────────────────────────────────────────────

function _isoWeekString(date) {
  const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
  d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay() || 7));
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
  const weekNo = Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
  return `${d.getUTCFullYear()}-W${String(weekNo).padStart(2, '0')}`;
}

function _populateImportWeekDropdown() {
  const sel = document.getElementById('dau-import-week');
  if (!sel) return;
  const today = new Date();
  const current = _isoWeekString(today);
  sel.innerHTML = '';
  for (let offset = -8; offset <= 2; offset++) {
    const d = new Date(today);
    d.setDate(d.getDate() + offset * 7);
    const w = _isoWeekString(d);
    const opt = document.createElement('option');
    opt.value = w;
    opt.textContent = w + (offset === 0 ? ' (current)' : '');
    if (w === current) opt.selected = true;
    sel.appendChild(opt);
  }
}

function _weeksForYear(year) {
  const result = [];
  const jan4 = new Date(Date.UTC(year, 0, 4));
  const d = new Date(jan4);
  d.setUTCDate(d.getUTCDate() - ((d.getUTCDay() + 6) % 7));
  while (true) {
    const w = _isoWeekString(d);
    if (!w.startsWith(String(year))) break;
    result.push(w);
    d.setUTCDate(d.getUTCDate() + 7);
  }
  return result;
}

function _populateRecordWeekDropdown(selectedWeek) {
  const sel = document.getElementById('dau-rec-week');
  if (!sel) return;
  const today = new Date();
  const currentWeek = _isoWeekString(today);
  const target = selectedWeek || currentWeek;
  const currentYear = today.getFullYear();

  const weeks = [..._weeksForYear(currentYear - 1), ..._weeksForYear(currentYear)].reverse();

  sel.innerHTML = '';
  let hasTarget = false;
  weeks.forEach((w) => {
    const opt = document.createElement('option');
    opt.value = w;
    opt.textContent = w + (w === currentWeek ? ' (current)' : '');
    if (w === target) { opt.selected = true; hasTarget = true; }
    sel.appendChild(opt);
  });

  if (!hasTarget && target) {
    const opt = document.createElement('option');
    opt.value = target;
    opt.textContent = target;
    opt.selected = true;
    sel.insertBefore(opt, sel.firstChild);
  }
}

// ── filter selector ───────────────────────────────────────────────────────────

async function _populateFilterSelect() {
  const sel = document.getElementById('dau-filter-select');
  if (!sel) return;
  try {
    const data = await getFilters();
    const filters = data.filters || [];
    sel.innerHTML = '<option value="">— Select a team —</option>';
    for (const f of filters) {
      const opt = document.createElement('option');
      opt.value = f.slug || '';
      opt.textContent = f.filter_name || f.slug || '(unnamed)';
      sel.appendChild(opt);
    }
  } catch (_) {}
}

// ── record filters ────────────────────────────────────────────────────────────

function _applyFilters() {
  const week = document.getElementById('dau-filter-week')?.value || '';
  const name = (document.getElementById('dau-filter-name')?.value || '').toLowerCase();
  const role = document.getElementById('dau-filter-role')?.value || '';
  return _records.filter((r) =>
    (!week || r.week === week) &&
    (!name || r.username.toLowerCase().includes(name)) &&
    (!role || r.role === role),
  );
}

function _refreshWeekFilter() {
  const sel = document.getElementById('dau-filter-week');
  if (!sel) return;
  const weeks = [...new Set(_records.map((r) => r.week))].sort().reverse();
  const current = sel.value;
  sel.innerHTML = '<option value="">— All weeks —</option>';
  weeks.forEach((w) => {
    const opt = document.createElement('option');
    opt.value = w;
    opt.textContent = w;
    if (w === current) opt.selected = true;
    sel.appendChild(opt);
  });
}

function _resetFilters() {
  ['dau-filter-week', 'dau-filter-role'].forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.value = '';
  });
  const n = document.getElementById('dau-filter-name');
  if (n) n.value = '';
}

// ── records table ─────────────────────────────────────────────────────────────

function _renderTable(records) {
  const tbody = document.getElementById('dau-records-tbody');
  const countEl = document.getElementById('dau-records-count');
  if (!tbody) return;

  // Page-size cap
  const pageSize = parseInt(document.getElementById('dau-page-size')?.value || '100', 10);
  const total = records.length;
  const display = pageSize > 0 ? records.slice(0, pageSize) : records;

  const dispEl = document.getElementById('dau-records-displayed');
  if (dispEl) {
    dispEl.textContent = pageSize > 0 && total > pageSize ? `Showing ${display.length} of ${total}` : '';
  }

  if (countEl) countEl.textContent = total ? `(${total})` : '';

  if (!display.length) {
    tbody.innerHTML = `<tr id="dau-empty-row"><td colspan="6" style="text-align:center;padding:24px;color:var(--text-muted);">No records found for this team.</td></tr>`;
    return;
  }

  tbody.innerHTML = display.map((r) => `
    <tr data-username="${_escHtml(r.username)}" data-week="${_escHtml(r.week)}" style="border-bottom:1px solid var(--border);">
      <td style="padding:7px 10px;">${_escHtml(r.week)}</td>
      <td style="padding:7px 10px;">${_escHtml(r.username)}</td>
      <td style="padding:7px 10px;">${_escHtml(r.role || '—')}</td>
      <td style="padding:7px 10px;">${_escHtml(r.usage)}</td>
      <td style="padding:7px 10px;text-align:right;">${r.score ?? '—'}</td>
      <td style="padding:7px 10px;text-align:center;white-space:nowrap;">
        <button class="btn btn-secondary dau-edit-btn"
          data-username="${_escHtml(r.username)}" data-week="${_escHtml(r.week)}"
          style="padding:4px 10px;font-size:0.8rem;" aria-label="Edit record">Edit</button>
        <button class="btn dau-delete-btn"
          data-username="${_escHtml(r.username)}" data-week="${_escHtml(r.week)}"
          style="padding:4px 10px;font-size:0.8rem;background:var(--error);color:#fff;border-color:var(--error);"
          aria-label="Delete record">Delete</button>
      </td>
    </tr>
  `).join('');

  // Wire edit/delete buttons
  tbody.querySelectorAll('.dau-edit-btn').forEach((btn) => {
    btn.addEventListener('click', () => _onEdit(btn.dataset.username, btn.dataset.week));
  });
  tbody.querySelectorAll('.dau-delete-btn').forEach((btn) => {
    btn.addEventListener('click', () => _onDelete(btn.dataset.username, btn.dataset.week));
  });
}

// ── load records ─────────────────────────────────────────────────────────────

async function _loadRecords(slug) {
  const tbody = document.getElementById('dau-records-tbody');
  if (tbody) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:24px;color:var(--text-muted);">Loading…</td></tr>`;
  }
  _resetFilters();
  try {
    const res = await fetch(`/api/dau/records?filter=${encodeURIComponent(slug)}`);
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || 'Server error');
    _records = data.records || [];
    _refreshWeekFilter();
    _renderTable(_records);
  } catch (err) {
    if (tbody) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:24px;color:var(--error);">Failed to load records: ${_escHtml(String(err))}</td></tr>`;
    }
  }
}

// ── roster ────────────────────────────────────────────────────────────────────

async function _loadRoster(slug) {
  _roster = {};
  try {
    const res = await fetch(`/api/dau/roster?filter=${encodeURIComponent(slug)}`);
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || 'Server error');
    (data.roster || []).forEach((e) => { _roster[e.username] = e.role; });
    _renderRoster(data.roster || []);
  } catch (_) {
    _renderRoster([]);
  }
}

function _renderRoster(entries) {
  const tbody = document.getElementById('dau-roster-tbody');
  if (!tbody) return;
  if (!entries.length) {
    tbody.innerHTML = '<tr><td colspan="3" style="text-align:center;padding:16px;color:var(--text-muted);">No roster entries.</td></tr>';
    return;
  }
  tbody.innerHTML = entries.map((e) => `
    <tr style="border-bottom:1px solid var(--border);">
      <td style="padding:6px 10px;">${_escHtml(e.username)}</td>
      <td style="padding:6px 10px;">${_escHtml(e.role || '\u2014')}</td>
      <td style="text-align:center;padding:6px 10px;">
        <button class="btn btn-secondary dau-roster-remove-btn"
          data-username="${_escHtml(e.username)}"
          style="padding:3px 8px;font-size:0.8rem;" aria-label="Remove">Remove</button>
      </td>
    </tr>
  `).join('');
  tbody.querySelectorAll('.dau-roster-remove-btn').forEach((btn) => {
    btn.addEventListener('click', () => _removeRosterEntry(btn.dataset.username));
  });
}

async function _addRosterEntry() {
  const usernameEl = document.getElementById('dau-roster-username');
  const roleEl = document.getElementById('dau-roster-role');
  const errEl = document.getElementById('err-dau-roster');
  const username = (usernameEl?.value || '').trim();
  const role = roleEl?.value || '';
  if (!username) {
    if (errEl) { errEl.textContent = 'Username is required'; errEl.classList.add('visible'); }
    return;
  }
  if (errEl) { errEl.textContent = ''; errEl.classList.remove('visible'); }
  try {
    const res = await fetch(`/api/dau/roster?filter=${encodeURIComponent(_currentSlug)}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, role }),
    });
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || 'Save failed');
    if (usernameEl) usernameEl.value = '';
    if (roleEl) roleEl.value = '';
    await _loadRoster(_currentSlug);
  } catch (err) {
    if (errEl) { errEl.textContent = String(err); errEl.classList.add('visible'); }
  }
}

async function _removeRosterEntry(username) {
  if (!confirm(`Remove ${username} from the roster?`)) return;
  try {
    const params = new URLSearchParams({ filter: _currentSlug, username });
    const res = await fetch(`/api/dau/roster?${params}`, { method: 'DELETE' });
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || 'Delete failed');
    await _loadRoster(_currentSlug);
  } catch (err) {
    alert(`Failed to remove roster entry: ${err}`);
  }
}

// ── Excel import ──────────────────────────────────────────────────────────────

async function _importExcel(slug, file) {
  _setStatus('Reading file…');
  const btn = document.getElementById('btn-dau-import');
  if (btn) btn.disabled = true;

  try {
    const b64 = await new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        // result is data:<mime>;base64,<data>
        const raw = reader.result;
        resolve(raw.split(',')[1] || '');
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });

    const targetWeek = document.getElementById('dau-import-week')?.value || '';
    const res = await fetch(`/api/dau/import?filter=${encodeURIComponent(slug)}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filename: file.name, data_b64: b64, target_week: targetWeek }),
    });
    const data = await res.json();
    if (!data.ok && !('imported' in data)) throw new Error(data.error || 'Import failed');

    const { imported = 0, skipped = 0, errors = [] } = data;
    let msg = `Imported ${imported}, skipped ${skipped}.`;
    if (errors.length) msg += ` ${errors.length} warning(s): ${errors.slice(0, 3).join('; ')}`;
    _setStatus(msg, errors.length > 0 && imported === 0);

    // Reload the table to reflect new records
    await _loadRecords(slug);
  } catch (err) {
    _setStatus(`Import failed: ${err}`, true);
  } finally {
    if (btn) btn.disabled = false;
    // Clear file input so re-importing same file works
    const fileEl = document.getElementById('dau-import-file');
    if (fileEl) fileEl.value = '';
  }
}

// ── save record (add / edit) ──────────────────────────────────────────────────

async function _saveRecord(slug) {
  const weekEl  = document.getElementById('dau-rec-week');
  const userEl  = document.getElementById('dau-rec-username');
  const roleEl  = document.getElementById('dau-rec-role');
  const usageEl = document.getElementById('dau-rec-usage');

  const week     = weekEl?.value.trim() || '';
  const username = userEl?.value.trim() || '';
  const role     = roleEl?.value || '';
  const usage    = usageEl?.value || '';

  if (!week) { _setRecordError('ISO Week is required (e.g. 2026-W20)'); return; }
  if (!username) { _setRecordError('Username is required'); return; }
  if (!usage) { _setRecordError('Usage selection is required'); return; }

  _setRecordError('');
  const btn = document.getElementById('btn-dau-save-record');
  if (btn) btn.disabled = true;

  // Include original key so server can clean up old files when week/username changes
  const editingKey = document.getElementById('dau-rec-editing-key')?.value || '';
  const [origUsername = '', origWeek = ''] = editingKey ? editingKey.split('||') : [];
  const body = { username, week, role, usage };
  if (origUsername && origWeek) {
    body.orig_username = origUsername;
    body.orig_week = origWeek;
  }

  try {
    const res = await fetch(`/api/dau/records?filter=${encodeURIComponent(slug)}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || 'Save failed');

    _resetForm();
    await _loadRecords(slug);
  } catch (err) {
    _setRecordError(String(err));
  } finally {
    if (btn) btn.disabled = false;
  }
}

// ── delete record ─────────────────────────────────────────────────────────────

async function _onDelete(username, week) {
  if (!confirm(`Delete record for ${username} / ${week}?`)) return;
  try {
    const params = new URLSearchParams({ filter: _currentSlug, username, week });
    const res = await fetch(`/api/dau/records?${params}`, { method: 'DELETE' });
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || 'Delete failed');
    await _loadRecords(_currentSlug);
  } catch (err) {
    alert(`Delete failed: ${err}`);
  }
}

// ── edit record ───────────────────────────────────────────────────────────────

function _onEdit(username, week) {
  const rec = _records.find((r) => r.username === username && r.week === week);
  if (!rec) return;

  const formDetails = document.getElementById('dau-form-details');
  if (formDetails) formDetails.open = true;

  const summaryEl = document.getElementById('dau-form-summary');
  if (summaryEl) summaryEl.textContent = 'Edit Record';

  _populateRecordWeekDropdown(rec.week || '');
  document.getElementById('dau-rec-username').value      = rec.username || '';
  document.getElementById('dau-rec-role').value          = rec.role || '';
  document.getElementById('dau-rec-usage').value         = rec.usage || '';
  document.getElementById('dau-rec-editing-key').value   = `${username}||${week}`;

  const cancelBtn = document.getElementById('btn-dau-cancel-edit');
  if (cancelBtn) cancelBtn.style.display = '';

  // Scroll form into view
  formDetails?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function _resetForm() {
  _populateRecordWeekDropdown(); // resets to current week
  ['dau-rec-username'].forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.value = '';
  });
  ['dau-rec-role', 'dau-rec-usage'].forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.value = '';
  });
  const keyEl = document.getElementById('dau-rec-editing-key');
  if (keyEl) keyEl.value = '';

  const summaryEl = document.getElementById('dau-form-summary');
  if (summaryEl) summaryEl.textContent = 'Add Record';

  const cancelBtn = document.getElementById('btn-dau-cancel-edit');
  if (cancelBtn) cancelBtn.style.display = 'none';

  _setRecordError('');
}

// ── init ──────────────────────────────────────────────────────────────────────

export function initDau() {
  const errNoFilter   = document.getElementById('err-dau-no-filter');
  const filterSelect  = document.getElementById('dau-filter-select');
  const btnLoad       = document.getElementById('btn-dau-load');
  const btnImport     = document.getElementById('btn-dau-import');
  const importFileEl  = document.getElementById('dau-import-file');
  const btnSaveRecord = document.getElementById('btn-dau-save-record');
  const btnCancelEdit = document.getElementById('btn-dau-cancel-edit');

  if (!filterSelect) return;

  _populateRecordWeekDropdown();

  // Populate dropdowns when the DAU tab is activated (lazy — avoids extra API calls on load)
  const tabBtn = document.getElementById('tab-dau');
  if (tabBtn) {
    tabBtn.addEventListener('click', () => {
      _populateFilterSelect();
      _populateImportWeekDropdown();
      _populateRecordWeekDropdown();
    });
  }

  // Hide "no filter" error on selection change
  if (filterSelect && errNoFilter) {
    filterSelect.addEventListener('change', () => {
      errNoFilter.classList.remove('visible');
    });
  }

  // Load records button
  if (btnLoad) {
    btnLoad.addEventListener('click', async () => {
      const slug = filterSelect?.value || '';
      if (!slug) {
        errNoFilter?.classList.add('visible');
        return;
      }
      errNoFilter?.classList.remove('visible');
      _currentSlug = slug;
      await _loadRoster(slug);
      await _loadRecords(slug);
    });
  }

  // Import Excel button
  if (btnImport) {
    btnImport.addEventListener('click', async () => {
      const slug = filterSelect?.value || '';
      if (!slug) { errNoFilter?.classList.add('visible'); return; }
      errNoFilter?.classList.remove('visible');
      _currentSlug = slug;

      const file = importFileEl?.files?.[0];
      if (!file) { _setStatus('Please select an .xlsx file first.', true); return; }
      _setStatus('');
      await _importExcel(slug, file);
    });
  }

  // Save record button
  if (btnSaveRecord) {
    btnSaveRecord.addEventListener('click', async () => {
      const slug = filterSelect?.value || _currentSlug;
      if (!slug) { errNoFilter?.classList.add('visible'); return; }
      errNoFilter?.classList.remove('visible');
      _currentSlug = slug;
      await _saveRecord(slug);
    });
  }

  // Cancel edit button
  if (btnCancelEdit) {
    btnCancelEdit.addEventListener('click', () => _resetForm());
  }

  // Record filter controls
  ['dau-filter-week', 'dau-filter-role'].forEach((id) => {
    document.getElementById(id)?.addEventListener('change', () => _renderTable(_applyFilters()));
  });
  document.getElementById('dau-filter-name')
    ?.addEventListener('input', () => _renderTable(_applyFilters()));
  document.getElementById('btn-dau-clear-filters')
    ?.addEventListener('click', () => {
      _resetFilters();
      _renderTable(_records);
    });

  // Page-size selector
  document.getElementById('dau-page-size')
    ?.addEventListener('change', () => _renderTable(_applyFilters()));

  // Roster add/update button
  document.getElementById('btn-dau-add-roster')
    ?.addEventListener('click', () => _addRosterEntry());

  // Auto-fill role from roster when username is entered (new records only)
  document.getElementById('dau-rec-username')?.addEventListener('blur', () => {
    const username = document.getElementById('dau-rec-username')?.value.trim() || '';
    const editingKey = document.getElementById('dau-rec-editing-key')?.value || '';
    if (!editingKey && username && _roster[username]) {
      const roleEl = document.getElementById('dau-rec-role');
      if (roleEl && !roleEl.value) roleEl.value = _roster[username];
    }
  });
}

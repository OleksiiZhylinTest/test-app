import { IS_SERVED, STORE_KEYS, FIELD_DEFAULTS } from './config.js';
import { store } from './store.js';
import { getConfig } from './api.js';
import { state, updateBadgeFromSaved, updateSaveBtn } from './connection.js';
import { loadSchemas } from './schema.js';
import { loadReports } from './reports.js';
import { loadFilters } from './filters.js';
import { loadCertStatus } from './cert.js';

export async function restoreValues(activateTab) {
  const jiraUrlInput   = document.getElementById('jira-url');
  const jiraEmailInput = document.getElementById('jira-email');
  const jiraTokenInput = document.getElementById('jira-token');

  // 1. Restore from localStorage first
  jiraUrlInput.value   = store.get(STORE_KEYS.JIRA_URL);
  jiraEmailInput.value = store.get(STORE_KEYS.JIRA_EMAIL);
  jiraTokenInput.value = store.get(STORE_KEYS.JIRA_API_TOKEN);

  document.getElementById('jira-board-id').value             = store.get(STORE_KEYS.JIRA_BOARD_ID);
  document.getElementById('filter-id').value                 = store.get(STORE_KEYS.JIRA_FILTER_ID);
  document.getElementById('sprint-count').value              = store.get(STORE_KEYS.JIRA_SPRINT_COUNT);
  document.getElementById('jira-project').value              = store.get(STORE_KEYS.JIRA_PROJECT);
  document.getElementById('jira-team-id').value              = store.get(STORE_KEYS.JIRA_TEAM_ID);
  document.getElementById('jira-issue-types').value          = store.get(STORE_KEYS.JIRA_ISSUE_TYPES);
  document.getElementById('jira-include-active-sprint').value  = store.get(STORE_KEYS.JIRA_INCLUDE_ACTIVE_SPRINT);
  document.getElementById('jira-filter-page-size').value     = store.get(STORE_KEYS.JIRA_FILTER_PAGE_SIZE);
  updateBadgeFromSaved();

  // 2. Overlay with server-side config read from .env on disk
  const _apiBase = IS_SERVED ? '' : 'http://localhost:8080';
  try {
    const data = await getConfig(_apiBase);
    const cfg  = data.config || {};

    if (cfg.JIRA_URL)   { const _url = cfg.JIRA_URL.trim().replace(/\/+$/, ''); jiraUrlInput.value = _url; store.set(STORE_KEYS.JIRA_URL, _url); }
    if (cfg.JIRA_EMAIL) { jiraEmailInput.value = cfg.JIRA_EMAIL; store.set(STORE_KEYS.JIRA_EMAIL, cfg.JIRA_EMAIL); }

    if (cfg.JIRA_API_TOKEN === '***') {
      state.hasServerToken = true;
      if (!jiraTokenInput.value) {
        jiraTokenInput.placeholder = 'Token saved — enter a new one to replace it';
      }
    }

    if (cfg.JIRA_BOARD_ID)            { document.getElementById('jira-board-id').value            = cfg.JIRA_BOARD_ID;            store.set(STORE_KEYS.JIRA_BOARD_ID,            cfg.JIRA_BOARD_ID); }
    if (cfg.JIRA_FILTER_ID)           { document.getElementById('filter-id').value                = cfg.JIRA_FILTER_ID;           store.set(STORE_KEYS.JIRA_FILTER_ID,           cfg.JIRA_FILTER_ID); }
    if (cfg.JIRA_SPRINT_COUNT)        { document.getElementById('sprint-count').value              = cfg.JIRA_SPRINT_COUNT;        store.set(STORE_KEYS.JIRA_SPRINT_COUNT,        cfg.JIRA_SPRINT_COUNT); }
    if (cfg.JIRA_PROJECT)             { document.getElementById('jira-project').value              = cfg.JIRA_PROJECT;             store.set(STORE_KEYS.JIRA_PROJECT,             cfg.JIRA_PROJECT); }
    if (cfg.JIRA_TEAM_ID)             { document.getElementById('jira-team-id').value              = cfg.JIRA_TEAM_ID;             store.set(STORE_KEYS.JIRA_TEAM_ID,             cfg.JIRA_TEAM_ID); }
    if (cfg.JIRA_ISSUE_TYPES)         { document.getElementById('jira-issue-types').value          = cfg.JIRA_ISSUE_TYPES;         store.set(STORE_KEYS.JIRA_ISSUE_TYPES,         cfg.JIRA_ISSUE_TYPES); }
    if (cfg.JIRA_INCLUDE_ACTIVE_SPRINT) { document.getElementById('jira-include-active-sprint').value  = cfg.JIRA_INCLUDE_ACTIVE_SPRINT; store.set(STORE_KEYS.JIRA_INCLUDE_ACTIVE_SPRINT, cfg.JIRA_INCLUDE_ACTIVE_SPRINT); }
    if (cfg.JIRA_FILTER_PAGE_SIZE)    { document.getElementById('jira-filter-page-size').value     = cfg.JIRA_FILTER_PAGE_SIZE;    store.set(STORE_KEYS.JIRA_FILTER_PAGE_SIZE,    cfg.JIRA_FILTER_PAGE_SIZE); }

    updateBadgeFromSaved();

    if (!data.configured && !store.get(STORE_KEYS.JIRA_URL)) {
      document.getElementById('first-run-banner').hidden = false;
      activateTab(document.getElementById('tab-connection'));
    }
  } catch (err) {
    console.warn('restoreValues: could not fetch /api/config —', err);
  }

  // 3. Apply defaults for fields that are still empty
  const fieldIds = {
    JIRA_SPRINT_COUNT:        'sprint-count',
    JIRA_INCLUDE_ACTIVE_SPRINT: 'jira-include-active-sprint',
    JIRA_FILTER_PAGE_SIZE:    'jira-filter-page-size',
  };
  for (const [key, elId] of Object.entries(fieldIds)) {
    const el = document.getElementById(elId);
    if (el && !el.value && FIELD_DEFAULTS[key]) {
      el.value = FIELD_DEFAULTS[key];
    }
  }

  const filterNameEl = document.getElementById('filter-name');
  if (filterNameEl && !filterNameEl.value) {
    const today = new Date().toISOString().slice(0, 10);
    filterNameEl.value = `Default_Jira_Filter_${today}`;
  }

  updateSaveBtn();

  loadSchemas();
  loadReports();
  loadFilters();
  loadCertStatus();
}

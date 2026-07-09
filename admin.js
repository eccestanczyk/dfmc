/* ============================================================
   HERUMON TOWER — Admin Mode
   ?admin=1 enables admin UI (sticky via localStorage)
   ?admin=0 disables it
   ============================================================ */

(function(){
  const p = new URLSearchParams(location.search);
  if (p.get('admin') === '1') localStorage.setItem('dfmc_admin', '1');
  if (p.get('admin') === '0') localStorage.removeItem('dfmc_admin');
  if (localStorage.getItem('dfmc_admin') === '1') {
    document.documentElement.classList.add('admin-mode');
  }
})();

/* ---------- Backlog storage ---------- */
const Backlog = {
  _key: 'dfmc_backlog',

  getAll() {
    try { return JSON.parse(localStorage.getItem(this._key)) || {}; } catch { return {}; }
  },

  get(id) {
    return (this.getAll()[id] || {}).actions || [];
  },

  getComment(id) {
    return (this.getAll()[id] || {}).comment || '';
  },

  set(id, name, actions, comment) {
    const all = this.getAll();
    if (actions.length === 0 && !comment) { delete all[id]; }
    else { all[id] = { name, actions, comment: comment || '', ts: Date.now() }; }
    localStorage.setItem(this._key, JSON.stringify(all));
  },

  toggle(id, name, action) {
    const all = this.getAll();
    const entry = all[id] || { actions: [], comment: '' };
    const actions = entry.actions || [];
    const idx = actions.indexOf(action);
    if (idx >= 0) actions.splice(idx, 1);
    else actions.push(action);
    this.set(id, name, actions, entry.comment);
    return actions;
  },

  setComment(id, name, comment) {
    const all = this.getAll();
    const entry = all[id] || { actions: [], comment: '' };
    this.set(id, name, entry.actions || [], comment);
  },

  count() {
    const all = this.getAll();
    let creatures = 0, actions = 0;
    for (const id in all) {
      const e = all[id];
      if ((e.actions && e.actions.length) || e.comment) {
        creatures++;
        actions += (e.actions || []).length;
      }
    }
    return { creatures, actions };
  },

  clear() {
    localStorage.removeItem(this._key);
  },

  formatForClipboard() {
    const all = this.getAll();
    const ids = Object.keys(all).sort();
    if (!ids.length) return 'BACKLOG EMPTY — no pending actions.';

    const { creatures, actions } = this.count();
    let out = `CREATURE BACKLOG (${creatures} creature${creatures!==1?'s':''}, ${actions} action${actions!==1?'s':''})\n`;
    out += '—'.repeat(40) + '\n';

    const ACTION_LABELS = {
      approve_art: 'Approve art',
      art_revision: 'Art revision needed',
      regenerate: 'Regenerate and overwrite',
      generate_option: 'Generate new option',
      remove_option: 'Remove an option',
      generate_crop: 'Generate new crop',
      framing_issue: 'Framing issue',
      flip_image: 'Flip image (face left)',
      mark_needs_reimport: 'Flag for reimport (altered since import)',
      mark_synced: 'Mark imported / synced to game',
      approve_option_A: 'Approve A (original chroma)',
      approve_option_B: 'Approve B (Sylph crop)',
      approve_option_C: 'Approve C (isnet crop)',
      delete_option_A: 'Delete A (original chroma)',
      delete_option_B: 'Delete B (Sylph crop)',
      delete_option_C: 'Delete C (isnet crop)'
    };

    for (const id of ids) {
      const entry = all[id];
      if (!(entry.actions && entry.actions.length) && !entry.comment) continue;
      const labels = (entry.actions || []).map(a => ACTION_LABELS[a] || a);
      out += `${id} ${entry.name}`;
      if (labels.length) out += `: ${labels.join(', ')}`;
      out += '\n';
      if (entry.comment) out += `  Comment: ${entry.comment}\n`;
    }
    return out.trim();
  },

  async copyToClipboard() {
    const text = this.formatForClipboard();
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch {
      const ta = document.createElement('textarea');
      ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
      document.body.appendChild(ta); ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      return true;
    }
  }
};

/* ---------- Inject backlog buttons into topbar ---------- */
(function(){
  if (!document.documentElement.classList.contains('admin-mode')) return;

  const topbar = document.querySelector('.topbar');
  if (!topbar) return;

  // Container for backlog buttons
  const wrap = document.createElement('div');
  wrap.style.cssText = 'display:flex;gap:6px;align-items:center;flex-shrink:0;';

  const btnStyle = 'font-family:Cinzel,serif;font-size:11px;font-weight:600;letter-spacing:0.04em;padding:5px 12px;border:1px solid #5c462c;background:#271e15;color:#cfa650;cursor:pointer;text-transform:uppercase;transition:all 0.14s;white-space:nowrap;';

  // Copy button
  const copyBtn = document.createElement('button');
  copyBtn.id = 'copy-backlog-btn';
  copyBtn.style.cssText = btnStyle + 'display:none;';
  copyBtn.onmouseenter = function(){ this.style.borderColor='#dd5646'; this.style.color='#dd5646'; };
  copyBtn.onmouseleave = function(){ this.style.borderColor='#5c462c'; this.style.color='#cfa650'; };

  // Clear button
  const clearBtn = document.createElement('button');
  clearBtn.id = 'clear-backlog-btn';
  clearBtn.textContent = '✕ CLEAR';
  clearBtn.style.cssText = btnStyle + 'display:none;';
  clearBtn.onmouseenter = function(){ this.style.borderColor='#dd5646'; this.style.color='#dd5646'; };
  clearBtn.onmouseleave = function(){ this.style.borderColor='#5c462c'; this.style.color='#cfa650'; };

  function updateBtns() {
    const { creatures, actions } = Backlog.count();
    if (actions > 0 || creatures > 0) {
      copyBtn.textContent = '📋 BACKLOG (' + (actions || creatures) + ')';
      copyBtn.style.display = 'block';
      clearBtn.style.display = 'block';
    } else {
      copyBtn.style.display = 'none';
      clearBtn.style.display = 'none';
    }
  }

  copyBtn.onclick = async function() {
    const ok = await Backlog.copyToClipboard();
    if (ok) {
      const orig = copyBtn.textContent;
      copyBtn.textContent = '✓ COPIED';
      copyBtn.style.color = '#4a7a44';
      copyBtn.style.borderColor = '#4a7a44';
      setTimeout(() => { copyBtn.textContent = orig; copyBtn.style.color = '#cfa650'; copyBtn.style.borderColor = '#5c462c'; }, 1500);
    }
  };

  clearBtn.onclick = function() {
    if (confirm('Clear entire backlog?')) {
      Backlog.clear();
      updateBtns();
      // Re-render creature dropdown if on creature page
      if (window._renderAdminMenu) window._renderAdminMenu();
    }
  };

  wrap.appendChild(copyBtn);
  wrap.appendChild(clearBtn);
  topbar.appendChild(wrap);
  updateBtns();

  window.addEventListener('storage', updateBtns);
  window._updateBacklogBtn = updateBtns;
})();

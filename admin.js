/* ============================================================
   TOWER CRAWLER — Admin Mode
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

  set(id, name, actions) {
    const all = this.getAll();
    if (actions.length === 0) { delete all[id]; }
    else { all[id] = { name, actions, ts: Date.now() }; }
    localStorage.setItem(this._key, JSON.stringify(all));
  },

  toggle(id, name, action) {
    const actions = this.get(id);
    const idx = actions.indexOf(action);
    if (idx >= 0) actions.splice(idx, 1);
    else actions.push(action);
    this.set(id, name, actions);
    return actions;
  },

  count() {
    const all = this.getAll();
    let creatures = 0, actions = 0;
    for (const id in all) {
      if (all[id].actions && all[id].actions.length) {
        creatures++;
        actions += all[id].actions.length;
      }
    }
    return { creatures, actions };
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
      framing_issue: 'Framing issue'
    };

    for (const id of ids) {
      const entry = all[id];
      if (!entry.actions || !entry.actions.length) continue;
      const labels = entry.actions.map(a => ACTION_LABELS[a] || a);
      out += `${id} ${entry.name}: ${labels.join(', ')}\n`;
    }
    return out.trim();
  },

  async copyToClipboard() {
    const text = this.formatForClipboard();
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch {
      // Fallback
      const ta = document.createElement('textarea');
      ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
      document.body.appendChild(ta); ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      return true;
    }
  }
};

/* ---------- Inject copy-backlog button into topbar ---------- */
(function(){
  if (!document.documentElement.classList.contains('admin-mode')) return;

  const topbar = document.querySelector('.topbar');
  if (!topbar) return;

  const btn = document.createElement('button');
  btn.id = 'copy-backlog-btn';
  btn.style.cssText = 'font-family:Cinzel,serif;font-size:11px;font-weight:600;letter-spacing:0.04em;padding:5px 12px;border:1px solid #5c462c;background:#271e15;color:#cfa650;cursor:pointer;margin-left:auto;text-transform:uppercase;transition:all 0.14s;display:none;';
  btn.onmouseenter = function(){ this.style.borderColor='#dd5646'; this.style.color='#dd5646'; };
  btn.onmouseleave = function(){ this.style.borderColor='#5c462c'; this.style.color='#cfa650'; };

  function updateBtn() {
    const { creatures, actions } = Backlog.count();
    if (actions > 0) {
      btn.textContent = `📋 BACKLOG (${actions})`;
      btn.style.display = 'block';
    } else {
      btn.style.display = 'none';
    }
  }

  btn.onclick = async function() {
    const ok = await Backlog.copyToClipboard();
    if (ok) {
      const orig = btn.textContent;
      btn.textContent = '✓ COPIED';
      btn.style.color = '#4a7a44';
      btn.style.borderColor = '#4a7a44';
      setTimeout(() => { btn.textContent = orig; btn.style.color = '#cfa650'; btn.style.borderColor = '#5c462c'; }, 1500);
    }
  };

  topbar.appendChild(btn);
  updateBtn();

  // Listen for backlog changes from creature page
  window.addEventListener('storage', updateBtn);
  window._updateBacklogBtn = updateBtn;
})();

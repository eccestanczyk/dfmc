import os
"""ghlib.py — DFMC GitHub helpers (rebuilt per PIPELINE.md).
GitHub via requests. get_file with >1MB blob fallback, commit_multi atomic, purge_cdn."""
import base64, json, requests

REPO = "eccestanczyk/dfmc"
PAT = os.environ.get("GH_TOKEN") or open(os.path.expanduser("~/.ghtoken")).read().strip()
API  = f"https://api.github.com/repos/{REPO}"
H    = {"Authorization": f"token {PAT}", "Accept": "application/vnd.github+json"}


def _get(url, **kw):
    r = requests.get(url, headers=H, **kw); r.raise_for_status(); return r


def head_sha(branch="main"):
    return _get(f"{API}/git/refs/heads/{branch}").json()["object"]["sha"]


def get_file(path, ref="main"):
    """Return (bytes, sha). Falls back to blobs API for files >1MB (Contents API
    silently returns empty content over 1MB)."""
    r = requests.get(f"{API}/contents/{path}", headers=H, params={"ref": ref})
    if r.status_code == 404:
        return None, None
    r.raise_for_status()
    j = r.json()
    content = j.get("content", "")
    if content:  # small file, inline base64
        return base64.b64decode(content), j["sha"]
    # >1MB: content empty -> fetch via blobs API using the sha
    sha = j["sha"]
    blob = _get(f"{API}/git/blobs/{sha}").json()
    return base64.b64decode(blob["content"]), sha


def get_sha(path, ref="main"):
    r = requests.get(f"{API}/contents/{path}", headers=H, params={"ref": ref})
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json()["sha"]


def commit_multi(changes, message, branch="main"):
    """Atomic multi-file commit via git data API.
    changes: list of {"path": str, "data": bytes|str|None}. data=None => delete.
    create blobs -> build tree -> create commit -> patch ref.
    NOTE: deletions 422 if path absent in base tree; confirm existence first."""
    base_sha = head_sha(branch)
    base_commit = _get(f"{API}/git/commits/{base_sha}").json()
    base_tree = base_commit["tree"]["sha"]

    tree = []
    for c in changes:
        path, data = c["path"], c["data"]
        if data is None:
            tree.append({"path": path, "mode": "100644", "type": "blob", "sha": None})
            continue
        if isinstance(data, str):
            data = data.encode()
        b = requests.post(f"{API}/git/blobs", headers=H, json={
            "content": base64.b64encode(data).decode(), "encoding": "base64"})
        b.raise_for_status()
        tree.append({"path": path, "mode": "100644", "type": "blob", "sha": b.json()["sha"]})

    t = requests.post(f"{API}/git/trees", headers=H,
                      json={"base_tree": base_tree, "tree": tree})
    t.raise_for_status(); new_tree = t.json()["sha"]

    cm = requests.post(f"{API}/git/commits", headers=H,
                       json={"message": message, "tree": new_tree, "parents": [base_sha]})
    cm.raise_for_status(); new_commit = cm.json()["sha"]

    ref = requests.patch(f"{API}/git/refs/heads/{branch}", headers=H,
                         json={"sha": new_commit, "force": False})
    if ref.status_code == 422:  # REBASE-RETRY: HEAD moved between base fetch and patch
        import time as _t
        for attempt in range(5):
            _t.sleep(2 + attempt)
            base_sha = head_sha(branch)
            base_commit = _get(f"{API}/git/commits/{base_sha}").json()
            t2 = requests.post(f"{API}/git/trees", headers=H,
                               json={"base_tree": base_commit["tree"]["sha"], "tree": tree})
            t2.raise_for_status()
            cm2 = requests.post(f"{API}/git/commits", headers=H,
                                json={"message": message, "tree": t2.json()["sha"],
                                      "parents": [base_sha]})
            cm2.raise_for_status(); new_commit = cm2.json()["sha"]
            ref = requests.patch(f"{API}/git/refs/heads/{branch}", headers=H,
                                 json={"sha": new_commit, "force": False})
            if ref.status_code == 200:
                break
    ref.raise_for_status()
    return new_commit


def purge_cdn(paths):
    """Purge jsDelivr CDN for touched image paths."""
    if isinstance(paths, str):
        paths = [paths]
    out = {}
    for p in paths:
        url = f"https://purge.jsdelivr.net/gh/{REPO}@main/{p}"
        try:
            out[p] = requests.get(url, timeout=20).status_code
        except Exception as e:
            out[p] = str(e)
    return out


def tree_paths(ref="main"):
    """Return set of all blob paths in HEAD tree (ground-truth verify)."""
    sha = head_sha(ref) if ref == "main" else ref
    t = _get(f"{API}/git/trees/{sha}", params={"recursive": "1"}).json()
    return {e["path"] for e in t["tree"] if e["type"] == "blob"}


def csv_update(path, updates, key="ID", message="csv row update", branch="main", max_retries=6):
    """Row-level CSV update with clobber-proof rebase loop.
    updates: {key_value: {col: val}}. Re-reads the CSV at commit time, applies row
    patches onto the FRESH copy, commits with parent=exact HEAD read; on ref-race
    (422 non-fast-forward) refetches and reapplies. Whole-file rewrites from stale
    reads are what clobber concurrent sessions' row edits — never do that again."""
    import csv as _csv, io as _io, time as _time
    for attempt in range(max_retries):
        base_sha = head_sha(branch)
        base_commit = _get(f"{API}/git/commits/{base_sha}").json()
        raw, _ = get_file(path, ref=base_sha)
        rows = list(_csv.DictReader(_io.StringIO(raw.decode("utf-8"))))
        cols = list(rows[0].keys())
        # ensure any new columns exist
        for kv in updates.values():
            for col in kv:
                if col not in cols:
                    cols.append(col)
                    for r in rows: r.setdefault(col, "")
        hit = 0
        for r in rows:
            if r.get(key) in updates:
                r.update(updates[r[key]]); hit += 1
        if hit != len(updates):
            raise RuntimeError(f"csv_update: matched {hit}/{len(updates)} keys in {path}")
        buf = _io.StringIO()
        w = _csv.DictWriter(buf, fieldnames=cols, lineterminator="\n")
        w.writeheader(); w.writerows(rows)
        b = requests.post(f"{API}/git/blobs", headers=H, json={
            "content": base64.b64encode(buf.getvalue().encode()).decode(), "encoding": "base64"})
        b.raise_for_status()
        t = requests.post(f"{API}/git/trees", headers=H, json={
            "base_tree": base_commit["tree"]["sha"],
            "tree": [{"path": path, "mode": "100644", "type": "blob", "sha": b.json()["sha"]}]})
        t.raise_for_status()
        cm = requests.post(f"{API}/git/commits", headers=H, json={
            "message": message, "tree": t.json()["sha"], "parents": [base_sha]})
        cm.raise_for_status()
        ref = requests.patch(f"{API}/git/refs/heads/{branch}", headers=H,
                             json={"sha": cm.json()["sha"], "force": False})
        if ref.status_code == 200:
            return cm.json()["sha"]
        if ref.status_code == 422:      # HEAD moved between read and write -> rebase
            _time.sleep(2 + attempt); continue
        ref.raise_for_status()
    raise RuntimeError("csv_update: ref race persisted after retries")

// LAUNCH STEP: run in a wp-admin tab on the target site AFTER the 48 case pages are published.
// Sets the 14 "Cases (new design)" Query Builder queries to published-only (they include drafts for staging preview).
(async () => {
  const nonce = await fetch('/wp-admin/admin-ajax.php?action=rest-nonce').then(r => r.text());
  const H = { 'X-WP-Nonce': nonce, 'Content-Type': 'application/json' };
  const ids = [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24];
  const out = [];
  for (const id of ids) {
    const g = await fetch('/wp-json/jet-engine/v2/get-query/' + id, { headers: H }).then(r => r.json());
    const d = g.data;
    if (!d || !String(d.name).startsWith('Cases (new design)')) { out.push([id, 'skipped', d && d.name]); continue; }
    d.posts.post_status = ['publish'];
    const r = await fetch('/wp-json/jet-engine/v2/edit-query/' + id, { method: 'POST', headers: H, body: JSON.stringify({ general_settings: d, meta_fields: [] }) }).then(r => r.json());
    out.push([id, d.name, r.success]);
  }
  console.table(out);
  return out;
})();

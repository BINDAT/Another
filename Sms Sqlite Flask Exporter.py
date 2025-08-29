#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sms_sqlite_flask_exporter.py

1) Importer (streaming) d'un gros XML SMS Backup -> SQLite + fichiers médias
2) Mini-application Flask (interface web simple) pour rechercher et parcourir les conversations

Usage:
  # installer dépendances (si besoin)
  python3 -m pip install --user flask

  # Importer
  python3 sms_sqlite_flask_exporter.py --import --xml /chemin/backup.xml --out ./export --split-by-year

  # Lancer le serveur web (après import)
  python3 sms_sqlite_flask_exporter.py --serve --db ./export/messages.db --media ./export/media

Notes:
- Conçu pour fonctionner en streaming (xml.etree.ElementTree.iterparse)
- Crée une table 'messages' et 'media' et une FTS5 'messages_fts' si SQLite le supporte
- Le serveur Flask est volontairement minimaliste et utilise des templates embarqués
"""

import os
import sys
import re
import time
import base64
import argparse
import sqlite3
import html
import xml.etree.ElementTree as ET
from datetime import datetime

# Flask import deferred (import only when --serve)

# -------------------- Utils --------------------

def ensure_dir(p):
    os.makedirs(p, exist_ok=True)


def ms_to_ts(ms):
    try:
        s = int(ms) / 1000.0
    except Exception:
        return None
    return datetime.fromtimestamp(s)


def safe_filename(name: str) -> str:
    name = (name or '')
    name = name.strip()
    name = name.replace('/', '_').replace('\\', '_')
    name = re.sub(r"[^\w\-. ]", '_', name)
    name = re.sub(r"\s+", ' ', name)
    return name[:200]


def guess_ext(ct: str, suggested: str = None):
    if suggested:
        _, ext = os.path.splitext(suggested)
        if ext:
            return ext
    if not ct:
        return '.bin'
    mapping = {
        'image/jpeg': '.jpg', 'image/jpg': '.jpg', 'image/png': '.png', 'image/gif': '.gif', 'image/webp': '.webp',
        'audio/mpeg': '.mp3', 'audio/mp3': '.mp3', 'audio/ogg': '.ogg', 'audio/amr': '.amr',
        'video/mp4': '.mp4', 'video/3gpp': '.3gp',
        'text/plain': '.txt', 'application/pdf': '.pdf'
    }
    return mapping.get(ct.lower(), '.' + ct.split('/')[-1])

# -------------------- Importer --------------------

def import_xml_to_sqlite(xml_path, out_dir, split_by_year=False, limit=0):
    """Lit le XML en streaming et alimente SQLite + sauvegarde médias dans out_dir/media"""
    ensure_dir(out_dir)
    media_dir = os.path.join(out_dir, 'media')
    ensure_dir(media_dir)
    db_path = os.path.join(out_dir, 'messages.db')

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('PRAGMA journal_mode=WAL')
    cur.execute('PRAGMA synchronous=NORMAL')

    # Tables
    cur.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        typ TEXT,
        address TEXT,
        contact_name TEXT,
        date_ms INTEGER,
        date_iso TEXT,
        direction TEXT,
        body TEXT
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS media (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message_id INTEGER,
        filename TEXT,
        content_type TEXT,
        orig_name TEXT,
        FOREIGN KEY(message_id) REFERENCES messages(id)
    )
    ''')

    # FTS for fast text search (FTS5)
    try:
        cur.execute("CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(body, address, contact_name, content='messages', content_rowid='id')")
        has_fts = True
    except sqlite3.OperationalError:
        print('FTS5 non disponible, recherche texte utilisera LIKE (plus lent).')
        has_fts = False

    conn.commit()

    context = ET.iterparse(xml_path, events=('start', 'end'))
    _, root = next(context)

    total = 0
    media_counter = 0
    batch = []

    def insert_message(typ, address, contact_name, date_ms, direction, body, media_items):
        nonlocal media_counter
        cur.execute('INSERT INTO messages (typ, address, contact_name, date_ms, date_iso, direction, body) VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (typ, address, contact_name, date_ms, ms_to_ts(date_ms).isoformat() if ms_to_ts(date_ms) else None, direction, body))
        mid = cur.lastrowid
        if has_fts:
            cur.execute('INSERT INTO messages_fts(rowid, body, address, contact_name) VALUES (?, ?, ?, ?)', (mid, body or '', address or '', contact_name or ''))
        for m in media_items:
            fname, ctype, oname = m
            media_counter += 1
            ext = os.path.splitext(fname)[1] or guess_ext(ctype, oname)
            saved_name = f'media_{media_counter:09d}{ext}'
            with open(os.path.join(media_dir, saved_name), 'wb') as f:
                f.write(m[3])
            cur.execute('INSERT INTO media (message_id, filename, content_type, orig_name) VALUES (?, ?, ?, ?)',
                        (mid, saved_name, ctype, oname))
        return

    for event, elem in context:
        if event != 'end':
            continue
        tag = elem.tag.lower()

        if tag == 'sms':
            address = elem.attrib.get('address') or elem.attrib.get('address_email') or ''
            name = elem.attrib.get('contact_name') or elem.attrib.get('name') or ''
            body = elem.attrib.get('body') or ''
            date_ms = elem.attrib.get('date')
            type_ = elem.attrib.get('type')
            direction = 'in' if type_ == '1' else 'out'
            insert_message('sms', address, name, date_ms, direction, body, [])
            total += 1
            if total % 10000 == 0:
                conn.commit(); print(f'[{total}] messages importés...')

        elif tag == 'mms':
            address = elem.attrib.get('address') or elem.attrib.get('address_email') or ''
            name = elem.attrib.get('contact_name') or elem.attrib.get('name') or ''
            date_ms = elem.attrib.get('date')
            box = elem.attrib.get('msg_box') or elem.attrib.get('box') or elem.attrib.get('m_type')
            direction = 'in' if (box == '1') else 'out'
            # parts
            parts_parent = elem.find('parts')
            if parts_parent is None:
                parts = elem.findall('part')
            else:
                parts = parts_parent.findall('part')
            body_chunks = []
            media_items = []
            for part in parts:
                ct = part.attrib.get('ct') or ''
                text = part.attrib.get('text')
                data = part.attrib.get('data')
                name_attr = part.attrib.get('name') or part.attrib.get('cl')
                if ct.startswith('text') or (ct == '' and text):
                    if text:
                        body_chunks.append(text)
                    continue
                if data:
                    try:
                        blob = base64.b64decode(data, validate=False)
                    except Exception:
                        blob = base64.b64decode(data + '==')
                    # store temp name, content-type, orig name, and raw bytes
                    media_items.append((name_attr or 'part', ct, name_attr or '', blob))
                else:
                    # not inlined media
                    if name_attr:
                        body_chunks.append(f"[pièce jointe: {name_attr}]")
            body = '\n'.join(body_chunks)
            insert_message('mms', address, name, date_ms, direction, body, media_items)
            total += 1
            if total % 10000 == 0:
                conn.commit(); print(f'[{total}] messages importés...')

        # clear to free memory
        root.clear()

        if limit and total >= limit:
            break

    conn.commit()
    conn.close()
    print(f"Import terminé. {total} messages. DB: {db_path} | media dir: {media_dir}")
    return db_path, media_dir

# -------------------- Minimal Flask server --------------------

FLASK_TEMPLATES = {
    'index': '''<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SMS Archive</title>
<style>
body{font-family:system-ui,Segoe UI,Roboto,Arial;margin:0;background:#f4f7fb;color:#111}
.container{max-width:1000px;margin:2rem auto;padding:1rem}
.header{display:flex;gap:1rem;align-items:center}
.form{display:flex;gap:.5rem}
.card{background:#fff;padding:1rem;border-radius:8px;box-shadow:0 6px 18px rgba(0,0,0,0.06);}
.result{margin-top:1rem}
.msg{padding:.6rem;border-bottom:1px solid #eee}
.small{color:#666;font-size:.9rem}
.media img{max-width:240px;display:block;margin-top:.5rem}
</style>
</head><body><div class="container">
<div class="header"><h1>🔎 Rechercher dans l'archive</h1></div>
<div class="card">
<form class="form" method="get" action="/search">
<input name="q" placeholder="Mot-clé, numéro ou contact" style="flex:1;padding:.5rem;border:1px solid #ddd;border-radius:6px" value="{{q|e}}">
<button style="padding:.5rem .9rem">Rechercher</button>
</form>
</div>
{% if q is defined and q %}
<div class="result">
  <h2>Résultats pour «{{q|e}}» — {{total}} messages</h2>
  <div class="card">
  {% for m in rows %}
    <div class="msg">
      <div><strong>{{m.contact_name or m.address}}</strong> <span class="small">• {{m.date_iso}}</span></div>
      <div>{{m.body_html | safe}}</div>
      {% if m.media %}
        <div class="media">{% for mm in m.media %}<a href="/media/{{mm}}" target="_blank"><img src="/media/{{mm}}"></a>{% endfor %}</div>
      {% endif %}
    </div>
  {% endfor %}
  </div>
</div>
{% endif %}
</div></body></html>''',

    'contact': '''<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Conversation</title>
<style>
body{font-family:system-ui,Segoe UI,Roboto,Arial;margin:0;background:#f4f7fb;color:#111}
.container{max-width:900px;margin:2rem auto;padding:1rem}
.thread{background:#fff;padding:1rem;border-radius:8px;box-shadow:0 6px 18px rgba(0,0,0,0.06)}
.msg{padding:.6rem;border-bottom:1px solid #eee}
.in{background:#eef;padding:.6rem;border-radius:6px}
.out{background:#efe;padding:.6rem;border-radius:6px}
.small{color:#666;font-size:.9rem}
.media img{max-width:300px;display:block;margin-top:.5rem}
</style>
</head><body><div class="container">
<h1>Conversation: {{who}}</h1>
<div class="thread">
{% for m in rows %}
  <div class="msg {{'out' if m.direction=='out' else 'in'}}">
    <div class="small">{{m.date_iso}}</div>
    <div>{{m.body_html | safe}}</div>
    {% if m.media %}
      <div class="media">{% for mm in m.media %}<a href="/media/{{mm}}" target="_blank"><img src="/media/{{mm}}"></a>{% endfor %}</div>
    {% endif %}
  </div>
{% endfor %}
</div>
</div></body></html>'''
}


def run_server(db_path, media_dir, host='127.0.0.1', port=5000):
    from flask import Flask, request, render_template_string, send_from_directory, abort
    app = Flask(__name__)

    def make_body_html(b):
        if not b:
            return ''
        # escape then convert urls
        t = html.escape(b)
        t = re.sub(r'(https?://[^\s<]+)', r'<a href="\1" target="_blank">\1</a>', t)
        return t.replace('\n', '<br>')

    @app.route('/')
    def index():
        return render_template_string(FLASK_TEMPLATES['index'], q='')

    @app.route('/search')
    def search():
        q = request.args.get('q', '').strip()
        rows = []
        total = 0
        if q:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            # si FTS dispo, utiliser MATCH
            try:
                c.execute("SELECT rowid, * FROM messages_fts WHERE messages_fts MATCH ? LIMIT 200", (q,))
                ids = [r[0] for r in c.fetchall()]
            except Exception:
                # fallback LIKE
                likeq = f'%{q}%'
                c.execute("SELECT id FROM messages WHERE body LIKE ? OR address LIKE ? OR contact_name LIKE ? LIMIT 200", (likeq, likeq, likeq))
                ids = [r[0] for r in c.fetchall()]
            if ids:
                placeholders = ','.join('?' for _ in ids)
                c.execute(f"SELECT * FROM messages WHERE id IN ({placeholders}) ORDER BY date_ms DESC", ids)
                for r in c.fetchall():
                    rr = dict(r)
                    # fetch media
                    c.execute('SELECT filename FROM media WHERE message_id=?', (rr['id'],))
                    media = [m[0] for m in c.fetchall()]
                    rr['media'] = media
                    rr['body_html'] = make_body_html(rr.get('body') or '')
                    rows.append(rr)
            total = len(rows)
            conn.close()
        return render_template_string(FLASK_TEMPLATES['index'], q=q, rows=rows, total=total)

    @app.route('/contact/<int:cid>')
    def contact(cid):
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT * FROM messages WHERE id=? ORDER BY date_ms', (cid,))
        rows = []
        for r in c.fetchall():
            rr = dict(r)
            c.execute('SELECT filename FROM media WHERE message_id=?', (rr['id'],))
            rr['media'] = [m[0] for m in c.fetchall()]
            rr['body_html'] = make_body_html(rr.get('body') or '')
            rows.append(rr)
        conn.close()
        if not rows:
            abort(404)
        # who = contact_name or address
        who = rows[0].get('contact_name') or rows[0].get('address')
        return render_template_string(FLASK_TEMPLATES['contact'], rows=rows, who=who)

    @app.route('/media/<path:filename>')
    def media(filename):
        # serve media files directly
        safe = os.path.normpath(filename)
        if '..' in safe or safe.startswith('/'):
            abort(404)
        return send_from_directory(media_dir, filename)

    print(f"Serving on http://{host}:{port} (DB: {db_path}, media: {media_dir})")
    app.run(host=host, port=port)

# -------------------- CLI --------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xml')
    ap.add_argument('--out', default='./export')
    ap.add_argument('--split-by-year', action='store_true')
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--import', dest='do_import', action='store_true')
    ap.add_argument('--serve', dest='do_serve', action='store_true')
    ap.add_argument('--db', default=None)
    ap.add_argument('--media', default=None)
    ap.add_argument('--host', default='127.0.0.1')
    ap.add_argument('--port', type=int, default=5000)
    args = ap.parse_args()

    if args.do_import:
        if not args.xml:
            print('Erreur: --xml requis pour --import')
            sys.exit(1)
        db_path, media_dir = import_xml_to_sqlite(args.xml, args.out, split_by_year=args.split_by_year, limit=args.limit)
        print('Import OK. DB at', db_path)
        sys.exit(0)

    if args.do_serve:
        dbp = args.db or os.path.join(args.out, 'messages.db')
        med = args.media or os.path.join(args.out, 'media')
        if not os.path.exists(dbp):
            print('DB introuvable:', dbp); sys.exit(1)
        if not os.path.exists(med):
            print('Media dir introuvable:', med); sys.exit(1)
        run_server(dbp, med, host=args.host, port=args.port)
        sys.exit(0)

    ap.print_help()

if __name__ == '__main__':
    main()

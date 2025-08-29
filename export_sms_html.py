#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import csv
import base64
import html
import time
import argparse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

# ----------------------------
# Utils
# ----------------------------

def safe_filename(name: str) -> str:
    name = name.strip()
    name = name.replace("/", "_").replace("\\", "_")
    name = re.sub(r"[^\w\-. ]", "_", name)
    name = re.sub(r"\s+", " ", name)
    return name[:200] if len(name) > 200 else name

def ms_to_local_str(ms: str) -> str:
    # SMS Backup & Restore stocke en ms depuis epoch
    try:
        ms = int(ms)
    except (TypeError, ValueError):
        return ""
    # on convertit en heure locale de la machine
    s = ms / 1000.0
    loc = time.localtime(s)
    return time.strftime("%Y-%m-%d %H:%M:%S", loc)

def contact_key(address: str, name: str) -> str:
    # Clé stable : "Nom (numéro)" si les deux existent ; sinon l'un ou l'autre
    addr = (address or "").strip()
    nam  = (name or "").strip()
    if nam and addr:
        return f"{nam} ({addr})"
    return nam or addr or "Inconnu"

def ensure_dir(p):
    os.makedirs(p, exist_ok=True)

def write_if_new(path: str, content: str):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

def append(path: str, content: str):
    with open(path, "a", encoding="utf-8") as f:
        f.write(content)

def guess_part_filename(idx: int, ct: str, suggested: str = None):
    ext_map = {
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/png": ".png",
        "image/gif": ".gif",
        "image/webp": ".webp",
        "audio/mpeg": ".mp3",
        "audio/mp3": ".mp3",
        "audio/ogg": ".ogg",
        "audio/amr": ".amr",
        "video/mp4": ".mp4",
        "video/3gpp": ".3gp",
        "text/plain": ".txt",
        "application/pdf": ".pdf",
    }
    base = f"media_{idx:09d}"
    ext = ""
    if suggested:
        _, ext0 = os.path.splitext(suggested)
        if ext0:
            ext = ext0.lower()
    if not ext and ct in ext_map:
        ext = ext_map[ct]
    if not ext and ct and "/" in ct:
        ext = "." + ct.split("/")[-1].lower()
    if not ext:
        ext = ".bin"
    return base + ext

CSS = """
<style>
:root { --bg:#0b1020; --card:#121a34; --bubble-in:#0e6b3a; --bubble-out:#1e2a55; --text:#e7ecff; --muted:#a6b0d1; --link:#8ab4ff; }
*{box-sizing:border-box}
body{margin:0;padding:2rem;background:var(--bg);color:var(--text);font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,"Helvetica Neue",Arial}
a{color:var(--link)}
.container{max-width:1100px;margin:0 auto}
.card{background:var(--card);border-radius:16px;padding:1rem 1.2rem;box-shadow:0 10px 30px rgba(0,0,0,.25)}
.header{display:flex;align-items:center;gap:.75rem;margin-bottom:1rem}
.h1{font-size:1.4rem;font-weight:700;margin:0}
.meta{color:var(--muted);font-size:.92rem}
.grid{display:grid;grid-template-columns:1fr;gap:1rem}
.contact-list{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:1rem}
.contact{padding:1rem;border-radius:16px;background:var(--card);box-shadow:0 8px 24px rgba(0,0,0,.2)}
.contact h3{margin:.2rem 0 .4rem 0}
.badge{display:inline-block;background:#223; color:#c9d3ff; border-radius:999px; padding:.1rem .6rem; font-size:.85rem; margin-left:.4rem}
.thread{display:flex;flex-direction:column;gap:.6rem}
.msg{max-width:75%;padding:.6rem .8rem;border-radius:16px;line-height:1.35}
.in{align-self:flex-start;background:var(--bubble-out)}
.out{align-self:flex-end;background:var(--bubble-in)}
.msg .small{display:block;color:var(--muted);font-size:.8rem;margin-top:.2rem}
.media{margin-top:.35rem;border-radius:12px;overflow:hidden}
.media img{max-width:100%;display:block}
.media video,.media audio{width:100%}
.separator{color:#9fb0ff33;text-align:center;margin:1rem auto .5rem}
hr{border:none;border-top:1px solid #ffffff1a;margin:1rem 0}
.nav{display:flex;gap:.6rem;flex-wrap:wrap;margin-bottom:1rem}
.nav a{background:#1a2244;padding:.4rem .7rem;border-radius:999px;text-decoration:none}
.year{opacity:.8;font-weight:600;margin:1rem 0 .4rem}
.footer{color:#99a3c5;font-size:.9rem;margin-top:1rem}
</style>
"""

HTML_HEADER = f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{title}}</title>{CSS}</head><body><div class="container">
"""

HTML_FOOTER = """<div class="footer">Export généré localement — ouvrez <code>index.html</code> pour naviguer.</div></div></body></html>"""

INDEX_INTRO = """
<div class="header"><h1 class="h1">📱 Archive SMS/MMS/RCS</h1></div>
<p class="meta">Cliquez un contact pour ouvrir la conversation. Les pièces jointes (photos/vidéos/audio) sont visibles directement.</p>
<hr>
"""

def open_contact_page(path_html: str, title: str, split_by_year=False):
    # créer page si absente, avec entête
    write_if_new(path_html, HTML_HEADER.replace("{title}", html.escape(title)) +
                 f'<div class="header"><h1 class="h1">💬 {html.escape(title)}</h1></div>\n<div class="thread">\n')
    # si split_by_year, on insérera des séparateurs lors de l’écriture
    return

def close_contact_page(path_html: str):
    append(path_html, "</div>\n" + HTML_FOOTER)

def write_msg(path_html: str, direction: str, date_str: str, who: str, body_html: str, year_sep: str = None):
    # year_sep => si fourni, insère un séparateur d'année
    if year_sep:
        append(path_html, f'<div class="separator">— {html.escape(year_sep)} —</div>\n')
    bubble_class = "out" if direction == "out" else "in"
    who_txt = f"{who}" if who else ("Moi" if bubble_class=="out" else "Contact")
    block = f'<div class="msg {bubble_class}">{body_html}<span class="small">{html.escape(who_txt)} • {html.escape(date_str)}</span></div>\n'
    append(path_html, block)

def render_text(text: str) -> str:
    if not text:
        return ""
    # echappe HTML et transforme liens en <a>
    t = html.escape(text)
    # URLs -> liens
    t = re.sub(r'(https?://[^\s<]+)', r'<a href="\1" target="_blank" rel="noopener">\1</a>', t)
    return t.replace("\n", "<br>")

# ----------------------------
# Parsing principal
# ----------------------------

def main():
    ap = argparse.ArgumentParser(description="Exporter SMS Backup & Restore (XML) en HTML+Médias lisibles.")
    ap.add_argument("--xml", required=True, help="Chemin vers le fichier XML (très gros).")
    ap.add_argument("--out", default="export", help="Dossier de sortie (par défaut: ./export)")
    ap.add_argument("--split-by-year", action="store_true", help="Découper chaque contact par année (recommandé pour très longues conversations).")
    ap.add_argument("--limit", type=int, default=0, help="Limiter le nombre de messages (debug). 0 = pas de limite.")
    args = ap.parse_args()

    xml_path = args.xml
    out_dir  = args.out
    media_dir = os.path.join(out_dir, "media")
    contacts_dir = os.path.join(out_dir, "contacts")

    ensure_dir(out_dir)
    ensure_dir(media_dir)
    ensure_dir(contacts_dir)

    # Stats & index
    contact_stats = {}      # key -> {"count": int, "files": set()}
    known_contacts = set()  # keys
    media_counter = 0
    total_msgs = 0

    # Index header
    index_path = os.path.join(out_dir, "index.html")
    write_if_new(index_path, HTML_HEADER.replace("{title}", "Archive SMS/MMS/RCS") + INDEX_INTRO + '<div class="contact-list">\n')

    # Streaming parse
    context = ET.iterparse(xml_path, events=("start", "end"))
    _, root = next(context)

    # util pour écrire une carte contact dans index (définitif à la fin aussi)
    index_cards_buffer = []  # on tamponne puis on ajoutera en fin

    # Mémoire pour séparateur d'années par contact
    last_year_by_contact = {}

    def contact_file_path(key: str, year: str = None):
        fname = safe_filename(key)
        if args.split_by_year and year:
            fname = f"{fname}__{year}"
        return os.path.join(contacts_dir, f"{fname}.html")

    # Boucle
    for event, elem in context:
        if event != "end":
            continue

        tag = elem.tag.lower()

        # ---------------- SMS ----------------
        if tag == "sms":
            address = elem.attrib.get("address", "") or elem.attrib.get("address_email", "")
            name = elem.attrib.get("contact_name", "") or elem.attrib.get("name", "")
            body = elem.attrib.get("body", "")
            date_ms = elem.attrib.get("date")
            type_ = elem.attrib.get("type")  # 1=inbox,2=sent (convention Android)
            direction = "in" if type_ == "1" else "out"

            key = contact_key(address, name)
            date_str = ms_to_local_str(date_ms)
            year = date_str[:4] if date_str else None

            # fiche contact
            if key not in known_contacts:
                known_contacts.add(key)
                contact_stats[key] = {"count": 0, "files": set()}

            cfile = contact_file_path(key, year if args.split_by_year else None)
            open_contact_page(cfile, key, split_by_year=args.split_by_year)

            # séparateur année si changé
            ysep = None
            if args.split_by_year:
                # pas besoin de séparateur, car fichier par année
                pass
            else:
                prev = last_year_by_contact.get(key)
                if year and prev != year:
                    ysep = year
                    last_year_by_contact[key] = year

            write_msg(
                cfile,
                direction,
                date_str,
                "Moi" if direction == "out" else key,
                render_text(body),
                year_sep=ysep
            )

            contact_stats[key]["count"] += 1
            contact_stats[key]["files"].add(cfile)
            total_msgs += 1

            if total_msgs % 10000 == 0:
                print(f"[+] {total_msgs} messages traités...")

            if args.limit and total_msgs >= args.limit:
                root.clear()
                break

            root.clear()

        # ---------------- MMS ----------------
        elif tag == "mms":
            address = elem.attrib.get("address", "") or elem.attrib.get("address_email", "")
            name = elem.attrib.get("contact_name", "") or elem.attrib.get("name", "")
            date_ms = elem.attrib.get("date")
            # type MMS: box="1" (inbox), "2" (sent) souvent
            box = elem.attrib.get("msg_box") or elem.attrib.get("box") or elem.attrib.get("m_type")
            # Heuristique direction
            direction = "in" if (box == "1") else "out"

            key = contact_key(address, name)
            if key not in known_contacts:
                known_contacts.add(key)
                contact_stats[key] = {"count": 0, "files": set()}

            date_str = ms_to_local_str(date_ms)
            year = date_str[:4] if date_str else None

            cfile = contact_file_path(key, year if args.split_by_year else None)
            open_contact_page(cfile, key, split_by_year=args.split_by_year)

            # Construire contenu MMS
            parts_parent = elem.find("parts")
            body_chunks = []
            media_html = []

            if parts_parent is None:
                # ancien format: parts au même niveau ?
                parts = elem.findall("part")
            else:
                parts = parts_parent.findall("part")

            for part in parts:
                ct = part.attrib.get("ct", "")  # content-type
                text = part.attrib.get("text")  # texte éventuel
                data = part.attrib.get("data")  # base64 éventuel
                name_attr = part.attrib.get("name") or part.attrib.get("cl")

                if ct.startswith("text"):
                    if text:
                        body_chunks.append(render_text(text))
                    continue

                # Media
                if data:
                    try:
                        blob = base64.b64decode(data, validate=False)
                    except Exception:
                        blob = base64.b64decode(data + "==")
                    media_counter += 1
                    fname = guess_part_filename(media_counter, ct, name_attr)
                    fpath = os.path.join(media_dir, fname)
                    with open(fpath, "wb") as mf:
                        mf.write(blob)

                    # Affichage selon type
                    if ct.startswith("image/"):
                        media_html.append(f'<div class="media"><a href="../media/{fname}" target="_blank"><img src="../media/{fname}" alt="{html.escape(ct)}"></a></div>')
                    elif ct.startswith("video/"):
                        media_html.append(f'<div class="media"><video controls src="../media/{fname}"></video></div>')
                    elif ct.startswith("audio/"):
                        media_html.append(f'<div class="media"><audio controls src="../media/{fname}"></audio></div>')
                    else:
                        media_html.append(f'<div class="media"><a href="../media/{fname}" download>Télécharger {html.escape(ct)}</a></div>')
                else:
                    # Pas de base64 -> on laisse un lien symbolique si nom connu
                    if name_attr:
                        media_html.append(f'<div class="media"><em>(Pièce jointe non incluse dans le backup : {html.escape(name_attr)})</em></div>')

            body_html = "<br>".join(body_chunks) if body_chunks else "<em>(MMS sans texte)</em>"
            if media_html:
                body_html += "<br>" + "\n".join(media_html)

            # séparateur d'année éventuel
            ysep = None
            if not args.split_by_year:
                prev = last_year_by_contact.get(key)
                if year and prev != year:
                    ysep = year
                    last_year_by_contact[key] = year

            write_msg(
                cfile,
                direction,
                date_str,
                "Moi" if direction == "out" else key,
                body_html,
                year_sep=ysep
            )

            contact_stats[key]["count"] += 1
            contact_stats[key]["files"].add(cfile)
            total_msgs += 1

            if total_msgs % 10000 == 0:
                print(f"[+] {total_msgs} messages traités...")

            if args.limit and total_msgs >= args.limit:
                root.clear()
                break

            root.clear()

        # d'autres balises : <rcs> n’est pas standardisé dans ce backup ; souvent intégrés comme <sms> ou <mms>.
        else:
            root.clear()

    # Clore toutes les pages contact
    for key in known_contacts:
        for cfile in contact_stats[key]["files"]:
            # n’ajoute le footer qu’une fois par fichier (si absent)
            with open(cfile, "rb") as ck:
                tail = ck.read()[-2000:]
            if b"</html>" not in tail:
                close_contact_page(cfile)

    # Générer les cartes contacts dans l'index
    # tri par nb messages décroissant
    sorted_contacts = sorted(known_contacts, key=lambda k: contact_stats[k]["count"], reverse=True)
    for key in sorted_contacts:
        count = contact_stats[key]["count"]
        # si split par année, on pointe vers une "page sommaire" auto : on crée une nav
        # autrement, un seul fichier.
        files = sorted(list(contact_stats[key]["files"]))
        if len(files) == 1:
            rel = os.path.relpath(files[0], out_dir)
            index_cards_buffer.append(
                f'<div class="contact"><h3>{html.escape(key)}</h3><div class="meta">{count} messages</div>'
                f'<p><a href="{html.escape(rel)}">Ouvrir la conversation</a></p></div>\n'
            )
        else:
            # Créer une page sommaire par contact listant les années
            contact_summary = os.path.join(os.path.dirname(files[0]), safe_filename(key) + "__SOMMAIRE.html")
            if not os.path.exists(contact_summary):
                write_if_new(contact_summary, HTML_HEADER.replace("{title}", f"Sommaire — {html.escape(key)}") +
                             f'<div class="header"><h1 class="h1">📂 {html.escape(key)} — Sommaire</h1></div>\n<div class="nav">\n')
                # ajouter liens vers fichiers (année)
                for fp in sorted(files):
                    label = os.path.splitext(os.path.basename(fp))[0]
                    # extraire l'année depuis le suffixe __YYYY
                    m = re.search(r"__([12][0-9]{3})$", label)
                    lab = m.group(1) if m else label
                    relf = os.path.relpath(fp, os.path.dirname(contact_summary))
                    append(contact_summary, f'<a href="{html.escape(relf)}">{html.escape(lab)}</a>\n')
                append(contact_summary, "</div>\n" + HTML_FOOTER)

            rel = os.path.relpath(contact_summary, out_dir)
            index_cards_buffer.append(
                f'<div class="contact"><h3>{html.escape(key)}</h3><div class="meta">{count} messages</div>'
                f'<p><a href="{html.escape(rel)}">Voir les années</a></p></div>\n'
            )

    append(index_path, "".join(index_cards_buffer))
    append(index_path, "</div>\n" + HTML_FOOTER)

    # Petit CSV de stats
    with open(os.path.join(out_dir, "contacts_stats.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["contact", "messages", "fichiers_html"])
        for key in sorted_contacts:
            w.writerow([key, contact_stats[key]["count"], " | ".join(sorted(os.path.relpath(p, out_dir) for p in contact_stats[key]["files"]))])

    print(f"✅ Terminé : {total_msgs} messages traités, {len(known_contacts)} contacts.")
    print(f"→ Ouvre {index_path}")

if __name__ == "__main__":
    main()

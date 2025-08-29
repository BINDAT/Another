import sqlite3
import xml.etree.ElementTree as ET

db = sqlite3.connect("messages.db")
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS sms (
    address TEXT,
    date INTEGER,
    type TEXT,
    body TEXT
)
""")

# Parse en streaming pour gros fichiers
context = ET.iterparse("sms.xml", events=("start", "end"))
_, root = next(context)

count = 0
for event, elem in context:
    if event == "end" and elem.tag == "sms":
        address = elem.attrib.get("address")
        date = elem.attrib.get("date")
        type_ = elem.attrib.get("type")
        body = elem.attrib.get("body")

        cur.execute("INSERT INTO sms VALUES (?, ?, ?, ?)",
                    (address, date, type_, body))

        count += 1
        if count % 10000 == 0:  # commit par lot
            db.commit()
            print(f"{count} SMS insérés...")

        root.clear()  # libère la mémoire

db.commit()
db.close()
print("Import terminé ✅")

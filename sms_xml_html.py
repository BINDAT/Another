import os
import xml.etree.ElementTree as ET

INPUT_FILE = "sms.xml"     # ton backup XML
OUTPUT_DIR = "export"
MEDIA_DIR = os.path.join(OUTPUT_DIR, "media")

os.makedirs(MEDIA_DIR, exist_ok=True)

html_output = ["<html><head><meta charset='utf-8'><title>SMS Backup</title></head><body>"]
html_output.append("<h1>Historique SMS/MMS/RCS</h1>")

# Streaming parse pour gros fichiers
context = ET.iterparse(INPUT_FILE, events=("start", "end"))
_, root = next(context)

for event, elem in context:
    if event == "end" and elem.tag == "sms":
        address = elem.attrib.get("address", "inconnu")
        date = elem.attrib.get("date", "")
        body = elem.attrib.get("body", "")
        html_output.append(f"<p><b>{address}</b> [{date}]<br>{body}</p>")
        root.clear()

    elif event == "end" and elem.tag == "mms":
        address = elem.attrib.get("address", "inconnu")
        date = elem.attrib.get("date", "")
        html_output.append(f"<p><b>{address}</b> [{date}] (MMS)</p>")

        # Parcours des "part" (texte ou média)
        for part in elem.findall("part"):
            ctype = part.attrib.get("ct", "")
            text = part.attrib.get("text", "")
            data = part.attrib.get("data", "")
            
            if ctype.startswith("text"):
                html_output.append(f"<p>{text}</p>")
            else:
                # média
                name = part.attrib.get("name", "media")
                fname = f"{len(os.listdir(MEDIA_DIR))}_{name}"
                path = os.path.join(MEDIA_DIR, fname)

                # dans le XML, les gros fichiers peuvent être en base64
                if data:
                    with open(path, "wb") as f:
                        f.write(data.encode("utf-8"))
                    html_output.append(f"<p><a href='media/{fname}'>{ctype}</a></p>")

        root.clear()

html_output.append("</body></html>")

with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write("\n".join(html_output))

print("✅ Export terminé. Ouvre export/index.html dans ton navigateur.")

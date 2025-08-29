import xml.etree.ElementTree as ET
import csv

tree = ET.parse("fichier.xml")
root = tree.getroot()

with open("sortie.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["id", "nom", "valeur"])  # adapter selon les balises

    for elem in root.findall("element"):  # adapter selon ton XML
        writer.writerow([
            elem.find("id").text,
            elem.find("nom").text,
            elem.find("valeur").text
        ])

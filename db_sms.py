import sqlite3

conn = sqlite3.connect("donnees.db")
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS elements (id TEXT, nom TEXT, valeur TEXT)")

for elem in root.findall("element"):
    c.execute("INSERT INTO elements VALUES (?, ?, ?)", (
        elem.find("id").text,
        elem.find("nom").text,
        elem.find("valeur").text
    ))

conn.commit()
conn.close()

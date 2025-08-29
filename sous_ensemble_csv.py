import pandas as pd
import sqlite3

con = sqlite3.connect("messages.db")
df = pd.read_sql_query("SELECT * FROM sms LIMIT 10000", con)
df.to_csv("sms_export.csv", index=False)

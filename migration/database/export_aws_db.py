import json
import os
import psycopg
from datetime import date, datetime
from decimal import Decimal

OUTPUT_FILE = "/tmp/aws_documents_export.json"

def serialize(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value

conn = psycopg.connect(os.environ["DATABASE_URL"])
cur = conn.cursor()

cur.execute("SELECT * FROM documents ORDER BY id")
columns = [desc.name for desc in cur.description]

records = []
for row in cur.fetchall():
    records.append({
        column: serialize(value)
        for column, value in zip(columns, row)
    })

with open(OUTPUT_FILE, "w") as file:
    json.dump(records, file, indent=2)

print(f"Exported AWS records: {len(records)}")
print(f"Export file: {OUTPUT_FILE}")

cur.close()
conn.close()
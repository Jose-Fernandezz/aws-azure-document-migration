import json
from pathlib import Path

from application.database import execute_query, fetch_one


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = PROJECT_ROOT / "sample-documents" / "manifest.json"


def load_manifest():
    with MANIFEST_PATH.open("r", encoding="utf-8") as file:
        records = json.load(file)

    if len(records) != 50:
        raise ValueError(
            f"Expected 50 manifest records, but found {len(records)}."
        )

    print(f"Manifest validated: {len(records)} records found.")
    return records


def load_records_into_rds(records):
    for record in records:
        execute_query(
            """
            INSERT INTO documents (
                record_number,
                original_filename,
                object_key,
                title,
                description,
                department,
                uploaded_by,
                uploaded_at,
                file_type,
                file_size,
                storage_provider,
                storage_location,
                checksum
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (record_number) DO NOTHING
            """,
            (
                record["record_number"],
                record["original_filename"],
                record["object_key"],
                record["title"],
                record["description"],
                record["department"],
                record["uploaded_by"],
                record["uploaded_at"],
                record["file_type"],
                record["file_size"],
                "s3",
                record["object_key"],
                record["checksum"],
            ),
        )

    result = fetch_one("SELECT COUNT(*) AS count FROM documents")
    print(f"RDS document count: {result['count']}")


def main():
    records = load_manifest()
    load_records_into_rds(records)


if __name__ == "__main__":
    main()
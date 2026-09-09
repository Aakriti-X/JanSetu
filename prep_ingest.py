import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore
import sqlite3, database

database.init_db()

# Remove failed log entry so hackk 4.pdf can be re-ingested
conn = sqlite3.connect("ingestion_log.db")
rows = conn.execute("DELETE FROM ingestion_log WHERE original_filename LIKE '%hackk%'")
conn.commit()
conn.close()
print("Cleared old log entries:", rows.rowcount)

from ingest_manager import ingest_file
result = ingest_file(file_path="hackk 4.pdf", user_id="cli_user", original_filename="hackk 4.pdf")
print("Status:", result["status"])
print("Message:", result["message"])
print("Chunks:", result["chunks"])

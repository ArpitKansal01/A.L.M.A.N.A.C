import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

try:
    conn = mysql.connector.connect(
        host=os.environ.get("host"),
        port=os.environ.get("port"),
        user=os.environ.get("user"),
        password=os.environ.get("password"),
        database=os.environ.get("database")
    )
    print("✅ Connected to MySQL successfully!")
    conn.close()
except mysql.connector.Error as err:
    print(f"❌ Error: {err}")

import psycopg2
import pandas as pd

# Connect to PostgreSQL
conn = psycopg2.connect(
    host="dpg-d7suitm7r5hc738kp680-a.singapore-postgres.render.com",
    database="debtdb",
    user="divya",
    password="k8Vq5iLU7OzObejUSU2zHS0uTGCbrntw",
    port="5432"
)

cursor = conn.cursor()

# Read CSV file
df = pd.read_csv(
    r"C:\Users\Dell\Downloads\cleaned_Country-Series - Metadata (1).csv"
)

# Replace spaces with underscores in column names
df.columns = df.columns.str.strip().str.replace(" ", "_")

# Optional: remove null values
df = df.fillna("")

# Create table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS country_series (
    type TEXT,
    country_code VARCHAR(20),
    series_code VARCHAR(100),
    description TEXT,
    series_name TEXT
)
""")

# Insert values into table
for index, row in df.iterrows():
    cursor.execute("""
        INSERT INTO country_series
        (type, country_code, series_code, description, series_name)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        row['type'],
        row['country_code'],
        row['series_code'],
        row['description'],
        row['series_name']
    ))

# Save changes
conn.commit()

print("Data inserted successfully!")

# Access inserted values
cursor.execute("SELECT * FROM country_series LIMIT 10")

rows = cursor.fetchall()

print("\nFirst 10 Rows:\n")

for row in rows:
    print(row)

# Close connection
cursor.close()
conn.close()
import openpyxl, psycopg2, os, dotenv

# PostgreSQL connection configuration

def read_env(env_path=".env", override=True):

    dotenv.load_dotenv(dotenv_path=str(env_path), override=override)
    parsed = dotenv.dotenv_values(dotenv_path=str(env_path))
    result = {k: os.environ.get(k, v) for k, v in parsed.items() if k is not None}

    return result


env = read_env()

conn = psycopg2.connect(
host=env.get("PGHOST", "localhost"),
database=env.get("PGDATABASE", "mydatabase"),
user=env.get("PGUSER", "myuser"),
password=env.get("PGPASSWORD", "mypass"),
port=int(env.get("PGPORT", 5432))
)
# Open the Excel file using openpyxl
wb = openpyxl.load_workbook(r'data\transports.xlsx')
sheet = wb.active  # assumes data is in the first sheet

# Connect to the PostgreSQL database
cur = conn.cursor()

# Skip header row, iterate through each row in Excel
for idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
    date, day_id, city_id, day_type_id, transport_cost, tax = row
    sql = """
        INSERT INTO transports (date, day_id, city_id, day_type_id, transport_cost, tax)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cur.execute(sql, (date, day_id, city_id, day_type_id, transport_cost, tax))

conn.commit()
cur.close()
conn.close()
print("Done inserting all rows.")



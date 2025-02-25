import sqlite3
import pandas as pd

def extract_excel(db_name, table_name):
    conn = sqlite3.connect(db_name)

    df = pd.read_sql_query('SELECT * FROM ' + table_name, conn)
    df.to_excel(f'{table_name}.xlsx')

    conn.close()

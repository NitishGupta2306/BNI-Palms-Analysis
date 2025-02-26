import sqlite3
import pandas as pd

def extract_excel():
    conn = sqlite3.connect('referrals.db')

    df = pd.read_sql_query('SELECT * FROM referrals', conn)
    df.to_excel(f'referrals.xlsx')

    conn.close()

    #conn = sqlite3.connect('oto.db')

    #df = pd.read_sql_query('SELECT * FROM oto', conn)
    #df.to_excel(f'oto.xlsx')

    #conn.close()

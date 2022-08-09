## This is the Database module. Which connects the python modules to
# the pSQL server.

from os import environ
from venv import create

import pandas
from dotenv import load_dotenv
#from sqlalchemy import create_engine
#from sqlalchemy.types import Integer, Numeric, String
import psycopg2


class Database:
    def __init__(self):
        load_dotenv()

        db_uri = environ.get("DATABASE_CONNECTION_URI")
        #self.engine = create_engine(db_uri, echo=True)

        self.conn = psycopg2.connect(f'dbname={environ.get("DB_NAME")} user={environ.get("DB_USER")}')


    def add_security(self, ticker: str, type: str, amount: int or float):
        """Add security to database.
        If the security isn't already present in the database then it should be added.
        If it does exist, the 'amount' value in the database should increase by the
        'amount' parameter.

        params: 
            ticker: consists of two parts: {SYMBOL_NAME}.{EXCHANGE_ID},
                then you can use, for example, MCD.MX for Mexican Stock Exchange.
                or MCD.US for NYSE.
            type: kind of security, ie: Stock, ETF, ETC, Index, Crypto,
                Bond, etc..
            amount: the quantity of said security to add."""
        
        # ------------------- Parameter manipulation ------------------ #

        ticker = ticker.upper()
        type = type.lower()
        
        # --- Check whether the security is already in the database --- #

        cur = self.conn.cursor()
        cur.execute(f"SELECT amount FROM holdings WHERE ticker = '{ticker}';")
        try:
            already_owned = cur.fetchone()[0]
        except TypeError:
            # already_owned is None, therefore not subscriptable.
            already_owned = None

        # ------------------- Database Manipulation ------------------- #

        if already_owned is None:
            sql = f"INSERT INTO holdings (ticker, type, amount) VALUES ('{ticker}', '{type}', {amount});"
            cur = self.conn.cursor()
            cur.execute(sql)
        else:
            new_amount = already_owned + amount

            sql = f"UPDATE holdings SET amount = {new_amount} WHERE ticker = '{ticker}';"
            cur = self.conn.cursor()
            cur.execute(sql)
        self.conn.commit()



if __name__ == '__main__':
    db = Database()

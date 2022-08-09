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
        self.cur = self.conn.cursor()

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

        already_owned = self.get_amount(ticker)

        # ------------------- Database Manipulation ------------------- #

        if already_owned is None:
            sql = f"INSERT INTO holdings (ticker, type, amount) VALUES ('{ticker}', '{type}', {amount});"
            self.cur.execute(sql)
        else:
            new_amount = already_owned + amount

            sql = f"UPDATE holdings SET amount = {new_amount} WHERE ticker = '{ticker}';"
            self.cur.execute(sql)
        self.conn.commit()

    def remove_security(self, ticker: str, amount: int or float):
        """Removes securities from database.
            Essentially a sell order.
        params:
            ticker: consists of two parts: {SYMBOL_NAME}.{EXCHANGE_ID},
                then you can use, for example, MCD.MX for Mexican Stock Exchange.
                or MCD.US for NYSE.
            amount: Quantity to remove."""
        
        # Read database and see if ticker exists
        already_owned = self.get_amount(ticker)

        # If the security is already owned, decrease 'amount' in DB by the 'amount' parameter.
        # Delete the row if it has been sold entirely.

        if already_owned is not None:
            new_amount = already_owned - amount

            if new_amount > 0:
                sql = f"UPDATE holdings SET amount = '{new_amount}' WHERE ticker = '{ticker}';"
                self.cur.execute(sql)

            elif new_amount == 0:
                sql = f"DELETE FROM holdings WHERE ticker = '{ticker}'"
                self.cur.execute(sql)

            else:
                raise Exception("Cannot sell more than holdings.")

            # Commit changes to DB.
            self.conn.commit()
        else:
            raise Exception("Cannot sell non-existing security.")

        # !TODO if 'amount' in DB reaches 0, remove it.

    def get_amount(self, ticker: str) -> int or float or None:
        """Returns the quantity of a given security in DB.
        params:
            ticker: consists of two parts: {SYMBOL_NAME}.{EXCHANGE_ID},
                then you can use, for example, MCD.MX for Mexican Stock Exchange.
                or MCD.US for NYSE."""

        self.cur.execute(f"SELECT amount FROM holdings WHERE ticker = '{ticker}';")
        try:
            return self.cur.fetchone()[0]
        except TypeError:
            # already_owned is None, therefore not subscriptable.
            return None

if __name__ == '__main__':
    db = Database()
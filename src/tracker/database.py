# This is the Database module. Which connects the python modules to
# the pSQL server.

from datetime import datetime
from os import environ
from venv import create

import pandas
import psycopg2
from dotenv import load_dotenv
from sqlalchemy import create_engine


class Database:
    def __init__(self):
        load_dotenv()
        self.connect_db()

    def connect_db(self):
        """Establishes a connection to he PostgreSQL server"""
        db_uri = environ.get("DATABASE_CONNECTION_URI")
        self.engine = create_engine(db_uri, echo=True)
        self.conn = psycopg2.connect(
            f'dbname={environ.get("DB_NAME")} user={environ.get("DB_USER")} password={environ.get("DB_PASSWORD")}')
        self.cur = self.conn.cursor()



    def add_security(self, ticker: str, type: str, amount: int or float):
        """Add security to database.
        If the security isn't already present in the database then it should be added.
        If it does exist, the 'amount' value in the database should increase by the
        'amount' parameter.

        params: 
            ticker: consists of two parts: {SYMBOL_NAME}_{EXCHANGE_ID}
            type: kind of security, ie: Stock, ETF, ETC, Index, Crypto,
                Bond, etc..
            amount: the quantity of said security to add."""

        # ------------------- Parameter manipulation ------------------ #

        ticker = self.translate_to_db(ticker.upper())
        type = type.lower()

        # --- Check whether the security is already in the database --- #

        already_owned = self.get_amount(ticker)

        # ------------------- Database Manipulation ------------------- #

        if already_owned is None:
            sql = f"""INSERT INTO holdings
            (ticker, type, amount)
            VALUES ('{ticker}', '{type}', {amount});"""
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
            ticker: consists of two parts: {SYMBOL_NAME}_{EXCHANGE_ID},

            amount: Quantity to remove."""

        # Read database and see if ticker exists
        already_owned = self.get_amount(ticker)

        # If the security is already owned, decrease 'amount' in DB by the 'amount' parameter.
        # Delete the row if it has been sold entirely.

        if already_owned is not None:
            new_amount = already_owned - amount

            if new_amount > 0:
                sql = f"UPDATE holdings.holdings SET amount = '{new_amount}' WHERE ticker = '{ticker}';"
                self.cur.execute(sql)

            elif new_amount == 0:
                sql = f"DELETE FROM holdings.holdings WHERE ticker = '{ticker}'"
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
            ticker: consists of two parts: {SYMBOL_NAME}_{EXCHANGE_ID}"""
        ticker = self.translate_to_db(ticker)
        try:
            self.cur.execute(
                f"SELECT amount FROM holdings WHERE ticker = '{ticker}';")
        except psycopg2.errors.UndefinedTable:
            # Table does not exist
            self.create_holdings_table()
        try:
            return self.cur.fetchone()[0]
        except TypeError:
            # already_owned is None, therefore not subscriptable.
            return None

    def read_historical_data(self, ticker: str,
                             *columns: str, start: str, stop: str) -> pandas.DataFrame:
        """Reads data from DB.
        params:
            ticker: consists of two parts: {SYMBOL_NAME}_{EXCHANGE_ID}

            columns: columns to retrieve. Ie: ticker, price, open, close,
                    adj close, etc.
        returns: A Pandas DataFrame containing historical price data for
                ticker."""
        columns_sql = ''
        for column in columns:
            if column != columns[-1]:
                columns_sql += column + ", "
            else:
                columns_sql += column
        ticker = self.translate_to_db(ticker)
        sql = f"SELECT {columns_sql} FROM historical.{ticker} BETWEEN {start} AND {stop}"
        data = self.cur.execute(sql)

    def write_historical_data(self, ticker: str, data: pandas.DataFrame,
                              _from: datetime):
        """Writes ticker price data to DB.

        -- Params --
            ticker: consists of: {SYMBOL_NAME}_{EXCHANGE_ID}
            data: data to be written to db."""
        ticker = self.translate_to_db(ticker)
        try:
            data.to_sql(ticker, self.engine, 'historical',
                        if_exists='fail')
        except ValueError("Table already exists."):
            pass

    def create_ticker_table(self, ticker):
        """Creates a DB table for the given ticker."""
        ticker = self.translate_to_db(ticker)
        sql = f"""CREATE TABLE historical.{ticker} (
            date DATE PRIMARY KEY,
            open FLOAT NOT NULL,
            high FLOAT NOT NULL,
            low FLOAT NOT NULL,
            close FLOAT NOT NULL,
            adj_close FLOAT NOT NULL,
            volume INT NOT NULL);"""
        self.cur.execute(sql)

        self.conn.commit()

    def create_holdings_table(self):
        """Creates a DB table to store what securities you own."""
        sql = f"CREATE TABLE holdings(ticker VARCHAR(8) PRIMARY KEY, type VARCHAR(7) NOT NULL, amount INT NOT NULL);"
        self.cur.execute(sql)
        self.conn.commit()

    def translate_to_db(self, ticker: str) -> str:
        """Translates the ticker from the format given by the API response into DB usable format"""
        return ticker.replace(".", "_").lower()

    def translate_to_api(self, ticker: str) -> str:
        """Translates the ticker from DB usable format to the format needed by API server."""
        return ticker.replace("-", ".").upper()

if __name__ == '__main__':
    db = Database()
    db.add_security("NVDA_US", "stock", 1)

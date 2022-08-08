## This is the Database module. Which connects the python modules to
# the pSQL server.

from os import environ
from venv import create
from dotenv import load_dotenv
import pandas
from sqlalchemy import create_engine
from sqlalchemy.types import String, Numeric, Integer


class Database:
    def __init__(self):
        load_dotenv()
        db_uri = environ.get("DATABASE_CONNECTION_URI")
        self.engine = create_engine(db_uri, echo=True)
    
    def create_table(self, ticker: str):
        df = pandas.read_csv(
            'F:\\Programming\\Projects\\portfolio_tracker\\data\\tickers\\{ticker}.csv')

        df.to_sql(
            ticker,
            self.engine,

            if_exists='replace',
            index=False,
            chunksize=1000,

            dtype={
                "Date": String,
                "Open": Numeric,
                "High": Numeric,
                "Low": Numeric,
                "Close": Numeric,
                "Adjusted": Numeric,
                "Volume": Integer
            }
        )


if __name__ == '__main__':
    db = Database()
    db.create_table()
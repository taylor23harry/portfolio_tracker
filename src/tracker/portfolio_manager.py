## This module is used to manage the portfolio, such as keeping track
# of portfolio securities.

from os import environ
from dotenv import load_dotenv
import pandas
from datetime import date

class Manager:
    def __init__(self):
        load_dotenv()
        self.data = {} # Main DataFrame
        self.datafile = environ.get("DATA_DIRECTORY") + "\\portfolio.csv"
    
    def add_security(self, type: str, ticker: str, 
        date: str= date.today()):
        """Adds the specified security to the portfolio.
        params:
            type: Type of security, ex: Stock, ETF, ETC, Crypto...
            
            ticker: consists of two parts: {SYMBOL_NAME}.{EXCHANGE_ID},
                then you can use, for example, MCD.MX
                for Mexican Stock Exchange. or MCD.US for NYSE.
                Check the list of supported exchanges to get more information
                about stock markets this supports at: 
                https://eodhistoricaldata.com/financial-apis/list-supported-exchanges/
            
            date: the day the security was purchased, this is to calculate
                the ongoing profit effectively."""
        
        security = {
            "type": type,
            "ticker": ticker,
            "purchase_date": date
        }

        self.data[ticker] = pandas.json_normalize(security)

    def write_csv(self):
        """Writes the current self.data DataFrame to a csv file."""
        self.data.to_csv(self.datafile())
        

manager = Manager()
manager.add_security("stock", "AAPL.US")



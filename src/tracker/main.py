## Main tracker.
# This is the part of the application which manages the data.
# It fetches, analyses and saves historical and present data for
# one's portfolio.

import os
import requests
import json
import pandas
from typing import List
from dotenv import load_dotenv


# This class uses the EODHD APIs found at https://eodhistoricaldata.com
# (End Of Day Historical Data)
class EODHD:
    def __init__(self):
        load_dotenv() # Reads .env file
        self.api_token = os.environ.get("API_TOKEN")
        self.data_directory = os.environ.get("DATA_DIRECTORY")
        self.data = {}

##-------------------------------- Get Data --------------------------------##

    def get_historical_data(self, ticker: str, period: str, _from: str, to: str) -> List[int, str]:
        """Fetches historical data for the given ticker.
        params:
            ticker: consists of two parts: {SYMBOL_NAME}.{EXCHANGE_ID},
                then you can use, for example, MCD.MX for Mexican Stock Exchange.
                or MCD.US for NYSE. 
                Check the list of supported exchanges to get more information about
                stock markets this supports:
                https://eodhistoricaldata.com/financial-apis/list-supported-exchanges/
            
            period: use 'd' for daily, 'w' for weekly, 'm' for monthly prices. 
                By default, daily prices will be shown.
            
            from and to - the format is 'YYYY-MM-DD'.
                If you need data from Jan 5, 2017, to Feb 10, 2017,
                you should use from=2017-01-05 and to=2017-02-10.
        """
        request_data = {
            "fmt": "csv",
            "period": period,
            "order": "a",
            "from": _from,
            "to": to

        }

        url = f"https://eodhistoricaldata.com/api/eod/{ticker}?api_token={self.api_token}"
        for key, value in request_data.items():
            url += ("".join(["&", key, "=", value]))
        request = requests.get(url)
        return [request.status_code, request.text]
        

##---------------------------- CSV Manipulation ----------------------------##

    def read_csv(self):
        """Read data from CSV files in the DATA_DIRECTORY .env variable."""
        files = os.listdir(self.data_directory)
        for file in files:
            if file.endswith('.csv'):
                filename = file[:-4] # Filename without '.csv'
                self.data[filename] = pandas.read_csv(self.data_directory + "\\" +
                file)

    def save_to_csv(self):
        """Writes data to CSV"""
        for ticker in self.data:
            ticker.to_csv()

if __name__ == '__main__':
    eod = EODHD()
    eod.get_historical_data("MCD.US", "d", "2015-10-10", "2021-10-10")

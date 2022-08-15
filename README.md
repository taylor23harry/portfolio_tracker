# portfolio_tracker
This is a investment tracker for my personal portfolio.
I was unsatisfied with the features of other portfolio trackers such as Delta,
so I decided to create my own.

Author: Harry Taylor (taylor23harry@gmail.com)
Version: (07/08/2022, v0.01 Beta)


---- Environment file guide -----

This project relies on API keys and custom folder directories to work,
here is an outline of the different keys you need to declare in a .env file
which should be placed in the ./src folder.

API_TOKEN = '' # The API key you get from https://eodhistoricaldata.com/
DB_NAME = '' # The name of your PostgreSQL database
DB_PASSWORD = '' # DB_USER password
DB_USER = '' # Database user

DATABASE_CONNECTION_URI = "postgresql+psycopg2://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE_NAME}" # The URI used to connect to the postgres server.
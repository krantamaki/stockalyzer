"""
Example script for the database module db
Covers some function, but not all. Excluded functions are

  drop_table
  add_table
  get_connection

NOTE! Run from the stockalyzer directory with command
  > python3 -m example.db_example
"""
import logging
import os
import numpy as np


# Configure the root Logger object. This needs to be done
# before importing modules that use logging.
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, force=True,
                        format="%(levelname)s: %(name)s - %(message)s")
    
logger = logging.getLogger(__name__)


# Import the db module. For this to work run the script as instructed at the 
# beginning of the file
from src.db import *


# We will use a database called
database = "__db_example.db"


# We begin by initializing a temporary database
# As an example we will have tables for stocks (stock)
# consisting of columns ticker (key), price, last_update
# and options (option) consisting of columns id (key),
# underlying, strike, maturity, type
initialize_database(["stock", "option"],            # Table names
                    [                               # Table columns and their specifiers
                     [("ticker", "TEXT PRIMARY KEY"), ("price", "REAL"), ("lastUpdate", "TEXT")],
                     [("id", "TEXT PRIMARY KEY"), ("ticker", "TEXT"), ("strike", "REAL"),
                      ("maturity", "TEXT"), ("type", "TEXT NOT NULL CHECK (type IN ('call', 'put'))")]
                    ], database=database,           # Name of the database to be generated
                    reconnect=True,                 # Technically, not necessary as this will be the first connection
                    reset=True                      # Again, not strictly necessary as such database should not exist
                    )

# To check that the initialized database has tables stock and option we can 
# do the check
tables_found = check_database(["stock", "option"], no_extras=True)
logger.info(f"Tables 'stock' and 'option' found in the database: {tables_found}")

# We notice that specifying which database we are working with is not necessary as 
# the connection created by the initialize_database function is still in memory

# Next we will add some rows to the empty tables
today = np.datetime64('today', 'D')
insert_row(["AAPL", 200.0, str(today)], "stock")
insert_row(["MSFT", 300.0, str(today)], "stock")
insert_row(["AMZN", 100.0, str(today)], "stock")

# Note the option IDs are quite arbitrary and not of the correct format
month_from_today = today + np.timedelta64(30, 'D')
insert_row(["AAPL200C", "AAPL", 200.0, str(month_from_today), "call"], "option")
insert_row(["AAPL200P", "AAPL", 200.0, str(month_from_today), "put"], "option")
insert_row(["MSFT300C", "MSFT", 300.0, str(month_from_today), "call"], "option")
insert_row(["MSFT300P", "MSFT", 300.0, str(month_from_today), "put"], "option")
insert_row(["AMZN100C", "AMZN", 100.0, str(month_from_today), "call"], "option")
insert_row(["AMZN100P", "AMZN", 100.0, str(month_from_today), "put"], "option")

# We can access rows by some column value simply by calling
rows = get_by_value("AAPL", "option", "ticker")
logger.info(f"Found rows {rows} with value 'AAPL' on column 'ticker'")

# Likewise, we can update rows by column value
yesterday = today + np.timedelta64(-1, 'D')
update_by_value("MSFT", ("lastUpdate", str(yesterday)), "stock", "ticker")

# And we can delete rows simply by
delete_by_value("AMZN", "option", "ticker")

# If we want to make more complicated queries we can retrieve a cursor to the 
# connection and execute them with it
cur = get_cursor()
res = cur.execute(f"""SELECT ticker 
                      FROM stock 
                      WHERE price >= '200.0' AND lastUpdate = '{check(str(today))}';""")

rows = res.fetchall()
finalize_execution(cur)

logger.info(f"Tickers with price greater or equal to 200 and last update today: {rows}")

# Above we notice two things. Firstly, it is good practice to pass value inserted 
# into the query through check function that limits the risk of SQL injection
# Secondly, if we are done with the cursor we should commit changes and close connection
# This is done with finalize_execution function

# And since this is just an example we will delete the generated file
os.remove(database)

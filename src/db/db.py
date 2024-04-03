"""
Module for doing general operations on a database
"""
from __future__ import annotations
import sqlite3 as sql
import logging
import atexit
from pathlib import Path


# We use Pythons logging library to control and redirect our outputs.
# To this end be need to define the Logger object
_logger = logging.getLogger(__name__)

# Global variable that holds the connection to the database
# Should only be access via the get_connection function
_connection = None

# Function used to close the connection to the database at program termination
def _close_connection():
    global _connection
    if _connection is not None:
        _connection.close()

atexit.register(_close_connection)

# Global variable that holds the path to the database
# to which we currently have a connection
_connected_database = None


def check(text: str) -> str:
    """Function that does simple validation checks to avoid SQL injection. The checks
    are by no means exhaustive, but should be enough for most (basic) cases. In the cases were
    user has the ability to input text directly separate checks should be in place.

    :param text: The text to be validated
    :type text: str

    :raises ValueError: Raised if any of the validation checks is not passed

    :return: The original text if no checks failed
    :rtype: str
    """
    valid = True

    # We don't allow comments in the input
    if ("--" in text) or ("/*" in text) or ("*/" in text):
        valid = False
    
    # We don't allow closing (or opening) brackets
    if ('(' in text) or (')' in text):
        valid = False

    # We don't allow ending the statement
    if ';' in text:
        valid = False

    # We don't allow references to user or global variables
    if '@' in text:
        valid = False
      
    # We don't allow wildcards
    if ('%' in text) or ('_' in text):
        valid = False

    if not valid:
        _logger.error(f"SQL injection vulnerability spotted with input {text}!")
        raise ValueError(f"SQL injection vulnerability spotted with input {text}!")
    
    return text


def finalize_execution(cursor: sql.Cursor) -> None:
    """Function that does required finalizations for executed SQL commands

    :param cursor: Cursor object that executed the command.
    :type cursor: sqlite3.Cursor 
    
    :return: Void
    :rtype: None
    """
    cursor.connection.commit()
    cursor.close()


def get_connection(database: str = None, reconnect: bool = False, generate: bool = False) -> sql.Connection:
    """Function for accessing the global variable holding the connection to the database. Note that
    as we will only have a single database we will generally discourage switching connections. However,
    in the case that it is needed, it is made possible with the reconnect kwarg.

    :param database: The path to the database or ":memory:" for a temporary database in RAM. If connection \
                     is already established no need to pass a parameter. Defaults to None
    :type database: str, optional
    :param reconnect: Boolean flag allowing establishing a connection to a different database. Defaults to False
    :type reconnect: bool, optional
    :param generate: Boolean flag telling if a new file is allowed to be made at specified path if the database \
                     doesn't already exist. Defaults to False
    :type generate: bool, optional

    :raises FileNotFoundError: Raised when the specified database is not found
    :raises ValueError: Raised if a different database path is given when a connection is already established \
                        or if None is passed when no connection is yet established.

    :return: A Connection object to the specified database
    :rtype: sqlite3.Connection
    """
    global _connection, _connected_database

    if _connection is not None and (_connected_database != database and database is not None) and not reconnect:
        _logger.error(f"Tried to access database {database}, when connection to database {_connected_database} is already established!")
        raise ValueError(f"Tried to access database {database}, when connection to database {_connected_database} is already established!")

    if _connection is None or reconnect:
        if Path(str(database)).is_file() or generate or database == ":memory:":
            if database != _connected_database:
                _logger.warning(f"Changing the connected database during program execution is not recommended! (Changing from {_connected_database} to {database})")
                _connection = sql.connect(database)
                _connected_database = database

            return _connection

        elif database is None:
            _logger.error(f"Cannot connect to an unspecified database!")
            raise ValueError(f"Cannot connect to an unspecified database!")
        
        else:
            _logger.error(f"Invalid path {database} provided!")
            raise FileNotFoundError(f"Invalid path {database} provided!")  

    return _connection


def get_cursor(database: str = None, reconnect: bool = False) -> sql.Cursor:
    """Function for accessing a cursor to the specified database

    :param database: The path to the database or ":memory:" for a temporary database in RAM. If connection \
                     is already established no need to pass a parameter. Defaults to None
    :type database: str, optional
    :param reconnect: Boolean flag allowing establishing a connection to a different database. Defaults to False
    :type reconnect: bool, optional

    :return: A Cursor object to the specified database
    :rtype: sqlite3.Cursor
    """
    con = get_connection(database=database, reconnect=reconnect)

    return con.cursor()


def check_database(table_names: list[str], database: str = None, reconnect: bool = False, no_extras: bool = False) -> bool:
    """Function that checks if the required tables exist in the current database. Note that this function only
    verifies that the some tables of the specified names exist, but not assert that they would have a correct schema.

    :param table_names: A list of the names of the tables of interest
    :type table_names: list[str] 
    :param database: The path to the database or ":memory:" for a temporary database in RAM. If connection \
                     is already established no need to pass a parameter. Defaults to None
    :type database: str, optional
    :param reconnect: Boolean flag allowing establishing a connection to a different database. Defaults to False
    :type reconnect: bool, optional
    :param no_extras: Boolean flag telling if the database is allowed to contain extra tables in addition to \
                      the ones listed in table_names. Defaults to False
    :type no_extras: bool, optional

    :return: True if tables exist False otherwise
    :rtype: bool
    """
    cur = get_cursor(database=database, reconnect=reconnect)
    res = cur.execute("SELECT name FROM sqlite_master WHERE type='table';")

    database_tables_set = set([tup[0] for tup in res.fetchall()])
    table_names_set = set(table_names.copy())

    finalize_execution(cur)

    if len(table_names_set.difference(database_tables_set)) > 0:
        return False
    
    if no_extras and (len(database_tables_set.difference(table_names_set)) > 0):
        return False

    return True


def drop_table(name: str, database: str = None, reconnect: bool = False) -> None:
    """Function that drops a table of specified name from the wanted database.
    
    :param name: Name of the table to be dropped
    :type name: str
    :param database: The path to the database or ":memory:" for a temporary database in RAM. If connection \
                     is already established no need to pass a parameter. Defaults to None
    :type database: str, optional
    :param reconnect: Boolean flag allowing establishing a connection to a different database. Defaults to False
    :type reconnect: bool, optional

    :raises ValueError: Raised if table not found in the specified database.

    :return Void
    :rtype: None
    """
    cur = get_cursor(database=database, reconnect=reconnect)
    checked_name = check(name)

    table_exists = bool(len(cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{checked_name}';").fetchall()))

    if not table_exists:
        _logger.error(f"Cannot drop table {name} since it doesn't exist!")
        raise ValueError(f"Cannot drop table {name} since it doesn't exist!")
    
    _logger.warning(f"Dropping tables can lead to data loss! (Dropping table {checked_name})")

    cur.execute(f"DROP TABLE IF EXISTS {checked_name};")
    finalize_execution(cur)


def add_table(name: str, columns: list[tuple[str, str]], database: str = None, reconnect: bool = False, reset: bool = False) -> None:
    """Function for adding a table into a database. If the table already exists and reset kwarg is set to False, won't do
    anything. If reset is set to True the existing table will be removed and replaced by one with the specified schema.

    :param name: Name of the table to be added
    :type name: str
    :param columns: The column names and type specifiers for the table as a list of tuples
    :type columns: list[tuple[str, str]]
    :param database: The path to the database or ":memory:" for a temporary database in RAM. If connection \
                     is already established no need to pass a parameter. Defaults to None
    :type database: str, optional
    :param reconnect: Boolean flag allowing establishing a connection to a different database. Defaults to False
    :type reconnect: bool, optional
    :param reset: Boolean flag specifying if an existing table with specified name should be replaced by a new \
                  one. Defaults to False.
    :type reset: bool, optional

    :return: Void
    :rtype: None
    """
    cur = get_cursor(database=database, reconnect=reconnect)

    column_str = ", ".join([f"{tup[0]} {tup[1]}" for tup in columns])

    if reset:
        drop_table(name, database=database, reconnect=reconnect)

    cur.execute(f"CREATE TABLE IF NOT EXISTS {check(name)} ({check(column_str)});")

    finalize_execution(cur)


def initialize_database(table_names: list[str], table_columns: list[list[tuple[str, str]]],
                  database: str = None, reconnect: bool = False, reset: bool = False) -> None:
    """Function for initializing a database. Creates the needed database file and the specified tables with
    wanted columns. If a database already exists in the wanted path doesn't do anything unless reset kwarg is 
    set to True. In this case all tables will be removed from the old database and the new ones created in their
    stead.

    :param table_names: Names of the wanted tables as a list of strings
    :type table_names: list[str]
    :param table_columns: The columns of the tables as a nested list of tuples specifying the name of the column \
                          and the type specifiers
    :type table_columns: list[list[tuple[str, str]]]
    :param database: The path to the database or ":memory:" for a temporary database in RAM. If connection \
                     is already established no need to pass a parameter. Defaults to None
    :type database: str, optional
    :param reconnect: Boolean flag allowing establishing a connection to a different database. Defaults to False
    :type reconnect: bool, optional
    :param reset: Boolean flag specifying if an existing database in the specified path should be replaced by a new \
                  one. Defaults to False.
    :type reset: bool, optional

    :return: Void
    :rtype: None
    """
    if (not Path(database).is_file()) or reset:
        con = get_connection(database=database, reconnect=reconnect, generate=True)
        cur = con.cursor()

        if reset:
            res = cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
            database_tables = [tup[0] for tup in res.fetchall()]

            for table in database_tables:
                drop_table(table, database=database, reconnect=reconnect)

        for tup in zip(table_names, table_columns):
            add_table(*tup, database=database, reconnect=reconnect)

        finalize_execution(cur)


def insert_row(row_values: list[any], table_name: str, database: str = None, reconnect: bool = False) -> None:
    """Function for inserting a row into a table in a given database

    :param row_values: The values on the row, which are to be added. 
    :type row_values: list[any]
    :param table_name: The name of the table to which row is added
    :type table_name: str
    :param database: The path to the database or ":memory:" for a temporary database in RAM. If connection \
                     is already established no need to pass a parameter. Defaults to None
    :type database: str, optional
    :param reconnect: Boolean flag allowing establishing a connection to a different database. Defaults to False
    :type reconnect: bool, optional

    :raises ValueError: Raised if the passed values don't match the schema of the table

    :return: Void
    :rtype: None
    """
    cur = get_cursor(database=database, reconnect=reconnect)
    value_str = ", ".join([f"'{value}'" for value in row_values])

    try:
        cur.execute(f"INSERT INTO {check(table_name)} VALUES({check(value_str)});")
    except (sql.OperationalError, sql.IntegrityError) as error:
        _logger.error(f"Failed to insert values {row_values} into table {table_name}: {error}")
        raise ValueError(f"Failed to insert values {row_values} into table {table_name}: {error}")
    
    finalize_execution(cur)


def get_by_key(key: any, table_name: str, column_name: str, database: str = None, reconnect: bool = False) -> list[tuple[any, ...]]:
    """Function for accessing row(s) in a table by some key value for a column.

    :param key: They key by which rows are queried
    :type key: any
    :param table_name: The name of the table from which rows are queried
    :type table_name: str
    :param column_name: The name of the column in which the key is matched
    :type column_name: str
    :param database: The path to the database or ":memory:" for a temporary database in RAM. If connection \
                     is already established no need to pass a parameter. Defaults to None
    :type database: str, optional
    :param reconnect: Boolean flag allowing establishing a connection to a different database. Defaults to False
    :type reconnect: bool, optional

    :return: A list of tuples containing the values of the found rows
    :rtype: list[tuple[any, ...]]
    """
    cur = get_cursor(database=database, reconnect=reconnect)

    try:
        res = cur.execute(f"SELECT * FROM {check(table_name)} WHERE {check(column_name)} = '{check(str(key))}'")
    except sql.OperationalError as error:
        _logger.error(f"Failed to retrieve rows by key {key} for column {column_name} in table {table_name}: {error}")
        raise ValueError(f"Failed to retrieve rows by key {key} for column {column_name} in table {table_name}: {error}")
    
    rows = res.fetchall()
    _logger.info(f"Found {len(rows)} rows with key {key} for column {column_name} in table {table_name}")
    finalize_execution(cur)

    return rows


def delete_by_key(key: any, table_name: str, column_name: str, database: str = None, reconnect: bool = False) -> None:
    """Function for deleting row(s) in a table by some key value for a column.

    :param key: They key by which rows are deleted
    :type key: any
    :param table_name: The name of the table from which rows are deleted
    :type table_name: str
    :param column_name: The name of the column in which the key is matched
    :type column_name: str
    :param database: The path to the database or ":memory:" for a temporary database in RAM. If connection \
                     is already established no need to pass a parameter. Defaults to None
    :type database: str, optional
    :param reconnect: Boolean flag allowing establishing a connection to a different database. Defaults to False
    :type reconnect: bool, optional

    :return: Void
    :rtype: None
    """
    cur = get_cursor(database=database, reconnect=reconnect)

    try:
      res = cur.execute(f"DELETE FROM {check(table_name)} WHERE {check(column_name)} = '{check(str(key))}'")
    except sql.OperationalError as error:
        _logger.error(f"Failed to delete rows by key {key} for column {column_name} in table {table_name}: {error}")
        raise ValueError(f"Failed to delete rows by key {key} for column {column_name} in table {table_name}: {error}")

    _logger.info(f"Deleted {res.rowcount} rows with key {key} for column {column_name} in table {table_name}")

    finalize_execution(cur)


def update_by_key(key: any, value_tuple: tuple[str, any], table_name: str, column_name: str, 
                  database: str = None, reconnect: bool = False) -> None:
    """Function for updating row(s) in given table by some key for a column. If no row has the key
    does nothing.

    :param key: They key by which rows are updated
    :type key: any
    :param value_tuple: Tuple containing the name of the column to be updated and the new value
    :type value_tuple: tuple[str, any]
    :param table_name: The name of the table from which rows are updated
    :type table_name: str
    :param column_name: The name of the column in which the key is matched
    :type column_name: str
    :param database: The path to the database or ":memory:" for a temporary database in RAM. If connection \
                     is already established no need to pass a parameter. Defaults to None
    :type database: str, optional
    :param reconnect: Boolean flag allowing establishing a connection to a different database. Defaults to False
    :type reconnect: bool, optional

    :return: Void
    :rtype: None
    """
    cur = get_cursor(database=database, reconnect=reconnect)

    try:
        cur.execute(f"""UPDATE {check(table_name)} SET {check(value_tuple[0])} = '{check(str(value_tuple[1]))}' 
                        WHERE {check(column_name)} = '{check(str(key))}';""")
    except (sql.OperationalError, sql.IntegrityError) as error:
        _logger.error(f"Failed to update rows by key {key} for column {column_name} in table {table_name}: {error}")
        raise ValueError(f"Failed to update rows by key {key} for column {column_name} in table {table_name}: {error}")
    
    finalize_execution(cur)


# List the functions and variables accessible in other modules
__all__ = ["check", "finalize_execution", "get_connection", "get_cursor", "check_database", "drop_table", "add_table", 
           "initialize_database", "insert_row", "get_by_key", "delete_by_key", "update_by_key"]

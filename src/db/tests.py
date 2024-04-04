"""
Unit tests for most of the functions present in db module. Some functions that are excluded from tests are:

  finalize_execution
  get_cursor

due to their innate simplicity and assumption that the library methods are well tested.

If an unforseen errors occur, it is important to remove all database files that didn't end up getting
cleaned up. Otherwise, they will cause issues when rerunning the tests.

Note that while not best practice the test do depend on each other. Thus, they are labelled in 
alphabetical order (unittest library should execute them in this order). If tests end up failing
this is good to keep in mind.
"""
import unittest
import logging
import sqlite3
import os
import inspect


# Configure the root Logger object. This needs to be done
# before importing modules using logging.
if __name__ == "__main__":
    logging.basicConfig(filename='db_tests.log', level=logging.INFO, force=True,
                        format="%(levelname)s: %(name)s - %(message)s")

from db import *


# Template for the name of the temporary database used by tests. The tests will append 
# the method name at the end
_tmp_database = "__tmp_database_"

# Function for deleting a file if it exists
def _delete_if_exists(path):
    if os.path.exists(path):
        os.remove(path)


class TestDatabaseFunctions(unittest.TestCase):

    def test_a_check_1(self):
        self.assertEqual(check("valid input"), "valid input")

    def test_a_check_2(self):
        with self.assertRaises(ValueError):
            check("input with comments --")

    def test_a_check_3(self):
        with self.assertRaises(ValueError):
            check("very invalid @ input; test")

    def test_a_check_4(self):
        with self.assertRaises(ValueError):
            check("Robert'); DROP TABLE Students;--")

    def test_b_get_connection_1(self):
        con = get_connection(database=":memory:")
        cur = con.cursor()
        self.assertIsInstance(cur, sqlite3.Cursor)
        finalize_execution(cur)

    def test_b_get_connection_2(self):
        con = get_connection()
        cur = con.cursor()
        self.assertIsInstance(cur, sqlite3.Cursor)
        finalize_execution(cur)

    def test_b_get_connection_3(self):
        database = _tmp_database + inspect.stack()[0][3] + ".db"
        with self.assertRaises(ValueError):
            get_connection(database=database)
        _delete_if_exists(database)

    def test_b_get_connection_4(self):
        database = _tmp_database + inspect.stack()[0][3] + ".db"
        with self.assertRaises(FileNotFoundError):
            get_connection(database=database, reconnect=True)
        _delete_if_exists(database)

    def test_b_get_connection_5(self):
        database = _tmp_database + inspect.stack()[0][3] + ".db"
        with self.assertRaises(ValueError):
            get_connection(database=database, generate=True)
        _delete_if_exists(database)

    def test_b_get_connection_6(self):
        database = _tmp_database + inspect.stack()[0][3] + ".db"
        con = get_connection(database=database, reconnect=True, generate=True)
        cur = con.cursor()
        self.assertIsInstance(cur, sqlite3.Cursor)

        finalize_execution(cur)
        _delete_if_exists(database)

    def test_c_check_database_1(self):
        database = _tmp_database + inspect.stack()[0][3] + ".db"
        con = get_connection(database=database, reconnect=True, generate=True)
        cur = con.cursor()

        cur.execute(f"CREATE TABLE IF NOT EXISTS name1 (column1 TEXT);")
        cur.execute(f"CREATE TABLE IF NOT EXISTS name2 (column2 TEXT);")
        cur.execute(f"CREATE TABLE IF NOT EXISTS name3 (column3 TEXT);")

        finalize_execution(cur)

        self.assertTrue(check_database(["name1", "name2", "name3"], database=database, reconnect=True))
        _delete_if_exists(database)

    def test_c_check_database_2(self):
        database = _tmp_database + inspect.stack()[0][3] + ".db"
        con = get_connection(database=database, reconnect=True, generate=True)
        cur = con.cursor()

        cur.execute(f"CREATE TABLE IF NOT EXISTS name1 (column1 TEXT);")
        cur.execute(f"CREATE TABLE IF NOT EXISTS name2 (column2 TEXT);")
        cur.execute(f"CREATE TABLE IF NOT EXISTS name3 (column3 TEXT);")

        finalize_execution(cur)

        self.assertFalse(check_database(["name1", "name2"], database=database, reconnect=True, no_extras=True))
        _delete_if_exists(database)

    def test_c_check_database_3(self):
        database = _tmp_database + inspect.stack()[0][3] + ".db"
        con = get_connection(database=database, reconnect=True, generate=True)
        cur = con.cursor()

        cur.execute(f"CREATE TABLE IF NOT EXISTS name1 (column1 TEXT);")
        cur.execute(f"CREATE TABLE IF NOT EXISTS name2 (column2 TEXT);")

        finalize_execution(cur)

        self.assertTrue(check_database(["name1", "name2"], database=database, reconnect=True, no_extras=True))
        _delete_if_exists(database)

    def test_d_drop_table_1(self):
        database = _tmp_database + inspect.stack()[0][3] + ".db"
        con = get_connection(database=database, reconnect=True, generate=True)
        cur = con.cursor()

        cur.execute(f"CREATE TABLE IF NOT EXISTS name1 (column1 TEXT);")
        cur.execute(f"CREATE TABLE IF NOT EXISTS name2 (column2 TEXT);")
        cur.execute(f"CREATE TABLE IF NOT EXISTS name3 (column3 TEXT);")

        drop_table("name3", database=database, reconnect=True)

        finalize_execution(cur)

        self.assertTrue(check_database(["name1", "name2"], database=database, reconnect=True, no_extras=True))
        _delete_if_exists(database)

    def test_d_drop_table_2(self):
        database = _tmp_database + inspect.stack()[0][3] + ".db"
        con = get_connection(database=database, reconnect=True, generate=True)
        cur = con.cursor()

        cur.execute(f"CREATE TABLE IF NOT EXISTS name1 (column1 TEXT);")
        cur.execute(f"CREATE TABLE IF NOT EXISTS name2 (column2 TEXT);")
        cur.execute(f"CREATE TABLE IF NOT EXISTS name3 (column3 TEXT);")

        with self.assertRaises(ValueError):
            drop_table("name4", database=database, reconnect=True)

        finalize_execution(cur)
        _delete_if_exists(database)

    def test_e_add_table_1(self):
        database = _tmp_database + inspect.stack()[0][3] + ".db"
        get_connection(database=database, reconnect=True, generate=True)

        add_table("name1", [("column1", "TEXT")], database=database, reconnect=True)
        add_table("name2", [("column2", "TEXT")], database=database, reconnect=True)

        self.assertTrue(check_database(["name1", "name2"], database=database, reconnect=True, no_extras=True))
        _delete_if_exists(database)

    def test_e_add_table_2(self):
        database = _tmp_database + inspect.stack()[0][3] + ".db"
        get_connection(database=database, reconnect=True, generate=True)

        add_table("name1", [("column1", "TEXT")], database=database, reconnect=True)
        add_table("name2", [("column2", "TEXT")], database=database, reconnect=True)

        add_table("name1", [("column1", "TEXT")], database=database, reconnect=True)

        self.assertTrue(check_database(["name1", "name2"], database=database, reconnect=True, no_extras=True))
        _delete_if_exists(database)

    def test_e_add_table_3(self):
        database = _tmp_database + inspect.stack()[0][3] + ".db"
        con = get_connection(database=database, reconnect=True, generate=True)
        cur = con.cursor()

        add_table("name1", [("column1", "TEXT")], database=database, reconnect=True)
        add_table("name2", [("column2", "TEXT")], database=database, reconnect=True)

        cur.execute("INSERT INTO name1 VALUES('test')")

        rows = cur.execute("SELECT * FROM name1").fetchall()
        self.assertTrue(len(rows) == 1)

        add_table("name1", [("column1", "TEXT")], database=database, reconnect=True, reset=True)

        rows = cur.execute("SELECT * FROM name1").fetchall()
        self.assertTrue(len(rows) == 0)
        _delete_if_exists(database)

    def test_f_initialize_database_1(self):
        database = _tmp_database + inspect.stack()[0][3] + ".db"
        initialize_database(["name1", "name2"], [[("column1", "TEXT")], [("column2", "TEXT")]],
                            database=database, reconnect=True)
        
        self.assertTrue(check_database(["name1", "name2"], database=database, reconnect=True, no_extras=True))
        _delete_if_exists(database)
    
    def test_f_initialize_database_2(self):
        database = _tmp_database + inspect.stack()[0][3] + ".db"
        initialize_database(["name1", "name2"], [[("column1", "TEXT")], [("column2", "TEXT")]],
                            database=database, reconnect=True)
        
        initialize_database(["name3", "name4"], [[("column3", "TEXT")], [("column4", "TEXT")]],
                            database=database, reconnect=True)
        
        self.assertTrue(check_database(["name1", "name2"], database=database, reconnect=True, no_extras=True))
        _delete_if_exists(database)

    def test_f_initialize_database_3(self):
        database = _tmp_database + inspect.stack()[0][3] + ".db"
        initialize_database(["name1", "name2"], [[("column1", "TEXT")], [("column2", "TEXT")]],
                            database=database, reconnect=True)
        
        initialize_database(["name3", "name4"], [[("column3", "TEXT")], [("column4", "TEXT")]],
                            database=database, reconnect=True, reset=True)
        
        self.assertTrue(check_database(["name3", "name4"], database=database, reconnect=True, no_extras=True))
        _delete_if_exists(database)

    def test_g_insert_row_1(self):
        database = _tmp_database + inspect.stack()[0][3] + ".db"
        con = get_connection(database=database, reconnect=True, generate=True)
        cur = con.cursor()

        add_table("name1", [("column1", "TEXT UNIQUE"), ("column2", "REAL")], database=database, reconnect=True)
        insert_row(["test", 0.0], "name1", database=database, reconnect=True)
        insert_row(["test2", 1.0], "name1", database=database, reconnect=True)

        rows = cur.execute("SELECT * FROM name1").fetchall()
        self.assertTrue(len(rows) == 2)

        _delete_if_exists(database)

    def test_g_insert_row_2(self):
        database = _tmp_database + inspect.stack()[0][3] + ".db"
        
        initialize_database(["name1"], [[("column1", "TEXT UNIQUE"), ("column2", "REAL")]],
                            database=database, reconnect=True)

        with self.assertRaises(ValueError):
            insert_row(["test", 0.0], "name1", database=database, reconnect=True)
            insert_row(["test2"], "name1", database=database, reconnect=True)

        _delete_if_exists(database)

    def test_g_insert_row_3(self):
        database = _tmp_database + inspect.stack()[0][3] + ".db"
        
        initialize_database(["name1"], [[("column1", "TEXT UNIQUE"), ("column2", "REAL")]],
                            database=database, reconnect=True)

        with self.assertRaises(ValueError):
            insert_row(["test", 0.0], "name1", database=database, reconnect=True)
            insert_row(["test", 1.0], "name1", database=database, reconnect=True)

        _delete_if_exists(database)

    def test_h_get_by_value_1(self):
        database = _tmp_database + inspect.stack()[0][3] + ".db"
        
        initialize_database(["name1"], [[("column1", "TEXT UNIQUE"), ("column2", "REAL")]],
                            database=database, reconnect=True)
        
        insert_row(["test1", 0.0], "name1", database=database, reconnect=True)
        insert_row(["test2", 1.0], "name1", database=database, reconnect=True)
        insert_row(["test3", 0.0], "name1", database=database, reconnect=True)

        rows = get_by_value("test1", "name1", "column1", database=database, reconnect=True)

        self.assertTrue(len(rows) == 1)
        _delete_if_exists(database)

    def test_h_get_by_value_2(self):
        database = _tmp_database + inspect.stack()[0][3] + ".db"
        
        initialize_database(["name1"], [[("column1", "TEXT UNIQUE"), ("column2", "REAL")]],
                            database=database, reconnect=True)
        
        insert_row(["test1", 0.0], "name1", database=database, reconnect=True)
        insert_row(["test2", 1.0], "name1", database=database, reconnect=True)
        insert_row(["test3", 0.0], "name1", database=database, reconnect=True)

        rows = get_by_value(0.0, "name1", "column2", database=database, reconnect=True)

        self.assertTrue(len(rows) == 2)
        _delete_if_exists(database)

    def test_h_get_by_value_3(self):
        database = _tmp_database + inspect.stack()[0][3] + ".db"
        
        initialize_database(["name1"], [[("column1", "TEXT UNIQUE"), ("column2", "REAL")]],
                            database=database, reconnect=True)
        
        insert_row(["test1", 0.0], "name1", database=database, reconnect=True)
        insert_row(["test2", 1.0], "name1", database=database, reconnect=True)
        insert_row(["test3", 0.0], "name1", database=database, reconnect=True)

        rows = get_by_value(-1.0, "name1", "column2", database=database, reconnect=True)

        self.assertTrue(len(rows) == 0)
        _delete_if_exists(database)

    def test_h_get_by_value_4(self):
        database = _tmp_database + inspect.stack()[0][3] + ".db"
        
        initialize_database(["name1"], [[("column1", "TEXT UNIQUE"), ("column2", "REAL")]],
                            database=database, reconnect=True)
        
        insert_row(["test1", 0.0], "name1", database=database, reconnect=True)
        insert_row(["test2", 1.0], "name1", database=database, reconnect=True)
        insert_row(["test3", 0.0], "name1", database=database, reconnect=True)

        with self.assertRaises(ValueError):
            get_by_value(-1.0, "name2", "column2", database=database, reconnect=True)

        _delete_if_exists(database)

    def test_h_get_by_value_5(self):
        database = _tmp_database + inspect.stack()[0][3] + ".db"
        
        initialize_database(["name1"], [[("column1", "TEXT UNIQUE"), ("column2", "REAL")]],
                            database=database, reconnect=True)
        
        insert_row(["test1", 0.0], "name1", database=database, reconnect=True)
        insert_row(["test2", 1.0], "name1", database=database, reconnect=True)
        insert_row(["test3", 0.0], "name1", database=database, reconnect=True)

        with self.assertRaises(ValueError):
            get_by_value(0.0, "name1", "column3", database=database, reconnect=True)

        _delete_if_exists(database)

    def test_i_delete_by_value_1(self):
        database = _tmp_database + inspect.stack()[0][3] + ".db"
        
        initialize_database(["name1"], [[("column1", "TEXT UNIQUE"), ("column2", "REAL")]],
                            database=database, reconnect=True)
        
        insert_row(["test1", 0.0], "name1", database=database, reconnect=True)
        insert_row(["test2", 1.0], "name1", database=database, reconnect=True)
        insert_row(["test3", 0.0], "name1", database=database, reconnect=True)

        delete_by_value("test1", "name1", "column1", database=database, reconnect=True)
        rows = get_by_value("test1", "name1", "column1", database=database, reconnect=True)

        self.assertTrue(len(rows) == 0)
        _delete_if_exists(database)

    def test_i_delete_by_value_2(self):
        database = _tmp_database + inspect.stack()[0][3] + ".db"
        
        initialize_database(["name1"], [[("column1", "TEXT UNIQUE"), ("column2", "REAL")]],
                            database=database, reconnect=True)
        
        insert_row(["test1", 0.0], "name1", database=database, reconnect=True)
        insert_row(["test2", 1.0], "name1", database=database, reconnect=True)
        insert_row(["test3", 0.0], "name1", database=database, reconnect=True)

        delete_by_value(0.0, "name1", "column2", database=database, reconnect=True)
        rows = get_by_value(0.0, "name1", "column2", database=database, reconnect=True)

        self.assertTrue(len(rows) == 0)
        _delete_if_exists(database)

    def test_i_delete_by_value_3(self):
        database = _tmp_database + inspect.stack()[0][3] + ".db"
        
        initialize_database(["name1"], [[("column1", "TEXT UNIQUE"), ("column2", "REAL")]],
                            database=database, reconnect=True)
        
        insert_row(["test1", 0.0], "name1", database=database, reconnect=True)
        insert_row(["test2", 1.0], "name1", database=database, reconnect=True)
        insert_row(["test3", 0.0], "name1", database=database, reconnect=True)

        delete_by_value(-1.0, "name1", "column2", database=database, reconnect=True)
        rows = get_by_value(-1.0, "name1", "column2", database=database, reconnect=True)

        self.assertTrue(len(rows) == 0)
        _delete_if_exists(database)

    def test_i_delete_by_value_4(self):
        database = _tmp_database + inspect.stack()[0][3] + ".db"
        
        initialize_database(["name1"], [[("column1", "TEXT UNIQUE"), ("column2", "REAL")]],
                            database=database, reconnect=True)
        
        insert_row(["test1", 0.0], "name1", database=database, reconnect=True)
        insert_row(["test2", 1.0], "name1", database=database, reconnect=True)
        insert_row(["test3", 0.0], "name1", database=database, reconnect=True)

        with self.assertRaises(ValueError):
            delete_by_value(-1.0, "name2", "column2", database=database, reconnect=True)

        _delete_if_exists(database)

    def test_i_delete_by_value_5(self):
        database = _tmp_database + inspect.stack()[0][3] + ".db"
        
        initialize_database(["name1"], [[("column1", "TEXT UNIQUE"), ("column2", "REAL")]],
                            database=database, reconnect=True)
        
        insert_row(["test1", 0.0], "name1", database=database, reconnect=True)
        insert_row(["test2", 1.0], "name1", database=database, reconnect=True)
        insert_row(["test3", 0.0], "name1", database=database, reconnect=True)

        with self.assertRaises(ValueError):
            delete_by_value(0.0, "name1", "column3", database=database, reconnect=True)

        _delete_if_exists(database)

    def test_j_update_by_value_1(self):
        database = _tmp_database + inspect.stack()[0][3] + ".db"
        
        initialize_database(["name1"], [[("column1", "TEXT UNIQUE"), ("column2", "REAL")]],
                            database=database, reconnect=True)
        
        insert_row(["test1", 0.0], "name1", database=database, reconnect=True)
        insert_row(["test2", 1.0], "name1", database=database, reconnect=True)
        insert_row(["test3", 0.0], "name1", database=database, reconnect=True)

        update_by_value("test1", ("column1", "test4"), "name1", "column1", database=database, reconnect=True)
        rows = get_by_value("test4", "name1", "column1", database=database, reconnect=True)

        self.assertTrue(len(rows) == 1)
        _delete_if_exists(database)

    def test_j_update_by_value_2(self):
        database = _tmp_database + inspect.stack()[0][3] + ".db"
        
        initialize_database(["name1"], [[("column1", "TEXT UNIQUE"), ("column2", "REAL")]],
                            database=database, reconnect=True)
        
        insert_row(["test1", 0.0], "name1", database=database, reconnect=True)
        insert_row(["test2", 1.0], "name1", database=database, reconnect=True)
        insert_row(["test3", 0.0], "name1", database=database, reconnect=True)

        update_by_value(1.0, ("column1", "test4"), "name1", "column2", database=database, reconnect=True)
        rows = get_by_value("test4", "name1", "column1", database=database, reconnect=True)

        self.assertTrue(len(rows) == 1)
        _delete_if_exists(database)

    def test_j_update_by_value_3(self):
        database = _tmp_database + inspect.stack()[0][3] + ".db"
        
        initialize_database(["name1"], [[("column1", "TEXT UNIQUE"), ("column2", "REAL")]],
                            database=database, reconnect=True)
        
        insert_row(["test1", 0.0], "name1", database=database, reconnect=True)
        insert_row(["test2", 1.0], "name1", database=database, reconnect=True)
        insert_row(["test3", 0.0], "name1", database=database, reconnect=True)

        update_by_value(-1.0, ("column1", "test4"), "name1", "column2", database=database, reconnect=True)
        rows = get_by_value("test4", "name1", "column1", database=database, reconnect=True)

        self.assertTrue(len(rows) == 0)

        _delete_if_exists(database)

    def test_j_update_by_value_4(self):
        database = _tmp_database + inspect.stack()[0][3] + ".db"
        
        initialize_database(["name1"], [[("column1", "TEXT UNIQUE"), ("column2", "REAL")]],
                            database=database, reconnect=True)
        
        insert_row(["test1", 0.0], "name1", database=database, reconnect=True)
        insert_row(["test2", 1.0], "name1", database=database, reconnect=True)
        insert_row(["test3", 0.0], "name1", database=database, reconnect=True)

        with self.assertRaises(ValueError):
            update_by_value(0.0, ("column1", "test4"), "name1", "column2", database=database, reconnect=True)

        _delete_if_exists(database)

    def test_j_update_by_value_5(self):
        database = _tmp_database + inspect.stack()[0][3] + ".db"
        
        initialize_database(["name1"], [[("column1", "TEXT UNIQUE"), ("column2", "REAL")]],
                            database=database, reconnect=True)
        
        insert_row(["test1", 0.0], "name1", database=database, reconnect=True)
        insert_row(["test2", 1.0], "name1", database=database, reconnect=True)
        insert_row(["test3", 0.0], "name1", database=database, reconnect=True)

        with self.assertRaises(ValueError):
            update_by_value(1.0, ("column1", "test4"), "name2", "column2", database=database, reconnect=True)

        _delete_if_exists(database)


if __name__ == '__main__':
    unittest.main()
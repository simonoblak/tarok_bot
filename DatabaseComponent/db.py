from Configuration import Configuration
from Logs import Logs

config = Configuration().get_config()


class Db:
    status_connected = False
    mydb = None
    cursor = None

    @staticmethod
    def connect_to_db():
        message = "Db.connect_to_db(): "
        if config["write_to_database"] == "yes":
            try:
                import mysql.connector
                Db.mydb = mysql.connector.connect(
                    host=config["host"],
                    user=config["db_user"],
                    passwd=config["db_pass"],
                    database=config["database"]
                )
                Db.cursor = Db.mydb.cursor()
                Db.status_connected = True
                Logs.info_message(message + "Successful connection to database.")
            except ImportError:
                Logs.error_message("Could not import MYSQL connector")
        else:
            Logs.warning_message("Connection to database turned off.")

    @staticmethod
    def execute_sql(sql, values="", multiple=False):
        if config["write_to_database"] == "yes" and Db.status_connected:
            message = "Db.execute_sql(): "
            Logs.debug_message(message + "SQL statement -> " + sql)
            try:
                if values == "" or len(values) == 0:
                    Db.cursor.execute(sql)
                elif multiple:
                    Db.cursor.executemany(sql, values)
                else:
                    Db.cursor.execute(sql, values)
                Db.mydb.commit()
                Logs.info_message(message + "Commit to database successful.")
            except Exception:
                Logs.warning_message(message + "Commit to database NOT successful!")

    @staticmethod
    def get_last_row_id():
        if config["write_to_database"] == "yes" and Db.status_connected:
            return Db.cursor.lastrowid

    @staticmethod
    def close_db():
        if config["write_to_database"] == "yes" and Db.status_connected:
            Db.mydb.close()
            Logs.info_message("Successfully closed connection to database.")
            Db.status_connected = False

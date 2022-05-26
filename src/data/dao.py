import sqlite3
import os
from abc import ABC, abstractmethod
from src import *
from src.data.data_class import *

class DAO(ABC):
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        self.cursor = self.connection.cursor()


class AppDAO:
    __ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    __DB_PATH = os.path.join(__ROOT_DIR, "naar_raan.db")
    __connection: sqlite3.Connection = sqlite3.connect(__DB_PATH)

    @staticmethod
    def get_dao(database: str = None) -> DAO:
        """
        Generate the dao by following the parameter and return it.

        If it not have the operation will return None.
        """
        if database == "user":
            return UserDAO(AppDAO.__connection)
        if database == "drink":
            return DrinkDAO(AppDAO.__connection)
        if database == "bakery":
            return BakeryDAO(AppDAO.__connection)
        if database == "addon":
            return AddonDAO(AppDAO.__connection)
        if database == "logentry":
            return LogEntryDAO(AppDAO.__connection)
        if database == "receipt":
            return ReceiptDAO(AppDAO.__connection)
        return None

    @staticmethod
    def close_database() -> None:
        """
        Disconnect database.
        """
        AppDAO.__connection.close()


class UserDAO(DAO):
    __table_name = "USERS"
    __COLUMN_ID = "id"
    __COLUMN_FIRSTNAME = "first_name"
    __COLUMN_LASTNAME = "last_name"
    __COLUMN_USERNAME = "username"
    __COLUMN_PASSWORD = "password"
    __COLUMN_ACCESSLEVEL = "access_level"

    def __init__(self, connection: sqlite3.Connection):
        super().__init__(connection)
        self.__create_table()

    def __create_table(self) -> None:
        """ create users table if not exists."""
        self.cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {UserDAO.__table_name} (
            {UserDAO.__COLUMN_ID} INTEGER PRIMARY KEY,
            {UserDAO.__COLUMN_FIRSTNAME} TEXT,
            {UserDAO.__COLUMN_LASTNAME} TEXT,
            {UserDAO.__COLUMN_USERNAME} TEXT,
            {UserDAO.__COLUMN_PASSWORD} TEXT,
            {UserDAO.__COLUMN_ACCESSLEVEL} TEXT
            )""")
        self.connection.commit()

    def add_user(self, user: User) -> None:
        """ add user data to users table."""
        access_level = user.get_access_level_str()
        self.cursor.execute(
            f"""INSERT INTO {UserDAO.__table_name}(
            {UserDAO.__COLUMN_FIRSTNAME},
            {UserDAO.__COLUMN_LASTNAME},
            {UserDAO.__COLUMN_USERNAME},
            {UserDAO.__COLUMN_PASSWORD},
            {UserDAO.__COLUMN_ACCESSLEVEL})
            VALUES
            ('{user.get_firstname()}',
            '{user.get_lastname()}',
            '{user.get_username()}',
            '{user.get_password()}',
            '{access_level}')""")
        self.connection.commit()

    def update_user(
        self,
        id: int,
        firstname: str = None,
        lastname: str = None,
        username: str = None,
        password: str = None,
        access: AccessLevel = None
    ) -> None:
        """ update user data where the given id.
            example:    update_user(10, firstname="natcha", access=AdminAccess())
        """

        query = f"UPDATE {UserDAO.__table_name} SET "

        if firstname is not None:
            query += f'{UserDAO.__COLUMN_FIRSTNAME}="{firstname}", '
        if lastname is not None:
            query += f'{UserDAO.__COLUMN_LASTNAME}="{lastname}", '
        if username is not None:
            query += f'{UserDAO.__COLUMN_USERNAME}="{username}", '
        if password is not None:
            query += f'{UserDAO.__COLUMN_PASSWORD}="{password}", '
        if access is not None:
            level = access.get_access_level_str()
            query += f'{UserDAO.__COLUMN_ACCESSLEVEL}="{level}"'

        if query[-2] == ',':
            query = query[:-2]

        query += f" WHERE {UserDAO.__COLUMN_ID}={id}"
        self.cursor.execute(query)
        self.connection.commit()

    def get_all_users(self) -> list[User]:
        self.execute(f"SELECT * FROM {UserDAO.__table_name}")
        query = self.cursor.fetchall()
        # convert data
        convert_data = list()
        for data in query:
            access_level = AdminAccess(
            ) if data[5] == "admin" else StaffAccess()
            user = User(data[0],
                        data[1],
                        data[2],
                        data[3],
                        data[4],
                        access_level)
            convert_data.append(user)
        return convert_data

    def get_user_by_id(self, id: int) -> User:
        self.cursor.execute(
            f"SELECT * FROM {UserDAO.__table_name} WHERE {UserDAO.__COLUMN_ID}={id}")
        data = self.cursor.fetchone()
        if data is None:
            return None
        access_level = AdminAccess() if data[5] == "admin" else StaffAccess()
        return User(data[0],
                    data[1],
                    data[2],
                    data[3],
                    data[4],
                    access_level)

    def get_user_by_username(self, username: str) -> User:
        self.cursor.execute(
            f"SELECT * FROM {UserDAO.__table_name} WHERE {UserDAO.__COLUMN_USERNAME}='{username}'")
        data = self.cursor.fetchone()
        if data is None:
            return None
        access_level = AdminAccess() if data[5] == "admin" else StaffAccess()
        return User(data[0],
                    data[1],
                    data[2],
                    data[3],
                    data[4],
                    access_level)

    def delete_user_by_id(self, id: int) -> None:
        """ delete user data at given id."""
        self.cursor.execute(
            f"DELETE FROM {UserDAO.__table_name} WHERE {UserDAO.__COLUMN_ID}={id}")
        self.connection.commit()


class DrinkDAO(DAO):
    __table_name = "DRINKS"
    __COLUMN_ID = "id"
    __COLUMN_NAME = "name"
    __COLUMN_HP = "hot_price"
    __COLUMN_CP = "cold_price"
    __COLUMN_BP = "blended_price"

    def __init__(self, connection: sqlite3.Connection):
        super().__init__(connection)
        self.__create_table()

    def __create_table(self) -> None:
        self.cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {DrinkDAO.__table_name} (
            {DrinkDAO.__COLUMN_ID} INTEGER PRIMARY KEY,
            {DrinkDAO.__COLUMN_NAME} TEXT,
            {DrinkDAO.__COLUMN_HP} REAL,
            {DrinkDAO.__COLUMN_CP} REAL,
            {DrinkDAO.__COLUMN_BP} REAL)""")
        self.connection.commit()

    def add_drink(self, drink: Drink) -> None:
        self.cursor.execute(
            f"""INSERT INTO {DrinkDAO.__table_name}(
            {DrinkDAO.__COLUMN_NAME},
            {DrinkDAO.__COLUMN_HP},
            {DrinkDAO.__COLUMN_CP},
            {DrinkDAO.__COLUMN_BP})
            VALUES
            ('{drink.get_name()}',
            {drink.get_h_price()},
            {drink.get_c_price()},
            {drink.get_b_price()})""")
        self.connection.commit()

    def get_all_drinks(self) -> list[Drink]:
        self.cursor.execute(f"""SELETE * FROM {DrinkDAO.__table_name}""")
        query = self.cursor.fetchall()
        convert_data = list()
        for data in query:
            drink = Drink(data[0], data[1], data[2], data[3], data[4])
            convert_data.append(drink)
        return convert_data

    def get_drink_by_id(self, id: int) -> Drink:
        self.cursor.execute(
            f"""SELETE * FROM {DrinkDAO.__table_name} WHERE {DrinkDAO.__COLUMN_ID}={id}"""
        )
        data = self.cursor.fetchone()
        return Drink(data[0], data[1], data[2], data[3], data[4])

    def update_drink(self, id: int, name: str = None, hprice: float = None, cprice: float = None, bprice: float = None) -> None:
        query = f"UPDATE {DrinkDAO.__table_name} SET "
        if name is not None:
            query += f'{DrinkDAO.__COLUMN_NAME}="{name}", '
        if hprice is not None:
            query += f'{DrinkDAO.__COLUMN_HP}={hprice}'
        if cprice is not None:
            query += f'{DrinkDAO.__COLUMN_CP}={cprice}'
        if bprice is not None:
            query += f'{DrinkDAO.__COLUMN_BP}={bprice}'

        if query[-2] == ',':
            query = query[:-2]

        query += f" WHERE {DrinkDAO.__COLUMN_ID}={id}"
        self.cursor.execute(query)
        self.connection.commit()

    def delete_drink(self, id: int) -> None:
        self.cursor.execute(
            f"DELETE FROM {DrinkDAO.__table_name} WHERE {DrinkDAO.__COLUMN_ID}={id}")
        self.connection.commit()


class BakeryDAO(DAO):
    __table_name = "BAKERIES"
    __COLUMN_ID = "id"
    __COLUMN_NAME = "name"
    __COLUMN_P = "price"

    def __init__(self, connection: sqlite3.Connection):
        super().__init__(connection)
        self.__create_table()

    def __create_table(self) -> None:
        self.cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {BakeryDAO.__table_name} (
            {BakeryDAO.__COLUMN_ID} INTEGER PRIMARY KEY,
            {BakeryDAO.__COLUMN_NAME} TEXT,
            {BakeryDAO.__COLUMN_P} REAL)""")
        self.connection.commit()

    def add_bakery(self, bakery: Bakery) -> None:
        self.cursor.execute(f"""INSERT INTO {BakeryDAO.__table_name} (
            {BakeryDAO.__COLUMN_NAME},
            {BakeryDAO.__COLUMN_P})
            VALUES
            ('{bakery.get_name()}',
            {bakery.get_price()})""")
        self.connection.commit()

    def get_all_bakeries(self) -> list[Bakery]:
        self.cursor.execute(f"""SELETE * FROM {BakeryDAO.__table_name}""")
        query = self.cursor.fetchall()
        convert_data = list()
        for data in query:
            bakery = Bakery(data[0], data[1], data[2])
            convert_data.append(bakery)
        return convert_data

    def get_bakery_by_id(self, id: int) -> Bakery:
        self.cursor.execute(
            f"SELETE * FROM {BakeryDAO.__table_name} WHERE {BakeryDAO.__COLUMN_ID}={id}")
        data = self.cursor.fetchone()
        return Bakery(data[0], data[1], data[2])

    def update_bakery(self, id: int, name: str = None, price: float = None) -> None:
        query = f"UPDATE {BakeryDAO.__table_name} SET "
        if name is not None:
            query += f'{BakeryDAO.__COLUMN_NAME}="{name}", '
        if price is not None:
            query += f'{BakeryDAO.__COLUMN_P}={price}'

        if query[-2] == ',':
            query = query[:-2]
        query += f'WHERE {BakeryDAO.__COLUMN_ID}={id}'
        self.cursor.execute(query)
        self.connection.commit()

    def delete_bakery(self, id: int) -> None:
        self.cursor.execute(
            f"DELETE FROM {BakeryDAO.__table_name} WHERE {BakeryDAO.__COLUMN_ID}={id}")
        self.connection.commit()


class AddonDAO(DAO):
    __table_name = "ADDONS"
    __COLUMN_ID = "id"
    __COLUMN_NAME = "name"
    __COLUMN_P = "price"

    def __init__(self, connection: sqlite3.Connection):
        super().__init__(connection)
        self.__create_table()

    def __create_table(self) -> None:
        self.cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {AddonDAO.__table_name} (
            {AddonDAO.__COLUMN_ID} INTEGER PRIMARY KEY,
            {AddonDAO.__COLUMN_NAME} TEXT,
            {AddonDAO.__COLUMN_P} REAL)""")
        self.connection.commit()

    def add_addon(self, addon: Addon) -> None:
        self.cursor.execute(f"""INSERT INTO {AddonDAO.__table_name} (
            {AddonDAO.__COLUMN_NAME},
            {AddonDAO.__COLUMN_P})
            VALUES
            ('{addon.get_name()}',
            {addon.get_price()})""")
        self.connection.commit()

    def get_all_addons(self) -> list[Addon]:
        self.cursor.execute(f"""SELETE * FROM {AddonDAO.__table_name}""")
        query = self.cursor.fetchall()
        convert_data = list()
        for data in query:
            addon = Addon(data[0], data[1], data[2])
            convert_data.append(bakery)
        return convert_data

    def get_addon_by_id(self, id: int) -> Bakery:
        self.cursor.execute(
            f"SELETE * FROM {AddonDAO.__table_name} WHERE {AddonDAO.__COLUMN_ID}={id}")
        data = self.cursor.fetchone()
        return Addon(data[0], data[1], data[2])

    def update_bakery(self, id: int, name: str = None, price: float = None) -> None:
        query = f"UPDATE {AddonDAO.__table_name} SET "
        if name is not None:
            query += f'{AddonDAO.__COLUMN_NAME}="{name}", '
        if price is not None:
            query += f'{AddonDAO.__COLUMN_P}={price}'

        if query[-2] == ',':
            query = query[:-2]
        query += f'WHERE {AddonDAO.__COLUMN_ID}={id}'
        self.cursor.execute(query)
        self.connection.commit()

    def delete_bakery(self, id: int) -> None:
        self.cursor.execute(
            f"DELETE FROM {AddonDAO.__table_name} WHERE {AddonDAO.__COLUMN_ID}={id}")
        self.connection.commit()


class LogEntryDAO(DAO):
    __table_name = "LOGENTRIES"
    __COLUMN_DATE = "date"
    __COLUMN_TIME = "time"
    __COLUMN_OWNER = "owner_id"
    __COLUMN_DESCR = "description"

    def __init__(self, connection: sqlite3.Connection):
        super().__init__(connection)
        self.__create_table()

    def __create_table(self):
        self.cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {LogEntryDAO.__table_name}(
            {LogEntryDAO.__COLUMN_DATE} TEXT NOT NULL,
            {LogEntryDAO.__COLUMN_TIME} TEXT NOT NULL,
            {LogEntryDAO.__COLUMN_OWNER} INTEGER,
            {LogEntryDAO.__COLUMN_DESCR} TEXT,
            PRIMARY KEY ({LogEntryDAO.__COLUMN_DATE},{LogEntryDAO.__COLUMN_TIME}))"""
        )

    def add_logentry(self, logentry: LogEntry) -> None:
        pass

    def get_all_logentries(self, date: str = None, time: str = None) -> list[LogEntry]:
        return


class ReceiptDAO(DAO):
    __table_name = "RECEIPTS"
    __COLUMN_DATE = "date"
    __COLUMN_TIME = "time"
    __COLUMN_NO = "number"
    __COLUMN_DESCR = "description"

    def __init__(self, connection: sqlite3.Connection):
        super().__init__(connection)
        self.__create_table()

    def __create_table(self) -> None:
        self.cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {ReceiptDAO.__table_name}(
            {ReceiptDAO.__COLUMN_DATE} TEXT NOT NULL,
            {ReceiptDAO.__COLUMN_TIME} TEXT NOT NULL,
            {ReceiptDAO.__COLUMN_NO} INTEGER NOT NULL,
            {ReceiptDAO.__COLUMN_DESCR} TEXT,
            PRIMARY KEY ({ReceiptDAO.__COLUMN_DATE},{ReceiptDAO.__COLUMN_TIME},{ReceiptDAO.__COLUMN_NO}))"""
        )
        self.connection.commit()

    def add_receipt(self, receipt: Receipt) -> None:
        pass


class RevenueDAO(DAO):
    __table_name = "TARGETREVENUES"
    __COLUMN_YEAR = "year"
    __COLUMN_MONTH = "month"
    __COLUMN_TARGET = "target"

    def __init__(self, connection: sqlite3.Connection):
        super().__init__(connection)
        self.__create_table()

    def __create_table(self) -> None:
        self.cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {RevenueDAO.__table_name}(
            {RevenueDAO.__COLUMN_YEAR} TEXT NOT NULL,
            {RevenueDAO.__COLUMN_MONTH} TEXT NOT NULL,
            {RevenueDAO.__COLUMN_TARGET} INTEGET,
            PRIMARY KEY ({RevenueDAO.__COLUMN_YEAR},{RevenueDAO.__COLUMN_MONTH})
            )"""
        )
        self.connection.commit()

    def add_target_revenue(self, target_revenue: TargetRevenue) -> None:
        self.cursor.execute(
            f"""INSERT INTO {RevenueDAO.__table_name}(
            {RevenueDAO.__COLUMN_YEAR},
            {RevenueDAO.__COLUMN_MONTH},
            {RevenueDAO.__COLUMN_TARGET})
            VALUES(
            "{target_revenue.get_year()}",
            "{target_revenue.get_month()}",
            {target_revenue.get_target_revenue()}
            )""")
        self.connection.commit()

    def update_target_revenue(self, year: str, month: str, target: int) -> None:
        pass

    def get_all_target_revenues(self) -> list[TargetRevenue]:
        pass

    def get_target_revenue(self, year, month) -> TargetRevenue:
        pass

    def delete_target_revenue(self) -> None:
        pass
"""
User defined settings that should be persisted
"""

from inventory.config import SETTINGS_PATH
from contextlib import closing
import sqlite3
import uuid

"""
# INVENTORY SPECIFIC SETTINGS

setting_id |   shop_id    |      name        | value |
-----------|--------------|------------------|-------|
 1         |  #SHOP-001   | LOW LEVEL        | 0     |
 2         |  #SHOP-001   | CONTROL STRATEGY | fifo  |
"""


class SQLSettingPersistor:

    def __init__(self, setting_db=SETTINGS_PATH):
        self.db = setting_db

    @property
    def connection(self):
        return self.connection()

    def cursor(self):
        conn = self.connection
        yield closing(conn.cursor())
        conn.close()

    def get(self, name: str, shop_id: uuid.UUID):
        setting_name = name.upper()
        with closing(self.connection.cursor()) as cursor:
            setting_id, inventory_value = cursor.execute(
                """
                SELECT value
                FROM inventory_setting
                WHERE name = %s
                AND shop_id = %s
                """,
                (setting_name, shop_id),
            ).fetchone()

        if not inventory_value:
            raise ValueError(
                f"Setting Value Not Found: {setting_name}. Did you save this in upper case?"
            )
        return inventory_value


def get_control_strategy(shop_id: uuid.UUID, setting_persistor=SQLSettingPersistor()):
    return setting_persistor.get("control strategy")


def get_low_level(shop_id: uuid.UUID, setting_persistor=SQLSettingPersistor()):
    return setting_persistor.get("low level")

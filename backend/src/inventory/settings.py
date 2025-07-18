"""
User defined settings that should be persisted
"""

from inventory.config import DATABASE_URL, DEFAULT_SETTINGS
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

    def __init__(self, setting_db=DATABASE_URL):
        self.db = setting_db

    @property
    def connection(self):
        return sqlite3.connect(self.db)

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

    def update(self, shop_id, name, value):
        name = name.upper()
        conn = self.connection
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                """
                INSERT INTO inventory_setting (value, name, shop_id)
                VALUES (:1, :2, :3)
                ON CONFLICT
                DO
                UPDATE SET value = :1
                WHERE name = :2
                AND shop_id = :3
            """,
                (value, name, shop_id),
            )
            conn.commit()


def get_control_strategy(shop_id: uuid.UUID, setting_persistor=SQLSettingPersistor()):
    return "fifo"
    return setting_persistor.get("control strategy", shop_id)


def get_low_level(shop_id: uuid.UUID, setting_persistor=SQLSettingPersistor()):
    return setting_persistor.get("low level")


def apply_default_settings(shop_id, setting_persistor=SQLSettingPersistor()):
    for name, value in DEFAULT_SETTINGS:
        setting_persistor.update(shop_id, name, value)

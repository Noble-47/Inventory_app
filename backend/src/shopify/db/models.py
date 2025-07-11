from functools import partial
from datetime import datetime
import uuid

from sqlmodel import SQLModel, Field
from pydantic import ConfigDict

from shopify.config import INVITE_TOKEN_EXPIRATION_SECONDS, TIMEZONE

datetime_now_utc = datetime.now(TIMEZONE)


class Token(SQLModel, table=True):
    model_config = ConfigDict(extra="allow")

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True)
    permissions: str
    token_str: str = Field(unique=True)
    business_id: uuid.UUID
    shop_id: uuid.UUID
    shop_location: str
    is_valid: bool = True
    used: bool = False
    expired: bool = False
    TTL: float = Field(default=INVITE_TOKEN_EXPIRATION_SECONDS)
    created: float = Field(default_factory=datetime_now_utc.timestamp)
    sent: bool = Field(default=False)

    def check_validity(self):
        if isinstance(self.created, float):
            time_lived = abs(self.created - datetime.now(TIMEZONE).timestamp())
        else:  # isinstance datetime
            time_lived = (self.created - datetime.now(TIMEZONE)).seconds()
        if time_lived >= self.TTL:
            self.expired = True
            self.is_valid = False
            return True
        return False


class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_log"

    id: int | None = Field(default=None, primary_key=True)
    business_id: uuid.UUID
    name: str = Field(index=True)
    description: str
    time: float
    event_hash: str = Field(unique=True)
    payload: str


"""
### Every service should control their settings

# GLOBAL Business SETTINGS

# Setting Map
id|      name        |    tag    |
--|------------------|-----------|
1 | LOW LEVEL        | inventory |
2 | CONTROL STRATEGY | inventory |


# BUSINESS WIDE SETTINGS
id| setting_id | value |
--|------------|-------|
1 |     1      | 0     |
2 |     2      | fifo  |

# SHOP SPECIFIC SETTINGS

setting_id |   shop_id    | value |
-----------|--------------|-------|
 1         | ac35         |  10   |
 2         | bc32a        | fifo  |
"""


class Setting(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    tag: str
    description: str


class EntitySetting(SQLModel, table=True):
    __tablename__ = "entity_setting"

    id: int | None = Field(default=None, primary_key=True)
    setting_id: int = Field(foreign_key="setting.id")
    entity_id: uuid.UUID
    entity_type: str
    value: str


class AccountVerification(SQLModel, table=True):
    __tablename__ = "account_verification"

    id: int | None = Field(default=None, primary_key=True)
    email: str
    verification_str: str = Field(unique=True, index=True)
    is_valid: bool = True
    model_config = ConfigDict(extra="allow")

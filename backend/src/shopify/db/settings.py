import uuid

from sqlmodel import Session, select

from shopify.db.models import Setting, EntitySetting
from shopify.db import events


class Setting:

    def __init__(self, session: Session, events=None):
        self.session = session

    def get_id(name: str):
        return self.session.exec(select(Setting.id).where(Setting.name == name)).one()

    def get_tag(name: str | None = None, id: int | None = None):
        if name:
            return self.session.exec(
                select(Setting.tag).where(Setting.name == name)
            ).one()
        if id:
            return self.session.exec(select(Setting.tag).where(Setting.id == id)).one()

    def set(self, name: str, value: str | int, entity_id: uuid.UUID):
        setting_id = self.get_setting_id(name)
        entity = self.session.exec(
            select(EntitySetting).where(EntitySetting.shop_id == entity_id)
        ).first()
        if entity:
            entity.value = str(value)
        else:
            # create new entry
            entity = EntitySetting(setting_id, entity_id, str(value))
        self.events.append(
            events.SettingUpdated(
                tag=get_tag(setting_id),
                entity_id=entity_id,
                entity_type=entity.type,
                value=value,
            )
        )
        self.session.add(entity)

    def get(self, name: str, entity_id: uuid.UUID):
        setting_id, tag = self.get_setting_id(name)
        setting = self.session.exec(
            select(EntitySetting).where(EntitySetting.setting_id == setting_id)
        ).first()
        if setting is None:
            return None
        if setting.value.isnumeric():
            return int(setting.value)
        return setting.value

    def fetch(self, entity_id):
        settings = self.session.exec(
            select(EntitySetting, Setting.name, Setting.tag)
            .join(Setting)
            .where(EntitySetting.setting_id == setting_id)
        ).all()
        return settings

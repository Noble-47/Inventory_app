from datetime import datetime

from pydantic import BaseModel, Field

from shared import datetime_now_func


class InfoMismatch(BaseModel):
    shop_id: str
    phone: str
    recorded_firstname: str
    recorded_lastname: str
    input_firstname: str
    input_lastname: str
    event_time: datetime = Field(default_factory=datetime_now_func)

    def json(self):
        data = self.model_dump()
        data["event_time"] = data["event_time"].timestamp()
        return data


class AttentionNeeded(BaseModel):
    shop_id: str
    sale_ref: str
    message: str

    def json(self):
        data = self.model_dump()
        data["event_time"] = data["event_time"].timestamp()
        return data

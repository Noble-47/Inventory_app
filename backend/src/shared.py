from functools import partial
from datetime import datetime
import pytz
import json

TIMEZONE = pytz.timezone("Africa/Lagos")

datetime_now_func = partial(datetime.now, tz=pytz.timezone("Africa/Lagos"))


def load_payload(payload):
    payload = json.loads(payload)
    if "time" in payload:
        payload["time"] = datetime.fromtimestamp(payload["time"])
    return payload

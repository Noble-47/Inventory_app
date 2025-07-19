from functools import partial
from datetime import datetime
import pytz

TIMEZONE = pytz.timezone("Africa/Lagos")

datetime_now_func = partial(datetime.now, tz=pytz.timezone("Africa/Lagos"))

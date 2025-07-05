from functools import partial
from datetime import datetime
import pytz

datetime_now_func = partial(datetime.now, tz=pytz.timezone("Africa/Lagos"))

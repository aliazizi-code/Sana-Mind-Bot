from datetime import datetime, timezone
import pytz


IRAN_TZ = pytz.timezone('Asia/Tehran')
def get_iran_time():
    return datetime.now(IRAN_TZ)

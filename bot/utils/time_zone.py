from datetime import datetime
import pytz


def get_iran_time(timezone='Asia/Tehran'):
    IRAN_TZ = pytz.timezone(timezone)
    return datetime.now(IRAN_TZ)
    

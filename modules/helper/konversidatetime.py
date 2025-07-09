import time
from datetime import datetime, timedelta


def format_ts(ts):
    try:
        ts = int(ts)
        return datetime.fromtimestamp(ts).strftime("%d-%m-%Y %H:%M")
    except:
        return "-"

def get_range_timestamp(qdate_start=None, qdate_end=None):
    # Default tanggal: 1 Jan 2000 sampai 31 Des 2099
    default_start = datetime(2000, 1, 1)
    default_end   = datetime(2100, 1, 1)  # eksklusif

    dt_start = datetime.combine(qdate_start.toPyDate(), datetime.min.time()) if qdate_start else default_start
    dt_end   = datetime.combine(qdate_end.toPyDate(), datetime.min.time()) + timedelta(days=1) if qdate_end else default_end

    ts_start = int(time.mktime(dt_start.timetuple()))
    ts_end   = int(time.mktime(dt_end.timetuple()))
    return ts_start, ts_end

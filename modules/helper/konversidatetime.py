from datetime import datetime


def format_ts(ts):
    try:
        ts = int(ts)
        return datetime.fromtimestamp(ts).strftime("%d-%m-%Y %H:%M")
    except:
        return "-"
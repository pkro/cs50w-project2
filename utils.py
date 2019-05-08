import time
from datetime import datetime

def cachebuster():
    return time.time() if debug else "static"

def get_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')